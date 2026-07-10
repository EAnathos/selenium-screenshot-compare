#!/usr/bin/env python3
"""Comparaison pixel de deux captures d'ecran."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops


@dataclass
class DiffResult:
    """Resultat d'une comparaison entre deux captures."""

    percent: float  # pourcentage de pixels differents
    first_diff_y: int | None  # 1re ligne de divergence substantielle (px)
    width: int
    height: int


def compare_images(img_a: Path, img_b: Path, diff_out: Path, threshold: int = 20) -> DiffResult:
    """Compare deux captures, ecrit une image surlignant les differences et
    renvoie un DiffResult.

    `threshold` : ecart de couleur (0-255) en dessous duquel un pixel est
    considere identique, pour absorber le bruit d'anti-aliasing.
    """
    a = Image.open(img_a).convert("RGB")
    b = Image.open(img_b).convert("RGB")

    # Les deux versions peuvent produire des pages de hauteur legerement
    # differente : on aligne sur la plus grande en remplissant de blanc.
    w = max(a.width, b.width)
    h = max(a.height, b.height)
    canvas_a = Image.new("RGB", (w, h), "white")
    canvas_b = Image.new("RGB", (w, h), "white")
    canvas_a.paste(a, (0, 0))
    canvas_b.paste(b, (0, 0))

    diff = ImageChops.difference(canvas_a, canvas_b)

    # Analyse vectorisee (numpy) : rapide meme sur une capture pleine page de
    # plusieurs megapixels. Un pixel "differe" si l'ecart depasse `threshold`
    # sur au moins un canal, pour ignorer le bruit d'anti-aliasing.
    arr = np.asarray(diff, dtype=np.int16)  # (h, w, 3)
    per_pixel = arr.max(axis=2)  # ecart max sur RGB, par pixel
    differing = per_pixel > threshold  # (h, w) booleen
    changed = int(differing.sum())
    total = w * h
    pct = 100.0 * changed / total if total else 0.0

    # Premiere ligne ou une part SUBSTANTIELLE des pixels differe : bien plus
    # parlant que le premier pixel isole (souvent juste de l'anti-aliasing).
    # Repere ainsi le vrai point de decalage vertical du layout.
    row_frac = differing.mean(axis=1)  # fraction diff. par ligne
    substantial = np.where(row_frac > 0.10)[0]  # >10 % de la ligne
    first_diff_y = int(substantial[0]) if substantial.size else None

    # Image de diff amplifiee (differences en clair sur fond noir).
    Path(diff_out).parent.mkdir(parents=True, exist_ok=True)
    diff.point(lambda p: min(255, p * 8)).save(diff_out)

    return DiffResult(percent=pct, first_diff_y=first_diff_y, width=w, height=h)
