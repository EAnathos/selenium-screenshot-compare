#!/usr/bin/env python3
"""Full-page capture using a given Firefox binary.

Selenium Manager (bundled with selenium >= 4.6) downloads geckodriver on its own.
"""

from __future__ import annotations

import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


def make_firefox(binary: str, width: int = 1280, height: int = 900, headless: bool = True):
    """Create a Firefox driver pointed at `binary` (empty = default).

    Fixed-size window: required for two captures to be pixel-comparable. Image
    lazy-loading is disabled to avoid holes in full-page captures.
    `headless=False` opens a visible window (useful to log in manually before
    capturing the auth state).
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
    """Capture the whole page currently loaded in `driver` into `out`.

    Waits `wait` seconds, scrolls the full page to trigger lazy content, scrolls
    back to the top, then writes the full-height screenshot (Firefox-specific:
    get_full_page_screenshot_as_png).
    """
    out = Path(out)
    time.sleep(wait)  # let the rendering / animations settle
    _scroll_full_page(driver, wait)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(driver.get_full_page_screenshot_as_png())


def _scroll_full_page(driver, wait: float) -> None:
    """Scroll the page top-to-bottom in steps to force lazy content to load,
    then scroll back to the top."""
    total = driver.execute_script("return document.body.scrollHeight")
    viewport = driver.execute_script("return window.innerHeight")
    y = 0
    while y < total:
        driver.execute_script("window.scrollTo(0, arguments[0]);", y)
        time.sleep(0.3)
        y += viewport
        # Height may grow as more content loads.
        total = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(min(wait, 1.0))  # let the last images finish rendering
