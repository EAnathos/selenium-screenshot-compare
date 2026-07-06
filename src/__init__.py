"""Cœur reutilisable : capture, comparaison et crawl.

Sans dependance a Robot Framework -> utilisable en script pur (compare.py) comme
depuis la librairie Robot Framework (ScreenshotCompareLibrary.py).
"""
from .capture import capture_screenshot
from .comparison import DiffResult, compare_images
from .crawl import crawl_site, slugify

__all__ = [
    "capture_screenshot",
    "compare_images",
    "DiffResult",
    "crawl_site",
    "slugify",
]
