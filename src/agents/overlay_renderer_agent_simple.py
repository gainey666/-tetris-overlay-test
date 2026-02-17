import sys
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



class OverlayRendererAgentSimple(BaseAgent):
    def __init__(self):
    @trace_calls('__init__', 'overlay_renderer_agent_simple.py', 23)
        cfg = ConfigAgent.config or ConfigAgent()
        self.use_overlay = getattr(cfg, "use_overlay", False)

    def handle(self, params):
    @trace_calls('handle', 'overlay_renderer_agent_simple.py', 27)
        pred = params.get("prediction")
        piece = params.get("piece", "Unknown")
        if not pred:
            print("[Overlay] No prediction available")
            return
        if not self.use_overlay:
            print(
                f"[Ghost] {piece} → col {pred['target_col']} rot {pred['target_rot']}"
            )
            return
        # existing pygame overlay code (unchanged) …
