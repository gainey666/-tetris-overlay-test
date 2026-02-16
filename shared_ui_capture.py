"""Capture helper for score, wins, and timer ROIs shared between players."""

from __future__ import annotations

import logging
from typing import Any, Dict

import mss  # type: ignore

from capture import ScreenCapture
from roi_capture import load_roi_config

log = logging.getLogger(__name__)

_SHARED_NAMES = ("score", "wins", "timer")
_FULL_CAPTURE: ScreenCapture | None = None


def _full_rect() -> tuple[int, int, int, int]:
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        return (monitor["left"], monitor["top"], monitor["width"], monitor["height"])


def _get_full_capture() -> ScreenCapture:
    global _FULL_CAPTURE
    if _FULL_CAPTURE is None:
        rect = _full_rect()
        log.debug("Initializing full-screen capture for shared UI: %s", rect)
        _FULL_CAPTURE = ScreenCapture(rect)
    return _FULL_CAPTURE


def _grab_full_frame():
    return _get_full_capture().grab()


def _crop(image, rect: list[int]):
    left, top, width, height = rect
    return image.crop((left, top, left + width, top + height))


def capture_shared_ui(frame=None) -> Dict[str, Any]:
    """Capture score/wins/timer once per frame and return them in a dict."""
    rois = {entry["name"]: entry.get("rect") for entry in load_roi_config()}
    missing = [name for name in _SHARED_NAMES if name not in rois]
    if missing:
        raise KeyError(f"Shared ROI(s) missing from config: {missing}")

    frame = frame or _grab_full_frame()
    result: Dict[str, Any] = {}
    for name in _SHARED_NAMES:
        rect = rois[name]
        if not isinstance(rect, list) or len(rect) != 4:
            raise ValueError(f"ROI '{name}' must be a [left, top, width, height] list")
        try:
            result[name] = _crop(frame, [int(v) for v in rect])
        except Exception as exc:  # pragma: no cover
            log.error("Failed to capture %s: %s", name, exc)
    return result


__all__ = ["capture_shared_ui"]
