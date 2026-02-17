import json, cv2, numpy as np
from pathlib import Path
from .base_agent import BaseAgent
from .config_agent import ConfigAgent

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


CFG = Path("config.json")


class BoardExtractorAgent(BaseAgent):
    def __init__(self):
    @trace_calls('__init__', 'board_extractor_agent.py', 26)
        cfg_obj = ConfigAgent()
        cfg = cfg_obj.handle()
        if cfg and hasattr(cfg, "roi") and cfg.roi:
            self.tl = tuple(cfg.roi["tl"])
            self.br = tuple(cfg.roi["br"])
        else:
            # full frame – use image dimensions later
            self.tl = None
            self.br = None

    def _crop(self, f):
    @trace_calls('_crop', 'board_extractor_agent.py', 37)
        if self.tl is None:
            return f  # whole image
        x1, y1 = self.tl
        x2, y2 = self.br
        return f[y1:y2, x1:x2]

    def _binary(self, roi):
    @trace_calls('_binary', 'board_extractor_agent.py', 44)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([0, 30, 30]), np.array([180, 255, 255]))
        mask = cv2.morphologyEx(
            mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        )
        board = cv2.resize(mask, (20, 10), interpolation=cv2.INTER_NEAREST)
        return np.where(board > 127, 255, 0).astype(np.uint8)

    def handle(self, params):
    @trace_calls('handle', 'board_extractor_agent.py', 53)
        frame = params["frame"]
        return {"board": self._binary(self._crop(frame))}
