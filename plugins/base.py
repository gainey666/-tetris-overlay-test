"""
Base classes for plugin system.
Defines interfaces for prediction agents, visual effects, and game modes.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum

class PluginType(Enum):
    """Types of plugins."""
    PREDICTION_AGENT = "prediction_agent"
    VISUAL_EFFECT = "visual_effect"
    GAME_MODE = "game_mode"
    UTILITY = "utility"

@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str]
    min_overlay_version: str
    max_overlay_version: Optional[str] = None
    tags: List[str] = None
    homepage: Optional[str] = None
    license: str = "MIT"

class BasePlugin(ABC):
    """Base class for all plugins."""
    
    def __init__(self):
        self.enabled = False
        self.config = {}
        
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Plugin metadata."""
        pass
        
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration."""
        pass
        
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass
        
    def enable(self) -> bool:
        """Enable the plugin."""
        if not self.enabled:
            if self.initialize(self.config):
                self.enabled = True
                return True
        return False
        
    def disable(self) -> None:
        """Disable the plugin."""
        if self.enabled:
            self.cleanup()
            self.enabled = False
            
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for this plugin."""
        return {}

class BasePredictionAgent(BasePlugin):
    """Base class for prediction agent plugins."""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.PREDICTION_AGENT
        
    @abstractmethod
    def predict(self, board: np.ndarray, piece_type: str, next_queue: List[str], 
                rotation: int = 0) -> Tuple[int, int]:
        """
        Predict the best position for the current piece.
        
        Args:
            board: 10x20 numpy array representing the game board
            piece_type: Current piece type ('I', 'O', 'T', 'S', 'Z', 'J', 'L')
            next_queue: List of upcoming pieces
            rotation: Current rotation state (0-3)
            
        Returns:
            Tuple of (x_position, y_position) for optimal placement
        """
        pass
        
    @abstractmethod
    def get_confidence(self) -> float:
        """Get confidence score for the prediction (0.0-1.0)."""
        pass
        
    def analyze_board(self, board: np.ndarray) -> Dict[str, Any]:
        """Analyze board state and return metrics."""
        return {
            'height': np.sum(board > 0, axis=1).max(),
            'holes': self._count_holes(board),
            'bumpiness': self._calculate_bumpiness(board),
            'lines_cleared': 0
        }
        
    def _count_holes(self, board: np.ndarray) -> int:
        """Count holes in the board."""
        holes = 0
        for x in range(10):
            found_block = False
            for y in range(20):
                if board[x, y] > 0:
                    found_block = True
                elif found_block and board[x, y] == 0:
                    holes += 1
        return holes
        
    def _calculate_bumpiness(self, board: np.ndarray) -> float:
        """Calculate board bumpiness."""
        heights = []
        for x in range(10):
            column_height = 20 - np.argmax(board[x, :] > 0) if np.any(board[x, :] > 0) else 0
            heights.append(column_height)
        
        bumpiness = 0
        for i in range(len(heights) - 1):
            bumpiness += abs(heights[i] - heights[i + 1])
        return bumpiness

class BaseVisualEffect(BasePlugin):
    """Base class for visual effect plugins."""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.VISUAL_EFFECT
        
    @abstractmethod
    def render(self, surface: Any, frame_data: Dict[str, Any]) -> None:
        """
        Render the visual effect on the given surface.
        
        Args:
            surface: Pygame surface to render on
            frame_data: Dictionary containing frame information
        """
        pass
        
    @abstractmethod
    def get_render_order(self) -> int:
        """Get render order (lower numbers render first)."""
        pass
        
    def is_enabled_for_frame(self, frame_data: Dict[str, Any]) -> bool:
        """Check if effect should be rendered for this frame."""
        return self.enabled

class BaseGameMode(BasePlugin):
    """Base class for game mode plugins."""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.GAME_MODE
        
    @abstractmethod
    def get_board_dimensions(self) -> Tuple[int, int]:
        """Get board dimensions (width, height)."""
        pass
        
    @abstractmethod
    def get_piece_types(self) -> List[str]:
        """Get list of valid piece types for this game mode."""
        pass
        
    @abstractmethod
    def validate_move(self, board: np.ndarray, piece_type: str, 
                      position: Tuple[int, int], rotation: int) -> bool:
        """Validate if a move is legal in this game mode."""
        pass
        
    @abstractmethod
    def calculate_score(self, board: np.ndarray, lines_cleared: int, 
                        piece_type: str, is_tspin: bool, is_b2b: bool) -> int:
        """Calculate score for a move in this game mode."""
        pass
        
    def get_special_rules(self) -> Dict[str, Any]:
        """Get special rules for this game mode."""
        return {}

class MultiPlayerSupport(BasePlugin):
    """Plugin for multi-player support."""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.UTILITY
        
    def __init__(self):
        super().__init__()
        self.active_players = {}
        self.max_players = 4
        
    def add_player(self, player_id: str, window_info: Dict[str, Any]) -> bool:
        """Add a new player."""
        if len(self.active_players) >= self.max_players:
            return False
            
        self.active_players[player_id] = {
            'window_info': window_info,
            'board': np.zeros((10, 20), dtype=int),
            'score': 0,
            'lines': 0
        }
        return True
        
    def remove_player(self, player_id: str) -> bool:
        """Remove a player."""
        if player_id in self.active_players:
            del self.active_players[player_id]
            return True
        return False
        
    def update_player_board(self, player_id: str, board: np.ndarray) -> bool:
        """Update player's board state."""
        if player_id in self.active_players:
            self.active_players[player_id]['board'] = board.copy()
            return True
        return False
        
    def get_all_boards(self) -> Dict[str, np.ndarray]:
        """Get all player boards."""
        return {pid: data['board'] for pid, data in self.active_players.items()}

class WebInterface(BasePlugin):
    """Plugin for web-based interface and streaming."""
    
    @property
    def plugin_type(self) -> PluginType:
        return PluginType.UTILITY
        
    def __init__(self):
        super().__init__()
        self.websocket_server = None
        self.stream_enabled = False
        
    def start_websocket_server(self, host: str = "localhost", port: int = 8765) -> bool:
        """Start WebSocket server for real-time data streaming."""
        try:
            # This would implement actual WebSocket server
            # For now, just return success
            self.stream_enabled = True
            return True
        except Exception as e:
            print(f"Failed to start WebSocket server: {e}")
            return False
            
    def stream_frame_data(self, frame_data: Dict[str, Any]) -> None:
        """Stream frame data to connected clients."""
        if self.stream_enabled and self.websocket_server:
            # This would actually stream the data
            pass
            
    def get_web_interface_url(self) -> str:
        """Get URL for web interface."""
        return "http://localhost:8765"

# Utility functions for plugin development
def create_plugin_metadata(name: str, version: str, description: str, 
                          author: str, plugin_type: PluginType,
                          dependencies: List[str] = None,
                          min_overlay_version: str = "2.0.0",
                          **kwargs) -> PluginMetadata:
    """Helper function to create plugin metadata."""
    return PluginMetadata(
        name=name,
        version=version,
        description=description,
        author=author,
        plugin_type=plugin_type,
        dependencies=dependencies or [],
        min_overlay_version=min_overlay_version,
        **kwargs
    )
