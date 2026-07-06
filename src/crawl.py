#!/usr/bin/env python3
"""Decouverte des pages d'un site (crawl same-domain, stdlib uniquement)."""
from __future__ import annotations

import re
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.request import Request, urlopen

# Extensions a ignorer (pas des pages HTML).
SKIP_EXT = re.compile(
    r"\.(pdf|zip|png|jpe?g|gif|svg|webp|mp4|mp3|css|js|ico|xml|json)$", re.I)


class _LinkExtractor(HTMLParser):
    """Collecte les href des balises <a>."""

    def __init__(self):
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href" and value:
                    self.links.append(value)


def normalize(url: str) -> str:
    """Retire le fragment (#...) et la barre finale pour dedupliquer."""
    url, _ = urldefrag(url)
    if url.endswith("/") and urlparse(url).path != "/":
        url = url.rstrip("/")
    return url


def slugify(url: str) -> str:
    """Transforme une URL en nom de dossier lisible et sur."""
    path = urlparse(url).path.strip("/") or "index"
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", path).strip("-")
    return slug or "index"


def _fetch_links(url: str, timeout: float) -> list[str]:
    """Recupere le HTML d'une page (via urllib) et renvoie ses liens absolus.

    Note : decouverte statique -> les liens injectes en JS ne sont pas vus.
    """
    req = Request(url, headers={"User-Agent": "screenshot-compare/1.0"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            if "text/html" not in resp.headers.get("Content-Type", ""):
                return []
            body = resp.read().decode("utf-8", errors="replace")
    except Exception:  # reseau, 404, timeout...
        return []
    parser = _LinkExtractor()
    parser.feed(body)
    return [urljoin(url, href) for href in parser.links]


def crawl_site(start: str, max_pages: int = 20, max_depth: int = 3,
               timeout: float = 15.0) -> list[str]:
    """BFS same-domain. Renvoie la liste ordonnee des URLs a comparer."""
    start = normalize(start)
    domain = urlparse(start).netloc
    seen = {start}
    ordered = [start]
    queue = deque([(start, 0)])

    while queue and len(ordered) < max_pages:
        url, depth = queue.popleft()
        if depth >= max_depth:
            continue
        for link in _fetch_links(url, timeout):
            link = normalize(link)
            p = urlparse(link)
            if p.scheme not in ("http", "https") or p.netloc != domain:
                continue
            if SKIP_EXT.search(p.path) or link in seen:
                continue
            seen.add(link)
            ordered.append(link)
            queue.append((link, depth + 1))
            if len(ordered) >= max_pages:
                break
    return ordered
