"""Placeholder calibration routine."""
from __future__ import annotations

import logging
from typing import Optional

from ..config import CalibrationConfig
from .base_agent import BaseAgent

log = logging.getLogger(__name__)


class CalibrateAgent(BaseAgent):
    """Writes dummy calibration data to disk."""

    def handle(self, params: Optional[dict] = None) -> None:
        log.info("CalibrateAgent started – performing dummy calibration.")
        calib = CalibrationConfig(
            camera_matrix=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            distortion_coeffs=[0.0, 0.0, 0.0, 0.0, 0.0],
        )
        calib.save()
        log.info("Calibration data saved.")
