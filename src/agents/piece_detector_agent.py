import cv2, numpy as np
from pathlib import Path
from .base_agent import BaseAgent

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


TEMPL = Path(__file__).parent.parent / "templates"


class PieceDetectorAgent(BaseAgent):
    def __init__(self):
    @trace_calls('__init__', 'piece_detector_agent.py', 25)
        self.tmpl = {}
        for p in TEMPL.glob("*.png"):
            name = p.stem  # e.g. "I_0"
            img = cv2.imread(str(p), 0)
            _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
            self.tmpl[name] = img

    def handle(self, params):
    @trace_calls('handle', 'piece_detector_agent.py', 33)
        board = params["board"]
        big = cv2.resize(board, (200, 100), interpolation=cv2.INTER_NEAREST)
        best_score = -1
        best = None
        best_loc = None
        for n, t in self.tmpl.items():
            r = cv2.matchTemplate(big, t, cv2.TM_CCOEFF_NORMED)
            _, s, _, loc = cv2.minMaxLoc(r)
            if s > best_score:
                best_score = s
                best = n
                best_loc = loc
        if best is None:
            return {"piece": None, "orientation": None, "position": None}
        piece, rot = best.split("_")
        col = best_loc[0] // 10
        row = best_loc[1] // 10
        return {"piece": piece, "orientation": int(rot), "position": (col, row)}
