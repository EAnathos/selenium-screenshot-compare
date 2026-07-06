#!/usr/bin/env python3
"""Pre-run modifier Robot Framework : crawle le site AVANT l'execution et
remplace le test placeholder de la suite par UN test distinct par page.

Chaque page devient ainsi un test independant -> pass/fail granulaire dans le
rapport RF (log.html / report.html).

Usage :
    robot --prerunmodifier PerPageModifier.py:<START_URL>:<MAX_PAGES>:<MAX_DEPTH> \
          tests/firefox_versions.robot
"""
from __future__ import annotations

import os
import sys

# Racine du projet (parent de src/) sur le path pour importer le package `src`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robot.api import SuiteVisitor, logger  # noqa: E402

from src import crawl_site  # noqa: E402

# Keyword de la suite appele par chaque test genere.
TEMPLATE_KEYWORD = "Compare One Page"


class PerPageModifier(SuiteVisitor):
    """Injecte un test par page decouverte lors du crawl."""

    def __init__(self, start_url: str, max_pages: int = 20, max_depth: int = 3):
        self.start_url = start_url
        self.max_pages = int(max_pages)
        self.max_depth = int(max_depth)

    def start_suite(self, suite):
        # N'agit que sur la suite qui definit le keyword template (evite d'agir
        # sur une eventuelle suite parente de type dossier).
        kw_names = [kw.name for kw in suite.resource.keywords]
        if TEMPLATE_KEYWORD not in kw_names:
            return

        urls = crawl_site(self.start_url, self.max_pages, self.max_depth)
        logger.info(f"{len(urls)} page(s) decouverte(s) -> {len(urls)} test(s).")

        suite.tests.clear()  # retire le test placeholder
        for url in urls:
            test = suite.tests.create(name=f"Compare {url}")
            test.body.create_keyword(name=TEMPLATE_KEYWORD, args=[url])
