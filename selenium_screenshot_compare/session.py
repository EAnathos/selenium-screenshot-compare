#!/usr/bin/env python3
"""Session driving TWO Firefox instances (version A and B) in parallel: every
action (click, input, navigation) is replayed identically in both, so we can
compare the rendering after any interaction — like a real test.
"""

from __future__ import annotations

import contextlib
import time
from pathlib import Path

from selenium.webdriver.common.by import By

from .capture import capture_full_page, make_firefox
from .storage import apply_storage_state

# Selenium-style locator strategies (locator = "strategy=value").
_STRATEGIES = {
    "css": By.CSS_SELECTOR,
    "xpath": By.XPATH,
    "id": By.ID,
    "name": By.NAME,
    "link": By.LINK_TEXT,
    "partial link": By.PARTIAL_LINK_TEXT,
    "tag": By.TAG_NAME,
    "class": By.CLASS_NAME,
}


def parse_locator(locator: str):
    """ "css=a.btn", "id=submit", "xpath=//a"... -> (By.*, value).
    Default: xpath if it starts with //, otherwise a CSS selector."""
    for sep in ("=", ":"):
        if sep in locator:
            strategy, _, value = locator.partition(sep)
            key = strategy.strip().lower()
            if key in _STRATEGIES:
                return _STRATEGIES[key], value.strip()
    if locator.startswith(("//", "(//")):
        return By.XPATH, locator
    return By.CSS_SELECTOR, locator


class DualSession:
    """Two Firefox drivers driven in lockstep."""

    def __init__(self, firefox_a: str, firefox_b: str, width: int = 1280, height: int = 900):
        self.driver_a = make_firefox(firefox_a, width, height)
        self.driver_b = make_firefox(firefox_b, width, height)
        self.version_a = self.driver_a.capabilities.get("browserVersion", "?")
        self.version_b = self.driver_b.capabilities.get("browserVersion", "?")

    @property
    def _drivers(self):
        return (self.driver_a, self.driver_b)

    # -- navigation / interactions (replayed on both versions) --------------

    def open(self, url: str) -> None:
        for d in self._drivers:
            d.get(url)
        self._wait_ready()

    def click(self, locator: str) -> None:
        by, value = parse_locator(locator)
        for d in self._drivers:
            d.find_element(by, value).click()
        self._wait_ready()

    def input_text(self, locator: str, text: str) -> None:
        by, value = parse_locator(locator)
        for d in self._drivers:
            el = d.find_element(by, value)
            el.clear()
            el.send_keys(text)

    def go_back(self) -> None:
        for d in self._drivers:
            d.back()
        self._wait_ready()

    def load_storage(self, path) -> bool:
        """Inject the storage state (cookies + localStorage) in both versions,
        then reload. Drivers must already be on the target domain. Returns
        False if the file is missing."""
        applied = False
        for d in self._drivers:
            applied = apply_storage_state(d, path) or applied
        if applied:
            for d in self._drivers:
                d.refresh()
            self._wait_ready()
        return applied

    def _wait_ready(self, timeout: float = 10.0) -> None:
        """Wait for document.readyState == complete on both drivers."""
        for d in self._drivers:
            end = time.time() + timeout
            while time.time() < end:
                if d.execute_script("return document.readyState") == "complete":
                    break
                time.sleep(0.1)

    # -- capture ------------------------------------------------------------

    def capture_both(self, shot_a: Path, shot_b: Path, wait: float = 2.0):
        """Capture the current state of both versions. Returns (version_a, version_b)."""
        capture_full_page(self.driver_a, shot_a, wait)
        capture_full_page(self.driver_b, shot_b, wait)
        return self.version_a, self.version_b

    def close(self) -> None:
        for d in self._drivers:
            with contextlib.suppress(Exception):
                d.quit()
