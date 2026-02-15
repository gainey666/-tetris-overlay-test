"""High-level driver that ties capture, processing, prediction, and overlay."""
from __future__ import annotations

import logging
import threading
import time
from typing import Dict, Optional

from .base_agent import BaseAgent
from .capture_agent import CaptureAgent
from .board_processor_agent import BoardProcessorAgent
from .prediction_agent import PredictionAgent
from .overlay_renderer_agent import OverlayRendererAgent

log = logging.getLogger(__name__)


class RunAgent(BaseAgent):
    """Runs the full pipeline for a specified duration."""

    def __init__(self, params: Optional[Dict] = None) -> None:
        self.params = params or {}
        self._stop_event = threading.Event()
        self.capture = CaptureAgent()
        self.board = BoardProcessorAgent(self.capture)
        self.prediction = PredictionAgent(self.board)
        self.overlay = OverlayRendererAgent(self.board, self.prediction)

    def handle(self, params: Optional[Dict] = None) -> None:
        if params:
            self.params.update(params)
        duration = self.params.get("duration", 30)
        log.info("RunAgent starting pipeline for %s seconds.", duration)

        self.capture.start()
        self.board.start()
        self.prediction.start()
        self.overlay.handle()

        start = time.perf_counter()
        while not self._stop_event.is_set():
            if time.perf_counter() - start >= duration:
                break
            time.sleep(0.1)

        self.shutdown()
        log.info("RunAgent completed after %.2f s.", time.perf_counter() - start)

    def shutdown(self) -> None:
        self._stop_event.set()
        try:
            self.overlay.stop()
        finally:
            self.prediction.stop()
            self.board.stop()
            self.capture.stop()
