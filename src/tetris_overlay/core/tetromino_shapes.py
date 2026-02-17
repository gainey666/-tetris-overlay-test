"""
Tetromino shapes and colors for Tetris overlay.
"""

from typing import List, Tuple
import numpy as np

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


# Tetromino shapes as (x, y) coordinates
TETROMINO_SHAPES = {
    'I': [
        [(0, 0), (1, 0), (2, 0), (3, 0)],  # Horizontal
        [(0, 0), (0, 1), (0, 2), (0, 3)],  # Vertical
    ],
    'O': [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
    ],
    'T': [
        [(1, 0), (0, 1), (1, 1), (2, 1)],  # T-down
        [(0, 0), (1, 0), (2, 0), (1, 1)],  # T-up
        [(1, 0), (0, 1), (1, 1), (1, 2)],  # T-left
        [(1, 0), (1, 1), (2, 1), (1, 2)],  # T-right
    ],
    'S': [
        [(1, 0), (2, 0), (0, 1), (1, 1)],  # S-horizontal
        [(1, 0), (0, 1), (1, 1), (0, 2)],  # S-vertical
    ],
    'Z': [
        [(0, 0), (1, 0), (1, 1), (2, 1)],  # Z-horizontal
        [(2, 0), (1, 1), (2, 1), (1, 2)],  # Z-vertical
    ],
    'J': [
        [(0, 0), (0, 1), (1, 1), (2, 1)],  # J-down
        [(0, 0), (1, 0), (2, 0), (2, 1)],  # J-right
        [(0, 0), (0, 1), (0, 2), (1, 2)],  # J-up
        [(0, 0), (1, 0), (0, 1), (0, 2)],  # J-left
    ],
    'L': [
        [(2, 0), (0, 1), (1, 1), (2, 1)],  # L-down
        [(0, 0), (1, 0), (2, 0), (0, 1)],  # L-right
        [(0, 0), (0, 1), (0, 2), (1, 2)],  # L-up
        [(2, 0), (1, 0), (2, 1), (2, 2)],  # L-left
    ]
}

# Standard Tetris colors (RGB)
TETROMINO_COLORS = {
    'I': (0, 255, 255),    # Cyan
    'O': (255, 255, 0),    # Yellow
    'T': (128, 0, 128),    # Purple
    'S': (0, 255, 0),      # Green
    'Z': (255, 0, 0),      # Red
    'J': (0, 0, 255),      # Blue
    'L': (255, 165, 0),    # Orange
}

def get_piece_shape(piece_type: str, rotation: int = 0) -> List[Tuple[int, int]]:
@trace_calls('get_piece_shape', 'tetromino_shapes.py', 72)
    """Get the shape of a tetromino piece."""
    if piece_type not in TETROMINO_SHAPES:
        raise ValueError(f"Unknown piece type: {piece_type}")
    
    shapes = TETROMINO_SHAPES[piece_type]
    if rotation < 0 or rotation >= len(shapes):
        raise ValueError(f"Invalid rotation {rotation} for piece {piece_type}")
    
    return shapes[rotation]

def get_piece_color(piece_type: str) -> Tuple[int, int, int]:
@trace_calls('get_piece_color', 'tetromino_shapes.py', 83)
    """Get the color of a tetromino piece."""
    if piece_type not in TETROMINO_COLORS:
        raise ValueError(f"Unknown piece type: {piece_type}")
    
    return TETROMINO_COLORS[piece_type]

def normalize_rotation(piece_type: str, rotation: int) -> int:
@trace_calls('normalize_rotation', 'tetromino_shapes.py', 90)
    """Normalize rotation to valid range."""
    shapes = TETROMINO_SHAPES[piece_type]
    return rotation % len(shapes)

def validate_piece_type(piece_type: str) -> bool:
@trace_calls('validate_piece_type', 'tetromino_shapes.py', 95)
    """Validate that a piece type exists."""
    return piece_type in TETROMINO_SHAPES
