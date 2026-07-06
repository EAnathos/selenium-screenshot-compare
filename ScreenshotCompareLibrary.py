#!/usr/bin/env python3
"""Librairie Robot Framework : expose le package `screenshot_compare` sous forme
de keywords.

Les noms de methodes deviennent automatiquement des keywords :
    capture_page           -> "Capture Page"
    compare_screenshots    -> "Compare Screenshots"
    crawl_site             -> "Crawl Site"
    compare_page_across_versions -> "Compare Page Across Versions"
    write_page_result      -> "Write Page Result"
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from robot.api import logger
from robot.api.deco import keyword, library

import os
import sys

# Rend le package `src` importable meme si RF n'ajoute pas la racine au path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src import (  # noqa: E402
    DualSession,
    capture_screenshot,
    compare_images,
    crawl_site,
    slugify,
)


@library(scope="GLOBAL", version="1.0")
class ScreenshotCompareLibrary:
    """Comparaison de rendu d'un site entre deux binaires Firefox."""

    def __init__(self):
        self._session: DualSession | None = None
        self._wait: float = 2.0

    # -- keywords bas niveau (1 fonction Python = 1 keyword) -----------------

    @keyword("Crawl Site")
    def crawl_site(self, start_url: str, max_pages: int = 20,
                   max_depth: int = 3, timeout: float = 15.0) -> list[str]:
        """Decouvre les pages same-domain a partir de `start_url` (BFS)."""
        urls = crawl_site(start_url, max_pages, max_depth, timeout)
        logger.info(f"{len(urls)} page(s) decouverte(s).")
        return urls

    @keyword("Capture Page")
    def capture_page(self, url: str, firefox_binary: str, output_path: str,
                     width: int = 1280, height: int = 900,
                     wait: float = 2.0) -> str:
        """Capture `url` en pleine page avec le binaire Firefox donne.
        Renvoie la version reelle du navigateur."""
        version = capture_screenshot(url, firefox_binary, Path(output_path),
                                     width, height, wait)
        logger.info(f"Firefox {version} -> {output_path}")
        return version

    @keyword("Compare Screenshots")
    def compare_screenshots(self, image_a: str, image_b: str, diff_output: str,
                            threshold: int = 20) -> dict:
        """Compare deux images, ecrit le diff, renvoie un dict
        {percent, first_diff_y, width, height}."""
        r = compare_images(Path(image_a), Path(image_b), Path(diff_output),
                           threshold)
        logger.info(f"Difference : {r.percent:.4f} % "
                    f"(1re divergence: {r.first_diff_y})")
        return {"percent": r.percent, "first_diff_y": r.first_diff_y,
                "width": r.width, "height": r.height}

    @keyword("Write Page Result")
    def write_page_result(self, result_path: str, data: dict) -> str:
        """Ecrit le fichier resultat (JSON) d'une page et renvoie son chemin."""
        path = Path(result_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                        encoding="utf-8")
        return str(path)

    # -- keyword haut niveau : tout enchainer pour UNE page ------------------

    @keyword("Compare Page Across Versions")
    def compare_page_across_versions(self, url: str, firefox_a: str,
                                     firefox_b: str, output_dir: str,
                                     width: int = 1280, height: int = 900,
                                     wait: float = 2.0,
                                     threshold: int = 20) -> float:
        """Capture `url` avec les deux Firefox, compare, ecrit un fichier
        result.json dans output_dir/<slug>/ et renvoie le % de difference."""
        page_dir = Path(output_dir) / slugify(url)
        page_dir.mkdir(parents=True, exist_ok=True)
        shot_a = page_dir / "version_a.png"
        shot_b = page_dir / "version_b.png"
        diff_img = page_dir / "diff.png"

        ver_a = capture_screenshot(url, firefox_a, shot_a, width, height, wait)
        ver_b = capture_screenshot(url, firefox_b, shot_b, width, height, wait)
        r = compare_images(shot_a, shot_b, diff_img, threshold)

        data = {
            "url": url,
            "firefox_a": ver_a,
            "firefox_b": ver_b,
            "difference_percent": round(r.percent, 4),
            "first_diff_y": r.first_diff_y,
            "image_width": r.width,
            "image_height": r.height,
            "threshold": threshold,
            "screenshots": {
                "version_a": shot_a.name,
                "version_b": shot_b.name,
                "diff": diff_img.name,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        self.write_page_result(str(page_dir / "result.json"), data)
        logger.info(f"{url} -> {r.percent:.4f} % "
                    f"(result.json dans {page_dir})")
        return r.percent

    # -- keywords interactifs : piloter les 2 versions en lockstep ----------
    # Style Selenium : on ouvre une session double, on clique / saisit, puis on
    # compare l'etat courant. Ideal pour un scenario de navigation par clics.

    @keyword("Open Versions")
    def open_versions(self, url: str, firefox_a: str, firefox_b: str,
                      width: int = 1280, height: int = 900,
                      wait: float = 2.0) -> None:
        """Ouvre `url` dans les deux versions de Firefox (session double)."""
        self._session = DualSession(firefox_a, firefox_b, width, height)
        self._wait = wait
        self._session.open(url)
        logger.info(f"Sessions ouvertes : Firefox {self._session.version_a} "
                    f"& {self._session.version_b} sur {url}")

    @keyword("Go To")
    def go_to(self, url: str) -> None:
        """Navigue vers `url` dans les deux versions."""
        self._require_session().open(url)

    @keyword("Click Element")
    def click_element(self, locator: str) -> None:
        """Clique l'element (ex: css=a.btn, id=submit, xpath=//a) dans les deux."""
        self._require_session().click(locator)

    @keyword("Input Text")
    def input_text(self, locator: str, text: str) -> None:
        """Saisit `text` dans le champ `locator` dans les deux versions."""
        self._require_session().input_text(locator, text)

    @keyword("Go Back")
    def go_back(self) -> None:
        """Revient a la page precedente dans les deux versions."""
        self._require_session().go_back()

    @keyword("Capture And Compare")
    def capture_and_compare(self, name: str, output_dir: str,
                            wait: float | None = None,
                            threshold: int = 20) -> float:
        """Capture l'etat courant des deux versions, compare, ecrit un
        result.json dans output_dir/<name>/ et renvoie le % de difference."""
        session = self._require_session()
        wait = self._wait if wait is None else float(wait)
        page_dir = Path(output_dir) / slugify(name)
        page_dir.mkdir(parents=True, exist_ok=True)
        shot_a = page_dir / "version_a.png"
        shot_b = page_dir / "version_b.png"
        diff_img = page_dir / "diff.png"

        url = session.driver_a.current_url
        ver_a, ver_b = session.capture_both(shot_a, shot_b, wait)
        r = compare_images(shot_a, shot_b, diff_img, threshold)

        data = {
            "step": name,
            "url": url,
            "firefox_a": ver_a,
            "firefox_b": ver_b,
            "difference_percent": round(r.percent, 4),
            "first_diff_y": r.first_diff_y,
            "image_width": r.width,
            "image_height": r.height,
            "threshold": threshold,
            "screenshots": {
                "version_a": shot_a.name,
                "version_b": shot_b.name,
                "diff": diff_img.name,
            },
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        self.write_page_result(str(page_dir / "result.json"), data)
        logger.info(f"[{name}] {url} -> {r.percent:.4f} %")
        return r.percent

    @keyword("Close Versions")
    def close_versions(self) -> None:
        """Ferme les deux navigateurs de la session double."""
        if self._session is not None:
            self._session.close()
            self._session = None

    def _require_session(self) -> DualSession:
        if self._session is None:
            raise RuntimeError("Aucune session ouverte : appelle d'abord "
                               "'Open Versions'.")
        return self._session
