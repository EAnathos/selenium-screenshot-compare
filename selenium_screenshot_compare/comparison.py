#!/usr/bin/env python3
"""Pixel comparison of two screenshots."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops


@dataclass
class DiffResult:
    """Result of a comparison between two captures."""

    percent: float  # percentage of differing pixels
    first_diff_y: int | None  # first row of substantial divergence (px)
    width: int
    height: int


def compare_images(img_a: Path, img_b: Path, diff_out: Path, threshold: int = 20) -> DiffResult:
    """Compare two captures, write an image highlighting the differences, and
    return a DiffResult.

    `threshold`: colour delta (0-255) below which a pixel is considered
    identical, to absorb anti-aliasing noise.
    """
    a = Image.open(img_a).convert("RGB")
    b = Image.open(img_b).convert("RGB")

    # The two versions may produce pages of slightly different heights: align
    # on the largest one, padding with white.
    w = max(a.width, b.width)
    h = max(a.height, b.height)
    canvas_a = Image.new("RGB", (w, h), "white")
    canvas_b = Image.new("RGB", (w, h), "white")
    canvas_a.paste(a, (0, 0))
    canvas_b.paste(b, (0, 0))

    diff = ImageChops.difference(canvas_a, canvas_b)

    # Vectorised analysis (numpy): fast even on a multi-megapixel full-page
    # capture. A pixel "differs" if the delta exceeds `threshold` on at least
    # one channel, to ignore anti-aliasing noise.
    arr = np.asarray(diff, dtype=np.int16)  # (h, w, 3)
    per_pixel = arr.max(axis=2)  # max RGB delta, per pixel
    differing = per_pixel > threshold  # (h, w) boolean
    changed = int(differing.sum())
    total = w * h
    pct = 100.0 * changed / total if total else 0.0

    # First row where a SUBSTANTIAL share of pixels differ: much more telling
    # than the first isolated pixel (often just anti-aliasing). Spots the
    # actual vertical offset of the layout.
    row_frac = differing.mean(axis=1)  # fraction differing per row
    substantial = np.where(row_frac > 0.10)[0]  # >10 % of the row
    first_diff_y = int(substantial[0]) if substantial.size else None

    # Amplified diff image (differences shown light on a dark background).
    Path(diff_out).parent.mkdir(parents=True, exist_ok=True)
    diff.point(lambda p: min(255, p * 8)).save(diff_out)

    return DiffResult(percent=pct, first_diff_y=first_diff_y, width=w, height=h)
