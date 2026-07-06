#!/usr/bin/env python3
"""CLI page unique : compare une URL entre deux binaires Firefox.

Pour comparer TOUT un site (crawl) et obtenir un fichier par page, utilise
plutot la suite Robot Framework : tests/firefox_versions.robot (voir README).

Exemple :
    python compare.py https://example.com \
        --firefox-a /usr/bin/firefox \
        --firefox-b "$(pwd)/firefoxes/firefox-128esr/firefox"
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import capture_screenshot, compare_images  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url", help="URL a comparer")
    parser.add_argument("--firefox-a", default="", help="chemin du 1er binaire Firefox")
    parser.add_argument("--firefox-b", default="", help="chemin du 2e binaire Firefox")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--wait", type=float, default=2.0,
                        help="secondes d'attente apres chargement (rendu/animations)")
    parser.add_argument("--threshold", type=int, default=20,
                        help="ecart couleur (0-255) sous lequel un pixel est identique")
    parser.add_argument("--out", default="output/single", help="dossier de sortie")
    args = parser.parse_args()

    out_dir = Path(args.out)
    shot_a = out_dir / "version_a.png"
    shot_b = out_dir / "version_b.png"
    diff_img = out_dir / "diff.png"

    print(f"[A] Capture avec {args.firefox_a or '(Firefox par defaut)'} ...")
    ver_a = capture_screenshot(args.url, args.firefox_a, shot_a,
                               args.width, args.height, args.wait)
    print(f"[A] Firefox {ver_a} -> {shot_a}")

    print(f"[B] Capture avec {args.firefox_b or '(Firefox par defaut)'} ...")
    ver_b = capture_screenshot(args.url, args.firefox_b, shot_b,
                               args.width, args.height, args.wait)
    print(f"[B] Firefox {ver_b} -> {shot_b}")

    r = compare_images(shot_a, shot_b, diff_img, args.threshold)
    print("-" * 50)
    print(f"Version A : Firefox {ver_a}")
    print(f"Version B : Firefox {ver_b}")
    print(f"Difference : {r.percent:.4f} % de pixels differents")
    if r.first_diff_y is not None:
        print(f"Premiere divergence substantielle a y={r.first_diff_y}px "
              f"(souvent le point de decalage du layout)")
    else:
        print("Aucune divergence substantielle (seules de fines differences "
              "d'anti-aliasing eventuelles)")
    print(f"Image de diff : {diff_img}")

    if ver_a == ver_b:
        print("\n(!) Les deux captures utilisent la MEME version de Firefox : "
              "renseigne --firefox-b avec un autre binaire pour une vraie comparaison.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
