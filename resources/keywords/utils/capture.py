#!/usr/bin/env python3
"""Capture d'une page en pleine hauteur avec un binaire Firefox donne.

Selenium Manager (integre a selenium >= 4.6) telecharge geckodriver tout seul.
"""
from __future__ import annotations

import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


def make_firefox(binary: str, width: int = 1280, height: int = 900,
                 headless: bool = True):
    """Cree un driver Firefox pointant sur `binary` (vide = defaut).

    Fenetre de taille fixe : indispensable pour que deux captures soient
    comparables pixel a pixel. Le lazy-loading des images est desactive pour ne
    pas avoir de trous dans les captures pleine page. `headless=False` ouvre une
    fenetre visible (utile pour se connecter a la main avant de capturer l'auth).
    """
    options = Options()
    if headless:
        options.add_argument("--headless")
    if binary:
        options.binary_location = binary
    options.add_argument(f"--width={width}")
    options.add_argument(f"--height={height}")
    options.set_preference("dom.image-lazy-loading.enabled", False)

    driver = webdriver.Firefox(options=options, service=Service())
    driver.set_window_size(width, height)
    return driver


def capture_full_page(driver, out: Path, wait: float = 2.0) -> None:
    """Capture toute la page actuellement chargee dans `driver` vers `out`.

    Attend `wait` s, fait defiler toute la page pour declencher le contenu
    paresseux, remonte, puis enregistre la capture pleine hauteur (specifique
    Firefox : get_full_page_screenshot_as_png).
    """
    out = Path(out)
    time.sleep(wait)  # laisse le rendu / les animations se stabiliser
    _scroll_full_page(driver, wait)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(driver.get_full_page_screenshot_as_png())


def _scroll_full_page(driver, wait: float) -> None:
    """Defile la page de haut en bas par paliers pour forcer le chargement du
    contenu paresseux, puis revient en haut."""
    total = driver.execute_script("return document.body.scrollHeight")
    viewport = driver.execute_script("return window.innerHeight")
    y = 0
    while y < total:
        driver.execute_script("window.scrollTo(0, arguments[0]);", y)
        time.sleep(0.3)
        y += viewport
        # La hauteur peut grandir a mesure que du contenu se charge.
        total = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(min(wait, 1.0))  # laisse les dernieres images finir de s'afficher
