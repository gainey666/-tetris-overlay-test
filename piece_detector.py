"""Tetromino detection based on Next Queue captures."""
from __future__ import annotations

import logging
from typing import List, Optional

import cv2
import numpy as np

from next_queue_capture import capture_next_queue

# Optional tracer decorator (no-op when tracer package missing)
try:  # pragma: no cover - defensive import
    from tracer.client import safe_trace_calls as trace_calls
except Exception:  # pragma: no cover
    def trace_calls(*_, **__):  # type: ignore[misc]
        def _decorator(func):
            return func

        return _decorator


log = logging.getLogger(__name__)

# Approximate HSV means for Guideline colours (H in degrees, S/V 0..1)
PIECE_TEMPLATES = {
    "I": {"h": 180, "shape": "line"},
    "O": {"h": 55, "shape": "square"},
    "T": {"h": 285, "shape": "tee"},
    "S": {"h": 130, "shape": "zig"},
    "Z": {"h": 350, "shape": "zig"},
    "J": {"h": 220, "shape": "el"},
    "L": {"h": 30, "shape": "el"},
}


def _ensure_bgr(image) -> np.ndarray:
    array = np.array(image)
    if array.ndim == 2:
        return cv2.cvtColor(array, cv2.COLOR_GRAY2BGR)
    if array.shape[2] == 4:
        return cv2.cvtColor(array, cv2.COLOR_RGBA2BGR)
    return array[:, :, ::-1] if image.mode == "RGB" else array


def _score_template(avg_h: float, aspect_ratio: float, template: dict) -> float:
    # Hue distance on circular scale (degrees 0-360)
    diff = abs(avg_h - template["h"])
    hue_dist = min(diff, 360 - diff)

    if template["shape"] == "line":
        shape_penalty = 0 if aspect_ratio < 0.65 else 40
    elif template["shape"] == "square":
        shape_penalty = 0 if 0.85 <= aspect_ratio <= 1.15 else 25
    elif template["shape"] == "tee":
        shape_penalty = 0 if 0.7 <= aspect_ratio <= 1.4 else 20
    elif template["shape"] == "zig":
        shape_penalty = 0 if 0.8 <= aspect_ratio <= 1.6 else 20
    else:  # "el"
        shape_penalty = 0 if 0.7 <= aspect_ratio <= 1.6 else 15

    return hue_dist + shape_penalty


@trace_calls("S")
def detect_piece_from_image(image) -> Optional[str]:
    """Detect tetromino type from a PIL Image of a queue slot."""
    try:
        bgr = _ensure_bgr(image)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        # Ignore very dark pixels (background)
        mask = cv2.inRange(hsv, (0, 60, 60), (180, 255, 255))
        if mask.mean() < 5:  # mostly empty
            return None

        masked = cv2.bitwise_and(hsv, hsv, mask=mask)
        avg_h = float(masked[:, :, 0][mask > 0].mean()) * 2.0  # OpenCV hue 0-180 -> degrees
        h, w = bgr.shape[:2]
        aspect_ratio = w / h if h else 1.0

        best_piece = None
        best_score = float("inf")
        for piece, template in PIECE_TEMPLATES.items():
            score = _score_template(avg_h, aspect_ratio, template)
            if score < best_score:
                best_piece = piece
                best_score = score

        return best_piece
    except Exception as exc:  # pragma: no cover - defensive logging
        log.error("Piece detection failed: %s", exc)
        return None


@trace_calls("S")
def get_current_piece() -> Optional[str]:
    """Return current piece (first queue slot)."""
    try:
        queue_images = capture_next_queue()
    except Exception as exc:  # pragma: no cover
        log.error("Queue capture failed: %s", exc)
        return None

    if not queue_images:
        log.warning("Queue capture returned no images")
        return None

    return detect_piece_from_image(queue_images[0])


@trace_calls("S")
def get_next_pieces(count: int = 3) -> List[str]:
    """Return the next N pieces detected from the queue."""
    pieces: List[str] = []
    try:
        queue_images = capture_next_queue()
    except Exception as exc:  # pragma: no cover
        log.error("Queue capture failed: %s", exc)
        return pieces

    for image in queue_images[:count]:
        piece = detect_piece_from_image(image)
        if piece:
            pieces.append(piece)

    return pieces
