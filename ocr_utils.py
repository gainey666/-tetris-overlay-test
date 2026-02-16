"""Tiny OCR helper for numeric overlays."""

from __future__ import annotations

import logging
import re

import pytesseract  # type: ignore

log = logging.getLogger(__name__)

_DIGIT_RE = re.compile(r"\d+")


def extract_number(image) -> int:
    """Return the integer value detected in the provided image."""
    if image is None:
        return 0
    try:
        text = pytesseract.image_to_string(image, config="--psm 7 digits")
    except Exception as exc:  # pragma: no cover
        log.error("OCR failure: %s", exc)
        return 0
    match = _DIGIT_RE.search(text or "")
    if not match:
        return 0
    try:
        return int(match.group())
    except ValueError:
        return 0


__all__ = ["extract_number"]
