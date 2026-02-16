"""
Plugin system for Tetris Overlay.
Provides extensible architecture for prediction agents, visual effects, and game modes.
"""

from .base import BasePlugin, BasePredictionAgent, BaseVisualEffect, BaseGameMode
from .loader import PluginLoader
from .registry import PluginRegistry

# Global plugin instances
plugin_loader = PluginLoader()
plugin_registry = PluginRegistry()

__all__ = [
    'BasePlugin',
    'BasePredictionAgent', 
    'BaseVisualEffect',
    'BaseGameMode',
    'PluginLoader',
    'PluginRegistry',
    'plugin_loader',
    'plugin_registry'
]
