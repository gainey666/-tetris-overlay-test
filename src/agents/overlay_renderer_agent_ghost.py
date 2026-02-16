import pygame, numpy as np
from .base_agent import BaseAgent
from .config_agent import ConfigAgent


class OverlayRendererAgent(BaseAgent):
    def __init__(self):
        cfg = ConfigAgent.config or ConfigAgent()
        self.scale = getattr(cfg, "overlay_scale", 30)
        self.board_w, self.board_h = 20, 10
        self.window = None

    def _init_window(self):
        pygame.init()
        w = self.board_w * int(self.scale)
        h = self.board_h * int(self.scale)
        self.window = pygame.display.set_mode((w, h), pygame.NOFRAME)
        pygame.display.set_caption("Tetris Ghost")

    def handle(self, params):
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
