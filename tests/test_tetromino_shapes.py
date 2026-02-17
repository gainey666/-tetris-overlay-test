"""Unit tests for tetromino shapes module."""

import pytest
from tetromino_shapes import (
    get_piece_shape, get_piece_color, get_all_piece_types,
    validate_piece_type, normalize_rotation, PieceType
)

class TestTetrominoShapes:
    """Test tetromino shape and color functions."""
    
    def test_get_piece_shape_valid(self):
        """Test getting shapes for valid pieces."""
        # Test T piece
        t_shape = get_piece_shape("T", 0)
        assert isinstance(t_shape, list)
        assert len(t_shape) == 4  # T piece has 4 cells
        assert all(isinstance(coord, tuple) and len(coord) == 2 for coord in t_shape)
        
        # Test I piece
        i_shape = get_piece_shape("I", 0)
        assert len(i_shape) == 4  # I piece has 4 cells
        
        # Test O piece
        o_shape = get_piece_shape("O", 0)
        assert len(o_shape) == 4  # O piece has 4 cells
        
    def test_get_piece_shape_rotations(self):
        """Test piece rotations."""
        # Test T piece rotations
        t_rot0 = get_piece_shape("T", 0)
        t_rot1 = get_piece_shape("T", 1)
        t_rot2 = get_piece_shape("T", 2)
        t_rot3 = get_piece_shape("T", 3)
        
        # All rotations should have 4 cells
        assert len(t_rot0) == len(t_rot1) == len(t_rot2) == len(t_rot3) == 4
        
        # Rotations should be different (except for symmetric pieces)
        assert t_rot0 != t_rot1 or t_rot1 != t_rot2
        
    def test_get_piece_shape_invalid(self):
        """Test getting shape for invalid piece type."""
        # Invalid piece should default to T piece
        invalid_shape = get_piece_shape("X", 0)
        t_shape = get_piece_shape("T", 0)
        assert invalid_shape == t_shape
        
    def test_get_piece_color_valid(self):
        """Test getting colors for valid pieces."""
        # Test known colors
        assert get_piece_color("I") == (0, 240, 240)  # Cyan
        assert get_piece_color("O") == (240, 240, 0)  # Yellow
        assert get_piece_color("T") == (160, 0, 240)  # Purple
        
        # All colors should be RGB tuples
        for piece_type in get_all_piece_types():
            color = get_piece_color(piece_type)
            assert isinstance(color, tuple)
            assert len(color) == 3
            assert all(0 <= c <= 255 for c in color)
            
    def test_get_piece_color_invalid(self):
        """Test getting color for invalid piece type."""
        # Invalid piece should default to T piece color
        invalid_color = get_piece_color("X")
        t_color = get_piece_color("T")
        assert invalid_color == t_color
        
    def test_get_all_piece_types(self):
        """Test getting all piece types."""
        pieces = get_all_piece_types()
        assert isinstance(pieces, list)
        assert len(pieces) == 7  # Standard Tetris has 7 pieces
        assert "I" in pieces
        assert "O" in pieces
        assert "T" in pieces
        assert "S" in pieces
        assert "Z" in pieces
        assert "J" in pieces
        assert "L" in pieces
        
    def test_validate_piece_type(self):
        """Test piece type validation."""
        # Valid pieces
        assert validate_piece_type("I") is True
        assert validate_piece_type("O") is True
        assert validate_piece_type("T") is True
        
        # Invalid pieces
        assert validate_piece_type("X") is False
        assert validate_piece_type("") is False
        assert validate_piece_type("ABC") is False
        
        # Case insensitive
        assert validate_piece_type("i") is True
        assert validate_piece_type("t") is True
        
    def test_normalize_rotation(self):
        """Test rotation normalization."""
        assert normalize_rotation(0) == 0
        assert normalize_rotation(1) == 1
        assert normalize_rotation(2) == 2
        assert normalize_rotation(3) == 3
        assert normalize_rotation(4) == 0
        assert normalize_rotation(5) == 1
        assert normalize_rotation(7) == 3
        assert normalize_rotation(8) == 0
        assert normalize_rotation(-1) == 3
        assert normalize_rotation(-2) == 2
        
    def test_piece_shape_coordinates(self):
        """Test that piece shapes have valid coordinates."""
        for piece_type in get_all_piece_types():
            for rotation in range(4):
                shape = get_piece_shape(piece_type, rotation)
                
                # All coordinates should be within reasonable bounds
                for x, y in shape:
                    assert 1 <= x <= 4  # Standard 4x4 grid
                    assert 1 <= y <= 4
                    
    def test_o_piece_symmetry(self):
        """Test that O piece is symmetric (all rotations same)."""
        o_rot0 = get_piece_shape("O", 0)
        o_rot1 = get_piece_shape("O", 1)
        o_rot2 = get_piece_shape("O", 2)
        o_rot3 = get_piece_shape("O", 3)
        
        assert o_rot0 == o_rot1 == o_rot2 == o_rot3
        
    def test_i_piece_symmetry(self):
        """Test I piece symmetry (rotations 0&2 same, 1&3 same)."""
        i_rot0 = get_piece_shape("I", 0)
        i_rot1 = get_piece_shape("I", 1)
        i_rot2 = get_piece_shape("I", 2)
        i_rot3 = get_piece_shape("I", 3)
        
        assert i_rot0 == i_rot2  # Horizontal
        assert i_rot1 == i_rot3  # Vertical
        assert i_rot0 != i_rot1  # Different orientations
