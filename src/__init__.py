"""Cœur reutilisable : capture, comparaison, crawl et session double.

Sans dependance a Robot Framework -> utilisable en script pur (compare.py) comme
depuis la librairie Robot Framework (ScreenshotCompareLibrary.py).
"""
from .capture import capture_full_page, capture_screenshot, make_firefox
from .comparison import DiffResult, compare_images
from .crawl import crawl_site, slugify
from .session import DualSession

__all__ = [
    "capture_screenshot",
    "capture_full_page",
    "make_firefox",
    "compare_images",
    "DiffResult",
    "crawl_site",
    "slugify",
    "DualSession",
]
