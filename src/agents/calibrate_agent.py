"""Placeholder calibration routine."""

from __future__ import annotations

import logging
from typing import Optional

from ..config import CalibrationConfig
from .base_agent import BaseAgent

# Import our logger bridge
try:
    import logger_bridge as log

# Import global function tracer
try:
    from tracer.client import safe_trace_calls as trace_calls
    TRACER_AVAILABLE = True
except ImportError:
    TRACER_AVAILABLE = False

    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False


log = logging.getLogger(__name__)


class CalibrateAgent(BaseAgent):
    """Writes dummy calibration data to disk."""

    def handle(self, params: Optional[dict] = None) -> None:
    @trace_calls('handle', 'calibrate_agent.py', 33)
        log.info("CalibrateAgent started – performing dummy calibration.")
        calib = CalibrationConfig(
            camera_matrix=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            distortion_coeffs=[0.0, 0.0, 0.0, 0.0, 0.0],
        )
        calib.save()
        log.info("Calibration data saved.")
