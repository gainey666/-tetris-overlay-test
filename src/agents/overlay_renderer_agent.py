"""Render the board mask + predictions using pygame (ghost window)."""
from __future__ import annotations

import logging
import queue
import threading
import time
from typing import List, Optional, Tuple

import numpy as np
import pygame

from .base_agent import BaseAgent
from .board_processor_agent import BoardProcessorAgent
from .prediction_agent import PredictionAgent

log = logging.getLogger(__name__)


class OverlayRendererAgent(BaseAgent):
    """Draws a semi-transparent overlay on top of a live view."""

    def __init__(
        self,
        board_processor: BoardProcessorAgent,
        prediction_agent: PredictionAgent,
        scale: int = 30,
        fps: int = 30,
    ) -> None:
        self.board_processor = board_processor
        self.prediction_agent = prediction_agent
        self.scale = scale
        self.fps = fps

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._initialized = False

    def handle(self, params: Optional[dict] = None) -> None:
        params = params or {}
        blocking = params.get("blocking", True)
        duration = params.get("duration", 5 if blocking else None)
        stop_upstream = params.get("stop_upstream", blocking)

        self.board_processor.start()
        self.prediction_agent.start()
        self._start_render_loop()

        if blocking:
            self._wait_until(duration)
            self.stop()
            if stop_upstream:
                self._stop_upstream()

    def _start_render_loop(self) -> None:
        if self._thread and self._thread.is_alive():
            log.debug("OverlayRendererAgent already running.")
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._render_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        if self._initialized:
            pygame.quit()
            self._initialized = False
        self._thread = None

    def _render_loop(self) -> None:
        pygame.init()
        self._initialized = True

        width = self.board_processor.board_width * self.scale
        height = self.board_processor.board_height * self.scale
        window = pygame.display.set_mode((width, height), pygame.NOFRAME)
        pygame.display.set_caption("WindSurf Overlay (ghost)")

        clock = pygame.time.Clock()
        log.info("OverlayRendererAgent rendering at %d FPS.", self.fps)

        while not self._stop_event.is_set():
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    self._stop_event.set()
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                    self._stop_event.set()

            try:
                mask = self.board_processor.mask_queue.get_nowait()
            except queue.Empty:
                mask = None

            try:
                preds = self.prediction_agent.prediction_queue.get_nowait()
            except queue.Empty:
                preds = None

            window.fill((0, 0, 0, 0))
            if mask is not None:
                self._draw_mask(window, mask)
            if preds is not None:
                self._draw_predictions(window, preds)

            pygame.display.flip()
            clock.tick(self.fps)

        pygame.quit()
        self._initialized = False
        log.info("OverlayRendererAgent stopped.")

    def _wait_until(self, duration: Optional[float]) -> None:
        start = time.perf_counter()
        while not self._stop_event.is_set():
            if duration is not None and time.perf_counter() - start >= duration:
                break
            time.sleep(0.1)

    def _stop_upstream(self) -> None:
        try:
            self.prediction_agent.stop()
        finally:
            self.board_processor.stop()
            capture = getattr(self.board_processor, "capture_agent", None)
            if capture is not None:
                capture.stop()

    def _draw_mask(self, surface: pygame.Surface, mask: np.ndarray) -> None:
        rows, cols = mask.shape
        cell_w = self.scale
        cell_h = self.scale
        for r in range(rows):
            for c in range(cols):
                if mask[r, c] == 255:
                    rect = pygame.Rect(c * cell_w, r * cell_h, cell_w, cell_h)
                    s = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
                    s.fill((255, 255, 255, 120))
                    surface.blit(s, rect.topleft)

    def _draw_predictions(
        self, surface: pygame.Surface, preds: List[Tuple[int, int, str]]
    ) -> None:
        font = pygame.font.SysFont("Arial", max(12, self.scale // 2))
        for r, c, piece in preds:
            cx = c * self.scale + self.scale // 2
            cy = r * self.scale + self.scale // 2
            colour = tuple(((hash(piece) >> shift) & 0xFF) for shift in (0, 8, 16))
            pygame.draw.circle(surface, colour, (cx, cy), self.scale // 3)
            label = font.render(piece, True, (255, 255, 255))
            surface.blit(label, label.get_rect(center=(cx, cy)))
