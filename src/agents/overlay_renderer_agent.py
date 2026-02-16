"""Render the board mask + predictions using pygame (ghost window)."""

from __future__ import annotations

import json
import logging
import queue
import threading
import time
from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
import pygame

from .base_agent import BaseAgent
from .board_processor_agent import BoardProcessorAgent
from .prediction_agent import PredictionAgent

log = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Load the global config once – we need the `auto_fit` flag and the board size
# ----------------------------------------------------------------------
_CFG_PATH = Path.cwd() / "config" / "config.json"
_cfg = json.load(_CFG_PATH.open())
_AUTO_FIT = _cfg.get("auto_fit", True)  # default to the new behaviour
_BOARD_W = _cfg.get("board_width", 20)
_BOARD_H = _cfg.get("board_height", 10)


class OverlayRendererAgent(BaseAgent):
    """Draws a semi-transparent overlay on top of a live view."""

    # -----------------------------------------------------------------
    # Singleton plumbing – the hot‑key agent needs a reference to the
    # *exact* renderer instance that the main loop created.
    # -----------------------------------------------------------------
    _instance: "OverlayRendererAgent | None" = None

    @classmethod
    def instance(cls) -> "OverlayRendererAgent":
        """Return the (already‑created) renderer instance – used by HotkeyAgent."""
        if cls._instance is None:
            raise RuntimeError(
                "OverlayRendererAgent.instance() called before it was created"
            )
        return cls._instance

    def __init__(self, **kw):
        super().__init__(**kw)
        OverlayRendererAgent._instance = self
        self._visible = True

        # These will be set later by RunAgent
        from .board_processor_agent import BoardProcessorAgent
        from .prediction_agent import PredictionAgent
        from .capture_agent import CaptureAgent

        self.board_processor: BoardProcessorAgent | None = None
        self.prediction_agent: PredictionAgent | None = None
        self.capture = CaptureAgent()

        # ----------------------------------------------------------
        # 1️⃣ Grab the ROI size from the CaptureAgent (it is always set)
        # ----------------------------------------------------------
        roi_w = self.capture.roi_width
        roi_h = self.capture.roi_height

        # ----------------------------------------------------------
        # 2️⃣ Decide how big each board cell should be
        # ----------------------------------------------------------
        if _AUTO_FIT:
            # Dynamic sizing – keep cells square, fit inside the ROI
            cell_w = roi_w // _BOARD_W
            cell_h = roi_h // _BOARD_H
            self.cell_px = min(cell_w, cell_h)  # square cells
            self.window_w = _BOARD_W * self.cell_px
            self.window_h = _BOARD_H * self.cell_px
        else:
            # Legacy mode – fixed 15 px per cell (the size you used manually)
            self.cell_px = 15
            self.window_w = _BOARD_W * self.cell_px
            self.window_h = _BOARD_H * self.cell_px

        # ----------------------------------------------------------
        # 3️⃣ Initialise the transparent pygame surface
        # ----------------------------------------------------------
        pygame.init()
        self.screen = pygame.display.set_mode(
            (self.window_w, self.window_h),
            pygame.NOFRAME | pygame.SRCALPHA | pygame.HWSURFACE | pygame.DOUBLEBUF,
        )
        pygame.display.set_caption("Tetris Ghost Overlay")

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._initialized = False

    # -----------------------------------------------------------------
    # Public API used by HotkeyAgent
    # -----------------------------------------------------------------
    def set_visibility(self, visible: bool) -> None:
        """Turn the overlay on/off.  Called from the hot‑key thread."""
        self._visible = visible

    def _rebuild_surface(self):
        """Re‑create the pygame surface after the ROI size has changed."""
        # Re‑compute cell size exactly as we do in __init__
        from .capture_agent import CaptureAgent

        cap = CaptureAgent()
        roi_w = cap.roi_width
        roi_h = cap.roi_height

        if _AUTO_FIT:
            # Dynamic sizing – keep cells square, fit inside the ROI
            cell_w = roi_w // _BOARD_W
            cell_h = roi_h // _BOARD_H
            self.cell_px = min(cell_w, cell_h)  # square cells
            self.window_w = _BOARD_W * self.cell_px
            self.window_h = _BOARD_H * self.cell_px
        else:
            # Legacy mode – fixed 15 px per cell
            self.cell_px = 15
            self.window_w = _BOARD_W * self.cell_px
            self.window_h = _BOARD_H * self.cell_px

        # Re‑initialise pygame surface with the new dimensions.
        if self._initialized:
            self.screen = pygame.display.set_mode(
                (self.window_w, self.window_h),
                pygame.NOFRAME | pygame.SRCALPHA | pygame.HWSURFACE | pygame.DOUBLEBUF,
            )
            print(
                f"[OverlayRendererAgent] Surface rebuilt: {self.window_w}x{self.window_h}, cell_px={self.cell_px}"
            )

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
        if not self._initialized:
            pygame.init()
            self._initialized = True

        clock = pygame.time.Clock()
        log.info(
            "OverlayRendererAgent rendering with auto_fit=%s, cell_px=%d",
            _AUTO_FIT,
            self.cell_px,
        )

        while not self._stop_event.is_set():
            # Early‑out if the user hid the overlay.
            if not self._visible:
                clock.tick(30)  # Default FPS when hidden
                continue

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

            self.screen.fill((0, 0, 0, 0))
            if mask is not None:
                self._draw_mask(self.screen, mask)
            if preds is not None:
                self._draw_predictions(self.screen, preds)

            pygame.display.flip()
            clock.tick(30)

        if self._initialized:
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
        cell_w = self.cell_px
        cell_h = self.cell_px
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
        font = pygame.font.SysFont("Arial", max(12, self.cell_px // 2))
        for r, c, piece in preds:
            cx = c * self.cell_px + self.cell_px // 2
            cy = r * self.cell_px + self.cell_px // 2
            colour = tuple(((hash(piece) >> shift) & 0xFF) for shift in (0, 8, 16))
            pygame.draw.circle(surface, colour, (cx, cy), self.cell_px // 3)
            label = font.render(piece, True, (255, 255, 255))
            surface.blit(label, label.get_rect(center=(cx, cy)))
