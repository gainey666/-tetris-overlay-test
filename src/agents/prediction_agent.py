"""Stub prediction agent – in a real system this would run an ONNX model."""

from __future__ import annotations

import logging
import queue
import threading
from typing import Optional, Tuple

import numpy as np

from .base_agent import BaseAgent
from .board_processor_agent import BoardProcessorAgent

log = logging.getLogger(__name__)


class PredictionAgent(BaseAgent):
    """Consumes binary masks and produces dummy piece predictions."""

    def __init__(self, board_processor: BoardProcessorAgent, queue_maxsize: int = 5):
        self.board_processor = board_processor
        self.prediction_queue: queue.Queue[list[Tuple[int, int, str]]] = queue.Queue(
            maxsize=queue_maxsize
        )
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            log.debug("PredictionAgent already running.")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def handle(self, params: Optional[dict] = None) -> None:
        self.board_processor.start()
        self.start()

    def _run(self) -> None:
        log.info("PredictionAgent started.")
        while not self._stop_event.is_set():
            try:
                mask = self.board_processor.mask_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            preds = self._fake_predict(mask)
            try:
                self.prediction_queue.put(preds, timeout=0.1)
            except queue.Full:
                try:
                    _ = self.prediction_queue.get_nowait()
                    self.prediction_queue.put_nowait(preds)
                except queue.Empty:
                    pass
        log.info("PredictionAgent stopped.")

    def _fake_predict(self, mask: np.ndarray) -> list[Tuple[int, int, str]]:
        import random

        piece_types = ["X", "O", "R", "B", "N", "Q", "K"]
        rows, cols = mask.shape
        predictions = []
        for r in range(rows):
            for c in range(cols):
                if mask[r, c] == 255:
                    predictions.append((r, c, random.choice(piece_types)))
        return predictions
