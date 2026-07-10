#!/usr/bin/env python3
"""Playwright-style "storage state" capture and restore:
cookies + localStorage, serialised as JSON.

Lets you record an authenticated session from one browser, then replay it in
other browsers without going through the login flow again.
"""

from __future__ import annotations

import contextlib
import json
from pathlib import Path

# Cookie keys accepted by Selenium add_cookie().
_COOKIE_KEYS = ("name", "value", "path", "domain", "secure", "httpOnly", "expiry", "sameSite")

_LOCALSTORAGE_JS = (
    "var o = {};"
    "for (var i = 0; i < window.localStorage.length; i++) {"
    "  var k = window.localStorage.key(i);"
    "  o[k] = window.localStorage.getItem(k);"
    "}"
    "return o;"
)


def capture_storage_state(driver) -> dict:
    """Return the driver's current storage state (cookies + localStorage)."""
    local_storage = driver.execute_script(_LOCALSTORAGE_JS) or {}
    origin = driver.execute_script("return window.location.origin;")
    return {
        "cookies": driver.get_cookies(),
        "origins": [
            {
                "origin": origin,
                "localStorage": [{"name": k, "value": v} for k, v in local_storage.items()],
            }
        ],
    }


def save_storage_state(driver, path) -> None:
    """Write the driver's current storage state to `path` (JSON)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = capture_storage_state(driver)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def apply_storage_state(driver, path) -> bool:
    """Inject cookies + localStorage from `path` into the driver.

    The driver must already be on the target domain (add_cookie requires it).
    Returns False if the file does not exist. The caller must reload the page
    for the site to pick up the restored session.
    """
    path = Path(path)
    if not path.exists():
        return False
    data = json.loads(path.read_text(encoding="utf-8"))

    for cookie in data.get("cookies", []):
        clean = {k: cookie[k] for k in _COOKIE_KEYS if k in cookie}
        # Cookie from another domain, invalid sameSite, etc. — ignore.
        with contextlib.suppress(Exception):
            driver.add_cookie(clean)

    for origin in data.get("origins", []):
        for item in origin.get("localStorage", []):
            with contextlib.suppress(Exception):
                driver.execute_script(
                    "window.localStorage.setItem(arguments[0], arguments[1]);",
                    item["name"],
                    item["value"],
                )
    return True
