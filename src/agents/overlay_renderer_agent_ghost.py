import pygame, numpy as np
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



class OverlayRendererAgent(BaseAgent):
    def __init__(self):
    @trace_calls('__init__', 'overlay_renderer_agent_ghost.py', 23)
        cfg = ConfigAgent.config or ConfigAgent()
        self.scale = getattr(cfg, "overlay_scale", 30)
        self.board_w, self.board_h = 20, 10
        self.window = None

    def _init_window(self):
    @trace_calls('_init_window', 'overlay_renderer_agent_ghost.py', 29)
        pygame.init()
        w = self.board_w * int(self.scale)
        h = self.board_h * int(self.scale)
        self.window = pygame.display.set_mode((w, h), pygame.NOFRAME)
        pygame.display.set_caption("Tetris Ghost")

    def handle(self, params):
    @trace_calls('handle', 'overlay_renderer_agent_ghost.py', 36)
        if not self.window:
            self._init_window()
        pred = params["prediction"]
        piece = params["piece"]
        rot = params["orientation"]
        col = pred["target_col"]
        # Simple ghost: draw 4 blocks at predicted column
        block_color = (0, 255, 0, 120)  # semi‑transparent green
        for x in range(4):
            rect = pygame.Rect(
                (col + x) * self.scale, 0 * self.scale, self.scale, self.scale
            )
            s = pygame.Surface((self.scale, self.scale), pygame.SRCALPHA)
            s.fill(block_color)
            self.window.blit(s, rect.topleft)

        pygame.display.flip()
