"""
Tetromino shapes and rotations for ghost rendering.
Provides standard Tetris piece definitions with all possible rotations.
"""

from typing import List, Tuple, Dict
from enum import Enum

class PieceType(Enum):
    I = "I"
    O = "O"
    T = "T"
    S = "S"
    Z = "Z"
    J = "J"
    L = "L"

# Standard Tetris piece shapes (4x4 grid, 1 = filled cell)
PIECE_SHAPES: Dict[PieceType, List[List[Tuple[int, int]]]] = {
    PieceType.I: [
        [(1,0), (2,0), (3,0), (4,0)],  # Horizontal
        [(2,1), (2,2), (2,3), (2,4)],  # Vertical
        [(1,0), (2,0), (3,0), (4,0)],  # Horizontal (same as 0)
        [(2,1), (2,2), (2,3), (2,4)],  # Vertical (same as 1)
    ],
    PieceType.O: [
        [(1,1), (2,1), (1,2), (2,2)],  # Square (only one rotation)
        [(1,1), (2,1), (1,2), (2,2)],  # Same
        [(1,1), (2,1), (1,2), (2,2)],  # Same
        [(1,1), (2,1), (1,2), (2,2)],  # Same
    ],
    PieceType.T: [
        [(2,1), (1,2), (2,2), (3,2)],  # T up
        [(2,1), (2,2), (3,2), (2,3)],  # T right
        [(1,2), (2,2), (3,2), (2,3)],  # T down
        [(2,1), (1,2), (2,2), (2,3)],  # T left
    ],
    PieceType.S: [
        [(2,1), (3,1), (1,2), (2,2)],  # S horizontal
        [(2,1), (2,2), (3,2), (3,3)],  # S vertical
        [(2,1), (3,1), (1,2), (2,2)],  # Same as 0
        [(2,1), (2,2), (3,2), (3,3)],  # Same as 1
    ],
    PieceType.Z: [
        [(1,1), (2,1), (2,2), (3,2)],  # Z horizontal
        [(3,1), (2,2), (3,2), (2,3)],  # Z vertical
        [(1,1), (2,1), (2,2), (3,2)],  # Same as 0
        [(3,1), (2,2), (3,2), (2,3)],  # Same as 1
    ],
    PieceType.J: [
        [(1,1), (1,2), (2,2), (3,2)],  # J up
        [(2,1), (3,1), (2,2), (2,3)],  # J right
        [(1,2), (2,2), (3,2), (3,3)],  # J down
        [(2,1), (2,2), (1,3), (2,3)],  # J left
    ],
    PieceType.L: [
        [(3,1), (1,2), (2,2), (3,2)],  # L up
        [(2,1), (2,2), (2,3), (3,3)],  # L right
        [(1,2), (2,2), (3,2), (1,3)],  # L down
        [(1,1), (2,1), (2,2), (2,3)],  # L left
    ],
}

# Standard Tetris colors (RGB)
PIECE_COLORS: Dict[PieceType, Tuple[int, int, int]] = {
    PieceType.I: (0, 240, 240),    # Cyan
    PieceType.O: (240, 240, 0),    # Yellow
    PieceType.T: (160, 0, 240),    # Purple
    PieceType.S: (0, 240, 0),      # Green
    PieceType.Z: (240, 0, 0),      # Red
    PieceType.J: (0, 0, 240),      # Blue
    PieceType.L: (240, 160, 0),    # Orange
}

def get_piece_shape(piece_type: str, rotation: int = 0) -> List[Tuple[int, int]]:
    """Get the shape coordinates for a tetromino piece.
    
    Args:
        piece_type: Piece type as string ('I', 'O', 'T', 'S', 'Z', 'J', 'L')
        rotation: Rotation state (0-3)
        
    Returns:
        List of (x, y) coordinates for the piece shape
    """
    try:
        piece_enum = PieceType(piece_type.upper())
        shapes = PIECE_SHAPES[piece_enum]
        return shapes[rotation % 4]
    except (ValueError, KeyError):
        # Default to T piece if invalid type
        return PIECE_SHAPES[PieceType.T][rotation % 4]

def get_piece_color(piece_type: str) -> Tuple[int, int, int]:
    """Get the standard color for a tetromino piece.
    
    Args:
        piece_type: Piece type as string ('I', 'O', 'T', 'S', 'Z', 'J', 'L')
        
    Returns:
        RGB color tuple
    """
    try:
        piece_enum = PieceType(piece_type.upper())
        return PIECE_COLORS[piece_enum]
    except (ValueError, KeyError):
        # Default to purple (T piece color)
        return (160, 0, 240)

def get_all_piece_types() -> List[str]:
    """Get list of all valid piece type strings."""
    return [piece.value for piece in PieceType]

def validate_piece_type(piece_type: str) -> bool:
    """Check if a piece type string is valid."""
    return piece_type.upper() in get_all_piece_types()

def normalize_rotation(rotation: int) -> int:
    """Normalize rotation to 0-3 range."""
    return rotation % 4
