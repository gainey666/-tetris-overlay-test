"""
Hot‑key controller for the overlay.

* **F9** – toggle visibility of the ghost overlay.
* **F2** – re‑run the ROI calibration UI.
* **Esc** – request a graceful shutdown of the whole orchestrator.

The implementation uses the ``keyboard`` library which works on Windows
out‑of‑the‑box (no extra native DLLs).  It must be run from an elevated
console (or as Administrator) because ``keyboard`` installs a low‑level
hook.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
from typing import Optional
import keyboard  # pip install keyboard

log = logging.getLogger(__name__)


class HotkeyAgent:
    """
    A very small agent that registers three global hot‑keys and mutates
    shared state that the other agents read.
    """

    def __init__(self):
    @trace_calls('__init__', 'hotkey_agent.py', 33)
        # ``OverlayRendererAgent`` will query this flag on each frame.
        self.overlay_visible: bool = True
        # ``RunAgent`` (or the orchestrator) will poll for shutdown.
        self.shutdown_requested: bool = False

    # -----------------------------------------------------------------
    # Public entry point – called by the orchestrator while the pipeline
    # is running.
    # -----------------------------------------------------------------
    def handle(self, params: Optional[dict] = None) -> None:
    @trace_calls('handle', 'hotkey_agent.py', 43)
        """Start the hot-key listener."""
        self.start()

    def start(self) -> None:
    @trace_calls('start', 'hotkey_agent.py', 47)
        """Spawn a daemon thread that installs the hot‑key callbacks."""
        thread = threading.Thread(target=self._listen, daemon=True)
        thread.start()
        log.info(
            "[HotkeyAgent] listening for F1 (re-detect), F9 (toggle), F2 (calibrate), Esc (quit)"
        )

    # -----------------------------------------------------------------
    # Internal helper – runs in the background thread.
    # -----------------------------------------------------------------
    def _listen(self) -> None:
    @trace_calls('_listen', 'hotkey_agent.py', 58)
        # Register the four hot‑keys.
        keyboard.add_hotkey("F9", self._toggle_overlay)
        keyboard.add_hotkey("F2", self._run_calibration)
        keyboard.add_hotkey("F1", self._re_detect_window)
        keyboard.add_hotkey("esc", self._request_shutdown)

        # Block forever; the callbacks do the actual work.
        keyboard.wait()

    # -----------------------------------------------------------------
    # Callback implementations
    # -----------------------------------------------------------------
    def _toggle_overlay(self) -> None:
    @trace_calls('_toggle_overlay', 'hotkey_agent.py', 71)
        self.overlay_visible = not self.overlay_visible
        # The renderer is a singleton – see OverlayRendererAgent below.
        from .overlay_renderer_agent import OverlayRendererAgent

        OverlayRendererAgent.instance().set_visibility(self.overlay_visible)
        log.info(f"[HotkeyAgent] overlay visibility set to {self.overlay_visible}")

    def _run_calibration(self) -> None:
    @trace_calls('_run_calibration', 'hotkey_agent.py', 79)
        """
        Re‑run the simple screen‑capture calibration UI we wrote earlier.
        ``test_screen_capture.py`` shows the whole screen and lets the user
        draw a new ROI.  After the UI finishes it overwrites ``config.json``,
        so the next frame will be cropped correctly.
        """
        log.info("[HotkeyAgent] launching calibration UI (test_screen_capture.py)")
        # ``subprocess.run`` blocks until the script exits – that's fine.
        subprocess.run([sys.executable, "test_screen_capture.py"], cwd=os.getcwd())

    def _re_detect_window(self) -> None:
    @trace_calls('_re_detect_window', 'hotkey_agent.py', 90)
        """Re-detect the Tetris window and update ROI."""
        from ..window_filter import re_detect_window, _verify_window_with_directshow
        from .capture_agent import CaptureAgent
        from .overlay_renderer_agent import OverlayRendererAgent

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


        print("[HotkeyAgent] Re-detecting Tetris window...")

        # Try to find the window again
        win_info = re_detect_window()
        if not win_info:
            print("[HotkeyAgent] No Tetris window found - keeping current settings")
            return

        # Verify window is accessible with DirectShow
        if not _verify_window_with_directshow(win_info):
            print("[HotkeyAgent] Window verification failed - keeping current settings")
            return

        # Update the CaptureAgent's ROI
        capture = CaptureAgent()
        win_left, win_top, win_w, win_h = win_info

        # Re-calculate window-relative ROI
        capture.roi_tl = (capture._abs_tl[0] - win_left, capture._abs_tl[1] - win_top)
        capture.roi_br = (capture._abs_br[0] - win_left, capture._abs_br[1] - win_top)
        capture.roi_width = capture.roi_br[0] - capture.roi_tl[0]
        capture.roi_height = capture.roi_br[1] - capture.roi_tl[1]
        capture.roi = (*capture.roi_tl, *capture.roi_br)

        print(f"[HotkeyAgent] Window re-detected at ({win_left}, {win_top})")
        print(f"[HotkeyAgent] New ROI: {capture.roi_tl} to {capture.roi_br}")

        # Tell the overlay to rebuild with new dimensions
        try:
            overlay = OverlayRendererAgent.instance()
            overlay._rebuild_surface()
            print("[HotkeyAgent] Overlay rebuilt with new dimensions")
        except RuntimeError:
            print("[HotkeyAgent] Overlay not running - window detection updated anyway")

    def _request_shutdown(self) -> None:
    @trace_calls('_request_shutdown', 'hotkey_agent.py', 147)
        self.shutdown_requested = True
        log.info("[HotkeyAgent] shutdown requested (Esc pressed)")
