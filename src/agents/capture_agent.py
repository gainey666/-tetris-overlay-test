"""Capture frames from a webcam or video file using OpenCV."""
from __future__ import annotations

import os
import sys
import queue
import threading
import time
import cv2
from .base_agent import BaseAgent
from .config_agent import ConfigAgent

# ---- try to import native DXGI module ------------------------------------
try:
    import dxgi_capture
    _dxgi_available = True
except ImportError:
    _dxgi_available = False

class CaptureAgent(BaseAgent):
    """Capture frames – DXGI if available & enabled, else OpenCV."""
    def __init__(self, source: int = 0, use_dxgi: bool | None = None):
        cfg = ConfigAgent.config
        if cfg is None:
            cfg = ConfigAgent()
            cfg = cfg.handle() or cfg
        # decide whether to use DXGI
        self.use_dxgi = (use_dxgi if use_dxgi is not None else cfg.use_dxgi) and _dxgi_available
        if self.use_dxgi:
            # expose FPS & pool size to the C++ side via env vars
            os.environ["DXGI_TARGET_FPS"] = str(cfg.dxgi_target_fps)
            os.environ["DXGI_POOL_SIZE"]  = str(cfg.dxgi_pool_size)
            self.grabber = dxgi_capture.FrameGrabber()
            if not self.grabber.initialize():
                self.use_dxgi = False
                print("⚠️ DXGI init failed – falling back to OpenCV")
        else:
            self.source = source
            self.cap = None

        self.frame_queue: queue.Queue = queue.Queue(maxsize=10)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def handle(self, params: dict | None = None) -> None:
        """Start/stop capture based on orchestrator request."""
        if params and params.get("stop"):
            self.stop()
        else:
            self.start()

    def _run(self) -> None:
        if self.use_dxgi:
            while not self._stop_event.is_set():
                frame = self.grabber.grab()
                if not frame.empty():
                    try:
                        self.frame_queue.put(frame, timeout=0.1)
                    except queue.Full:
                        try:
                            _ = self.frame_queue.get_nowait()
                            self.frame_queue.put_nowait(frame)
                        except queue.Empty:
                            pass
                else:
                    # DXGI may have returned an empty frame; sleep a bit
                    time.sleep(0.008)
        else:
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                raise RuntimeError("Unable to open video source")
            while not self._stop_event.is_set():
                ret, frame = self.cap.read()
                if not ret:
                    break
                try:
                    self.frame_queue.put(frame, timeout=0.1)
                except queue.Full:
                    try:
                        _ = self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait(frame)
                    except queue.Empty:
                        pass

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        if getattr(self, "cap", None):
            self.cap.release()
