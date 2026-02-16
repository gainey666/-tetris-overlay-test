import logging
from typing import Optional

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CaptureAgent(BaseAgent):
    """Simple wrapper for ScreenCapture functionality."""

    def __init__(self):
        super().__init__()
        self.frame_queue = None
        self.rect = (0, 0, 0, 0)
        self._roi_width = 0
        self._roi_height = 0
        self.roi_width = self.rect[2]
        self.roi_height = self.rect[3]

    def start(self):
        """Start capture – placeholder for dual-ROI system."""
        logger.info("CaptureAgent started (dual-ROI mode)")

    def stop(self):
        """Stop capture."""
        logger.info("CaptureAgent stopped")

    def handle(self, params: Optional[dict] = None):
        """Handle a capture request."""
        self.start()

    @property
    def roi_width(self):
        return self._roi_width

    @roi_width.setter
    def roi_width(self, value):
        self._roi_width = int(value) if value is not None else 0

    @property
    def roi_height(self):
        return self._roi_height

    @roi_height.setter
    def roi_height(self, value):
        self._roi_height = int(value) if value is not None else 0
