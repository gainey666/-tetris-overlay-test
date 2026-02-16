"""Capture helper for the next-piece queue (up to four slots)."""

from __future__ import annotations

import logging
from typing import Any, List

import mss  # type: ignore

from capture import ScreenCapture
from roi_capture import load_roi_config

log = logging.getLogger(__name__)

_FULL_CAPTURE: ScreenCapture | None = None


def _full_rect() -> tuple[int, int, int, int]:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        return (monitor["left"], monitor["top"], monitor["width"], monitor["height"])


def _get_full_capture() -> ScreenCapture:
    global _FULL_CAPTURE
    if _FULL_CAPTURE is None:
        rect = _full_rect()
        log.debug("Initializing full-screen capture for next queue: %s", rect)
        _FULL_CAPTURE = ScreenCapture(rect)
    return _FULL_CAPTURE


def _grab_full_frame():
    return _get_full_capture().grab()


def _crop(image, rect: list[int]):
    left, top, width, height = rect
    return image.crop((left, top, left + width, top + height))


def _queue_entry() -> dict:
    for entry in load_roi_config():
        if entry.get("name") == "next_queue":
            return entry
    raise KeyError("next_queue entry missing from roi_config.json")


def capture_next_queue(frame=None) -> List[Any]:
    """Capture the queue rectangles in order and return a list of images."""
    entry = _queue_entry()
    rects = entry.get("rect", [])
    if not isinstance(rects, list):
        raise ValueError("next_queue rect must be a list of rectangles")
    frame = frame or _grab_full_frame()
    images: List[Any] = []
    for rect in rects:
        if not isinstance(rect, list) or len(rect) != 4:
            log.warning("Skipping malformed next_queue rect: %s", rect)
            continue
        try:
            images.append(_crop(frame, [int(v) for v in rect]))
        except Exception as exc:  # pragma: no cover
            log.error("Failed to capture queue rect %s: %s", rect, exc)
    return images


__all__ = ["capture_next_queue"]
