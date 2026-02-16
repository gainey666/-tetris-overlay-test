"""Utility helpers for loading ROI definitions and capturing each rectangle."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict

from capture import ScreenCapture

CONFIG_PATH = Path("config/roi_config.json")

log = logging.getLogger(__name__)


def load_roi_config() -> list[dict]:
    """Return the ROI list stored in roi_config.json."""
    if not CONFIG_PATH.is_file():
        raise FileNotFoundError(
            f"{CONFIG_PATH} missing – run calibration (Ctrl+Alt+C) to generate it"
        )
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    rois = data.get("rois", [])
    if not isinstance(rois, list):
        raise ValueError("Invalid ROI config – expected 'rois' list")
    return rois


def _instantiate_capture(rect: list[int]) -> ScreenCapture:
    left, top, width, height = rect
    return ScreenCapture((left, top, width, height))


def capture_all() -> Dict[str, Any]:
    """Grab every rectangular ROI and return name -> Pillow Image."""
    rois = load_roi_config()
    frames: Dict[str, Any] = {}
    for entry in rois:
        name = entry.get("name")
        rect = entry.get("rect")
        if not name or rect is None:
            continue
        if isinstance(rect, list) and rect and isinstance(rect[0], list):
            # skip composite lists such as next_queue – handled by dedicated helper
            log.debug("Skipping composite ROI '%s' in capture_all", name)
            continue
        try:
            capture = _instantiate_capture([int(v) for v in rect])
            frames[name] = capture.grab()
        except Exception as exc:  # pragma: no cover
            log.error("Capture failed for %s: %s", name, exc)
    return frames


__all__ = ["load_roi_config", "capture_all"]
