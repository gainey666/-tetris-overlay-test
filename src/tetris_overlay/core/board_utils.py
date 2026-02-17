"""Utilities for extracting a normalized Tetris board matrix."""
from __future__ import annotations

import logging
from typing import Tuple

import cv2
import numpy as np

try:  # pragma: no cover - defensive tracer import
    from tracer.client import safe_trace_calls as trace_calls
except Exception:  # pragma: no cover
    def trace_calls(*_, **__):  # type: ignore[misc]
        def _decorator(func):
            return func

        return _decorator

LOGGER = logging.getLogger(__name__)

BOARD_HEIGHT = 20
BOARD_WIDTH = 10


def _ensure_rgb_array(image) -> np.ndarray:
    array = np.array(image)
    if array.ndim == 2:
        return cv2.cvtColor(array, cv2.COLOR_GRAY2RGB)
    if array.shape[2] == 4:
        return cv2.cvtColor(array, cv2.COLOR_RGBA2RGB)
    return array if image.mode == "RGB" else array[:, :, ::-1]


@trace_calls("S")
def roi_to_binary_matrix(roi_image) -> np.ndarray:
    """Convert an ROI image to a normalized 20×10 binary matrix (values 0/1)."""
    frame = _ensure_rgb_array(roi_image)
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2,
    )
    board = cv2.resize(thresh, (BOARD_WIDTH, BOARD_HEIGHT), interpolation=cv2.INTER_NEAREST)
    binary = (board > 0).astype("uint8")
    return binary


@trace_calls("S")
def extract_board(image) -> np.ndarray:
    """Extract board state from a captured image and return a normalized matrix."""
    binary = roi_to_binary_matrix(image)
    if binary.shape != (BOARD_HEIGHT, BOARD_WIDTH):
        raise ValueError(f"Unexpected board shape {binary.shape}")

    fill_ratio = float(binary.mean())
    if fill_ratio < 0.01:
        LOGGER.warning("Extracted board appears empty (ratio=%.4f)", fill_ratio)
    return binary
