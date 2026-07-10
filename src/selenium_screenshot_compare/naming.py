#!/usr/bin/env python3
"""Petits utilitaires de nommage."""

from __future__ import annotations

import re
from urllib.parse import urlparse


def slugify(value: str) -> str:
    """Transforme une URL ou un nom d'etape en identifiant de dossier sur.

    Ex : "https://site/en" -> "en", "apres-clic" -> "apres-clic".
    """
    path = urlparse(value).path.strip("/") or value
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", path).strip("-")
    return slug or "index"
