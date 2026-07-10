"""Compare le rendu d'un site entre deux versions de Firefox pilotees en parallele.

API publique (Python pur, sans dependance Robot Framework) :

- ``make_firefox`` / ``capture_full_page`` : driver Firefox + capture pleine page
- ``compare_images`` / ``DiffResult`` : diff pixel entre deux captures
- ``DualSession`` : session double (2 Firefox en lockstep)
- ``save_storage_state`` / ``apply_storage_state`` : storage state (cookies + localStorage)
- ``slugify`` : nom de dossier a partir d'une etape

La librairie Robot Framework vit dans ``selenium_screenshot_compare.ScreenshotCompareLibrary``.
"""

from __future__ import annotations

from .capture import capture_full_page, make_firefox
from .comparison import DiffResult, compare_images
from .naming import slugify
from .session import DualSession
from .storage import apply_storage_state, save_storage_state

__all__ = [
    "DiffResult",
    "DualSession",
    "apply_storage_state",
    "capture_full_page",
    "compare_images",
    "make_firefox",
    "save_storage_state",
    "slugify",
]

__version__ = "0.1.0"
