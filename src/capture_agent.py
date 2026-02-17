import logging
from typing import Optional

from src.agents.base_agent import BaseAgent

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

logger = logging.getLogger(__name__)


class CaptureAgent(BaseAgent):
    """Simple wrapper for ScreenCapture functionality."""

    def __init__(self):
    @trace_calls('__init__', 'capture_agent.py', 27)
        super().__init__()
        self.frame_queue = None
        self.rect = (0, 0, 0, 0)
        self._roi_width = 0
        self._roi_height = 0
        self.roi_width = self.rect[2]
        self.roi_height = self.rect[3]
        
        if LOGGER_AVAILABLE:
            log.log_info("CaptureAgent", "CaptureAgent initialized")

    def start(self):
    @trace_calls('start', 'capture_agent.py', 39)
        """Start capture – placeholder for dual-ROI system."""
        logger.info("CaptureAgent started (dual-ROI mode)")
        if LOGGER_AVAILABLE:
            log.log_success("CaptureAgent", "Capture started successfully")

    def stop(self):
    @trace_calls('stop', 'capture_agent.py', 45)
        """Stop capture."""
        logger.info("CaptureAgent stopped")
        if LOGGER_AVAILABLE:
            log.log_info("CaptureAgent", "Capture stopped")

    def handle(self, params: Optional[dict] = None):
    @trace_calls('handle', 'capture_agent.py', 51)
        """Handle a capture request."""
        if LOGGER_AVAILABLE:
            log.log_info("CaptureAgent", "Handling capture request")
        self.start()

    @property
    def roi_width(self):
    @trace_calls('roi_width', 'capture_agent.py', 58)
        return self._roi_width

    @roi_width.setter
    def roi_width(self, value):
    @trace_calls('roi_width', 'capture_agent.py', 62)
        self._roi_width = int(value) if value is not None else 0

    @property
    def roi_height(self):
    @trace_calls('roi_height', 'capture_agent.py', 66)
        return self._roi_height

    @roi_height.setter
    def roi_height(self, value):
    @trace_calls('roi_height', 'capture_agent.py', 70)
        self._roi_height = int(value) if value is not None else 0
