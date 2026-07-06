"""Cœur reutilisable : capture, comparaison, session double et nommage.

Sans dependance a Robot Framework -> utilisable depuis la librairie Robot
Framework (ScreenshotCompareLibrary.py) comme en Python pur.
"""
from .capture import capture_full_page, make_firefox
from .comparison import DiffResult, compare_images
from .naming import slugify
from .session import DualSession
from .storage import apply_storage_state, save_storage_state

__all__ = [
    "capture_full_page",
    "make_firefox",
    "compare_images",
    "DiffResult",
    "slugify",
    "DualSession",
    "save_storage_state",
    "apply_storage_state",
]
