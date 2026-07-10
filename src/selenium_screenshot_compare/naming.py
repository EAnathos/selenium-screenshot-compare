#!/usr/bin/env python3
"""Small naming utilities."""

from __future__ import annotations

import re
from urllib.parse import urlparse


def slugify(value: str) -> str:
    """Turn a URL or step name into a safe folder identifier.

    E.g. "https://site/en" -> "en", "after-click" -> "after-click".
    """
    path = urlparse(value).path.strip("/") or value
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", path).strip("-")
    return slug or "index"
