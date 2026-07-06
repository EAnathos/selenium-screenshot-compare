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


def capture_screenshot(url: str, binary: str, out: Path, width: int = 1280,
                       height: int = 900, wait: float = 2.0) -> str:
    """Ouvre `url` avec le binaire Firefox donne, enregistre une capture pleine
    page dans `out` et renvoie la version reelle du navigateur utilise.

    `binary` vide -> Firefox par defaut du systeme.
    """
    out = Path(out)
    options = Options()
    options.add_argument("--headless")
    if binary:
        options.binary_location = binary
    # Fenetre de taille fixe : indispensable pour que les deux captures soient
    # comparables pixel a pixel.
    options.add_argument(f"--width={width}")
    options.add_argument(f"--height={height}")
    # Force le chargement immediat des images en "loading=lazy" (sinon elles ne
    # se chargent qu'une fois visibles a l'ecran -> trous dans la capture).
    options.set_preference("dom.image-lazy-loading.enabled", False)

    driver = webdriver.Firefox(options=options, service=Service())
    try:
        driver.set_window_size(width, height)
        driver.get(url)
        time.sleep(wait)  # laisse le temps au rendu / animations de se stabiliser
        # Fait defiler toute la page pour declencher le contenu paresseux
        # (images, iframes, animations au scroll via IntersectionObserver), puis
        # remonte en haut avant la capture.
        _scroll_full_page(driver, wait)
        version = driver.capabilities.get("browserVersion", "?")
        # get_full_page_screenshot_as_png est specifique a Firefox : capture toute
        # la page, pas seulement la partie visible.
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(driver.get_full_page_screenshot_as_png())
        return version
    finally:
        driver.quit()


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
