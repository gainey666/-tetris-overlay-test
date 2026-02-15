import sys
from .base_agent import BaseAgent
from .config_agent import ConfigAgent

class OverlayRendererAgentSimple(BaseAgent):
    def __init__(self):
        cfg=ConfigAgent.config or ConfigAgent()
        self.use_overlay=getattr(cfg,"use_overlay",False)

    def handle(self,params):
        pred = params.get("prediction")
        piece = params.get("piece", "Unknown")
        if not pred:
            print("[Overlay] No prediction available")
            return
        if not self.use_overlay:
            print(f"[Ghost] {piece} → col {pred['target_col']} rot {pred['target_rot']}")
            return
        # existing pygame overlay code (unchanged) …
