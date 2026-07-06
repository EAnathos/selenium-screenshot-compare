#!/usr/bin/env python3
"""Librairie Robot Framework : pilote DEUX versions de Firefox en parallele et
compare leur rendu apres chaque interaction (clic, saisie, navigation). Gere
aussi la capture / restauration d'un storage state (cookies + localStorage).

Keywords exposes :
    Open Versions, Go To, Click Element, Input Text, Go Back,
    Capture And Compare, Load Storage State, Close Versions,
    Open Auth Browser, Save Storage State, Close Auth Browser.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from robot.api import logger
from robot.api.deco import keyword, library

import os
import sys

# Dossier de CETTE librairie (resources/keywords) sur le path, pour importer le
# sous-package utils/.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (  # noqa: E402
    DualSession,
    compare_images,
    make_firefox,
    save_storage_state,
    slugify,
)


@library(scope="GLOBAL", version="1.0")
class ScreenshotCompareLibrary:
    """Comparaison de rendu d'un site entre deux binaires Firefox."""

    def __init__(self):
        self._session: DualSession | None = None
        self._wait: float = 2.0
        self._auth_driver = None

    def _write_result(self, result_path: Path, data: dict) -> None:
        """Ecrit le fichier resultat (JSON) d'une etape."""
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(json.dumps(data, indent=2, ensure_ascii=False),
                               encoding="utf-8")

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
        self._write_result(page_dir / "result.json", data)
        logger.info(f"[{name}] {url} -> {r.percent:.4f} %")
        return r.percent

    @keyword("Load Storage State")
    def load_storage_state(self, path: str) -> bool:
        """Injecte cookies + localStorage depuis `path` dans les deux versions
        (session authentifiee), puis recharge. A appeler apres 'Open Versions',
        une fois sur le domaine. Ignore avec un avertissement si le fichier est
        absent (session anonyme)."""
        applied = self._require_session().load_storage(Path(path))
        if applied:
            logger.info(f"Storage state charge depuis {path}")
        else:
            logger.warn(f"Storage state introuvable ({path}) : session anonyme. "
                        "Lance d'abord tests/capture_auth.robot.")
        return applied

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

    # -- capture d'un storage state (un seul navigateur) --------------------

    @keyword("Open Auth Browser")
    def open_auth_browser(self, url: str, firefox_binary: str,
                          headless: bool = False, width: int = 1280,
                          height: int = 900) -> None:
        """Ouvre UN Firefox sur `url` (visible par defaut, pour se connecter a
        la main avant de capturer le storage state)."""
        self._auth_driver = make_firefox(firefox_binary, width, height, headless)
        self._auth_driver.get(url)
        logger.info(f"Navigateur d'auth ouvert sur {url} (headless={headless})")

    @keyword("Save Storage State")
    def save_storage_state(self, path: str) -> None:
        """Enregistre le storage state (cookies + localStorage) du navigateur
        d'auth dans `path` (JSON)."""
        if self._auth_driver is None:
            raise RuntimeError("Ouvre d'abord 'Open Auth Browser'.")
        save_storage_state(self._auth_driver, Path(path))
        logger.info(f"Storage state enregistre -> {path}")

    @keyword("Close Auth Browser")
    def close_auth_browser(self) -> None:
        """Ferme le navigateur d'auth."""
        if self._auth_driver is not None:
            self._auth_driver.quit()
            self._auth_driver = None
