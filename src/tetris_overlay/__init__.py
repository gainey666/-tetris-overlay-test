"""
Tetris Overlay - A real-time ghost piece overlay for Tetris games.
"""

__version__ = "0.1.0"
__author__ = "Tetris Overlay Team"

from .core.config import OverlayConfig
from .core.overlay import GhostOverlay


__all__ = ["OverlayConfig", "GhostOverlay"]
