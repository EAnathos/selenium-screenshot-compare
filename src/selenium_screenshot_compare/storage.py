#!/usr/bin/env python3
"""Capture / restauration d'un "storage state" facon Playwright :
cookies + localStorage, serialises en JSON.

Permet d'enregistrer une session authentifiee depuis un navigateur, puis de la
rejouer dans d'autres navigateurs sans refaire le login.
"""

from __future__ import annotations

import contextlib
import json
from pathlib import Path

# Cles de cookie acceptees par Selenium add_cookie().
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
    """Renvoie le storage state courant du driver (cookies + localStorage)."""
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
    """Ecrit le storage state courant du driver dans `path` (JSON)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = capture_storage_state(driver)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def apply_storage_state(driver, path) -> bool:
    """Injecte cookies + localStorage depuis `path` dans le driver.

    Le driver doit deja etre sur le domaine cible (add_cookie l'exige).
    Renvoie False si le fichier n'existe pas. L'appelant doit recharger la page
    pour que le site prenne en compte la session restauree.
    """
    path = Path(path)
    if not path.exists():
        return False
    data = json.loads(path.read_text(encoding="utf-8"))

    for cookie in data.get("cookies", []):
        clean = {k: cookie[k] for k in _COOKIE_KEYS if k in cookie}
        # cookie d'un autre domaine, sameSite invalide... on ignore.
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
