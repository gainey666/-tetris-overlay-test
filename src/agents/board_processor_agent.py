"""Simple board-mask extraction using OpenCV (Python fallback)."""

from __future__ import annotations

import logging
import queue
import threading
from typing import Optional

import cv2
import numpy as np

from .base_agent import BaseAgent
from .capture_agent import CaptureAgent

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


class BoardProcessorAgent(BaseAgent):
    """Consumes frames from CaptureAgent and emits a 20×10 binary mask."""

    def __init__(
    @trace_calls('__init__', 'board_processor_agent.py', 38)
        self,
        capture_agent: CaptureAgent,
        board_width: int = 20,
        board_height: int = 10,
        queue_maxsize: int = 5,
    ) -> None:
        self.capture_agent = capture_agent
        self.board_width = board_width
        self.board_height = board_height
        self.mask_queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=queue_maxsize)
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def _process_loop(self) -> None:
    @trace_calls('_process_loop', 'board_processor_agent.py', 52)
        log.info("BoardProcessorAgent started.")
        while not self._stop_event.is_set():
            try:
                frame = self.capture_agent.frame_queue.get(timeout=0.2)
            except queue.Empty:
                continue

            mask = self._create_mask(frame)
            try:
                self.mask_queue.put(mask, timeout=0.1)
            except queue.Full:
                try:
                    _ = self.mask_queue.get_nowait()
                    self.mask_queue.put_nowait(mask)
                except queue.Empty:
                    pass

        log.info("BoardProcessorAgent stopped.")

    def start(self) -> None:
    @trace_calls('start', 'board_processor_agent.py', 72)
        self.capture_agent.start()
        if self._thread and self._thread.is_alive():
            log.debug("BoardProcessorAgent already running.")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._process_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
    @trace_calls('stop', 'board_processor_agent.py', 81)
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def handle(self, params: Optional[dict] = None) -> None:
    @trace_calls('handle', 'board_processor_agent.py', 86)
        self.capture_agent.start()
        self.start()

    def _create_mask(self, frame: np.ndarray) -> np.ndarray:
    @trace_calls('_create_mask', 'board_processor_agent.py', 90)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2,
        )
        mask_resized = cv2.resize(
            thresh,
            (self.board_width, self.board_height),
            interpolation=cv2.INTER_NEAREST,
        )
        mask_binary = np.where(mask_resized > 127, 255, 0).astype(np.uint8)
        return mask_binary
