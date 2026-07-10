#!/usr/bin/env python3
"""Robot Framework library: drives TWO Firefox versions in parallel and
compares their rendering after every interaction (click, input, navigation).
Also handles capturing / restoring a storage state (cookies + localStorage).

Robot Framework import (once the package is installed):

    Library    selenium_screenshot_compare.ScreenshotCompareLibrary

Exposed keywords:
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

from . import (
    DualSession,
    __version__,
    compare_images,
    make_firefox,
    slugify,
)
from . import save_storage_state as _save_storage_state


@library(scope="GLOBAL", version=__version__)
class ScreenshotCompareLibrary:
    """Compare a website's rendering between two Firefox binaries."""

    def __init__(self):
        self._session: DualSession | None = None
        self._wait: float = 2.0
        self._auth_driver = None

    def _write_result(self, result_path: Path, data: dict) -> None:
        """Write the per-step result file (JSON)."""
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    # -- interactive keywords: drive both versions in lockstep --------------
    # Selenium-style: open a dual session, click / type, then compare the
    # current state. Ideal for a click-based navigation scenario.

    @keyword("Open Versions")
    def open_versions(
        self,
        url: str,
        firefox_a: str,
        firefox_b: str,
        width: int = 1280,
        height: int = 900,
        wait: float = 2.0,
    ) -> None:
        """Open `url` in both Firefox versions (dual session)."""
        self._session = DualSession(firefox_a, firefox_b, width, height)
        self._wait = wait
        self._session.open(url)
        logger.info(
            f"Sessions opened: Firefox {self._session.version_a} "
            f"& {self._session.version_b} on {url}"
        )

    @keyword("Go To")
    def go_to(self, url: str) -> None:
        """Navigate to `url` in both versions."""
        self._require_session().open(url)

    @keyword("Click Element")
    def click_element(self, locator: str) -> None:
        """Click the element (e.g. css=a.btn, id=submit, xpath=//a) in both."""
        self._require_session().click(locator)

    @keyword("Input Text")
    def input_text(self, locator: str, text: str) -> None:
        """Type `text` into the `locator` field in both versions."""
        self._require_session().input_text(locator, text)

    @keyword("Go Back")
    def go_back(self) -> None:
        """Go back to the previous page in both versions."""
        self._require_session().go_back()

    @keyword("Capture And Compare")
    def capture_and_compare(
        self, name: str, output_dir: str, wait: float | None = None, threshold: int = 20
    ) -> float:
        """Capture the current state of both versions, compare, write a
        result.json into output_dir/<name>/ and return the % difference."""
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
        """Inject cookies + localStorage from `path` into both versions
        (authenticated session), then reload. Call after 'Open Versions', once
        on the domain. Logs a warning and is ignored if the file is missing
        (anonymous session)."""
        applied = self._require_session().load_storage(Path(path))
        if applied:
            logger.info(f"Storage state loaded from {path}")
        else:
            logger.warn(
                f"Storage state not found ({path}): anonymous session. "
                "Run tests/capture_auth.robot first."
            )
        return applied

    @keyword("Close Versions")
    def close_versions(self) -> None:
        """Close both browsers of the dual session."""
        if self._session is not None:
            self._session.close()
            self._session = None

    def _require_session(self) -> DualSession:
        if self._session is None:
            raise RuntimeError("No session open: call 'Open Versions' first.")
        return self._session

    # -- storage state capture (single browser) -----------------------------

    @keyword("Open Auth Browser")
    def open_auth_browser(
        self,
        url: str,
        firefox_binary: str,
        headless: bool = False,
        width: int = 1280,
        height: int = 900,
    ) -> None:
        """Open ONE Firefox on `url` (visible by default, so you can log in
        manually before capturing the storage state)."""
        self._auth_driver = make_firefox(firefox_binary, width, height, headless)
        self._auth_driver.get(url)
        logger.info(f"Auth browser opened on {url} (headless={headless})")

    @keyword("Save Storage State")
    def save_storage_state(self, path: str) -> None:
        """Save the auth browser's storage state (cookies + localStorage) to
        `path` (JSON)."""
        if self._auth_driver is None:
            raise RuntimeError("Open 'Open Auth Browser' first.")
        _save_storage_state(self._auth_driver, Path(path))
        logger.info(f"Storage state saved -> {path}")

    @keyword("Close Auth Browser")
    def close_auth_browser(self) -> None:
        """Close the auth browser."""
        if self._auth_driver is not None:
            self._auth_driver.quit()
            self._auth_driver = None
