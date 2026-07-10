"""Compare a website's rendering between two Firefox versions driven in parallel.

Public API (plain Python, no Robot Framework dependency):

- ``make_firefox`` / ``capture_full_page``: Firefox driver + full-page capture
- ``compare_images`` / ``DiffResult``: pixel diff between two captures
- ``DualSession``: dual session (2 Firefox instances in lockstep)
- ``save_storage_state`` / ``apply_storage_state``: storage state (cookies + localStorage)
- ``slugify``: folder name from a step label

The Robot Framework library lives in ``selenium_screenshot_compare.ScreenshotCompareLibrary``.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

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

try:
    __version__ = version("selenium-screenshot-compare")
except PackageNotFoundError:  # package not installed (e.g. running from a checkout)
    __version__ = "0.0.0+unknown"
