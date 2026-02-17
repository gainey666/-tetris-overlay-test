"""Unit tests for overlay renderer."""

import pytest
import numpy as np
import pygame
from unittest.mock import Mock, patch
from overlay_renderer import OverlayRenderer
from tetromino_shapes import get_piece_shape


class TestOverlayRenderer:
    """Test overlay rendering functionality."""
    
    @pytest.fixture
    def renderer(self):
        """Create a test overlay renderer."""
        # Mock pygame to avoid actual window creation
        with patch('pygame.display.set_mode'):
            with patch('pygame.display.set_caption'):
                renderer = OverlayRenderer()
                return renderer
                
    @pytest.fixture
    def sample_board(self):
        """Create a sample game board."""
        board = np.zeros((10, 20), dtype=int)
        # Add some blocks at the bottom
        board[:, 18] = 1
        board[:, 19] = 1
        return board
        
    def test_renderer_initialization(self, renderer):
        """Test renderer initialization."""
        assert renderer.screen is not None
        assert hasattr(renderer, '_ghost_colour')
        assert isinstance(renderer._ghost_colour, tuple)
        assert len(renderer._ghost_colour) == 4  # RGBA
        
    def test_update_ghost_style(self, renderer):
        """Test updating ghost style."""
        colour = (255, 0, 0)
        opacity = 0.8
        
        renderer.update_ghost_style(colour, opacity)
        
        expected_alpha = int(opacity * 255)
        assert renderer._ghost_colour == (*colour, expected_alpha)
        
    def test_toggle_visibility(self, renderer):
        """Test overlay visibility toggle."""
        initial_state = renderer.visible
        renderer.toggle()
        assert renderer.visible != initial_state
        renderer.toggle()
        assert renderer.visible == initial_state
        
    def test_find_landing_position(self, renderer, sample_board):
        """Test finding landing position for pieces."""
        # Test T piece
        t_shape = get_piece_shape("T", 0)
        landing_y = renderer._find_landing_position(sample_board, t_shape)
        
        # Should land above the bottom blocks
        assert landing_y == 16  # Two rows above bottom (rows 18,19 are filled)
        
    def test_find_landing_position_empty_board(self, renderer):
        """Test landing position on empty board."""
        empty_board = np.zeros((10, 20), dtype=int)
        t_shape = get_piece_shape("T", 0)
        
        landing_y = renderer._find_landing_position(empty_board, t_shape)
        
        # Should land at the bottom
        assert landing_y == 18  # Just above bottom row
        
    def test_find_landing_position_full_board(self, renderer):
        """Test landing position on full board."""
        full_board = np.ones((10, 20), dtype=int)
        t_shape = get_piece_shape("T", 0)
        
        landing_y = renderer._find_landing_position(full_board, t_shape)
        
        # Should land at the top
        assert landing_y == -1  # Can't place anywhere
        
    @patch('pygame.display.flip')
    def test_draw_ghost_not_visible(self, mock_flip, renderer, sample_board):
        """Test that drawing does nothing when overlay is not visible."""
        renderer.visible = False
        
        renderer.draw_ghost(sample_board, "T", 0)
        
        # Should not call flip when not visible
        mock_flip.assert_not_called()
        
    @patch('pygame.display.flip')
    @patch('pygame.Surface')
    def test_draw_tetromino_ghost(self, mock_surface, mock_flip, renderer):
        """Test drawing tetromino ghost piece."""
        renderer.visible = True
        
        # Mock settings
        with patch('ui.current_settings.get') as mock_get:
            mock_settings = Mock()
            mock_settings.show_combo = False
            mock_settings.show_b2b = False
            mock_settings.show_fps = False
            mock_settings.ghost.outline_only = False
            mock_get.return_value = mock_settings
            
            shape = [(4, 0), (3, 1), (4, 1), (5, 1)]
            landing_y = 10
            
            renderer._draw_tetromino_ghost(shape, landing_y)
            
            # Should create surface for ghost
            mock_surface.assert_called()
            
    def test_draw_combo_indicator(self, renderer):
        """Test drawing combo indicator."""
        with patch('pygame.font.Font') as mock_font:
            mock_font_instance = Mock()
            mock_font.return_value = mock_font_instance
            mock_font_instance.render.return_value = Mock()
            
            renderer._draw_combo_indicator(5)
            
            # Should render combo text
            mock_font_instance.render.assert_called_with("COMBO x5", True, (255, 255, 0))
            
    def test_draw_b2b_indicator(self, renderer):
        """Test drawing B2B indicator."""
        with patch('pygame.font.Font') as mock_font:
            mock_font_instance = Mock()
            mock_font.return_value = mock_font_instance
            mock_font_instance.render.return_value = Mock()
            
            renderer._draw_b2b_indicator()
            
            # Should render B2B text
            mock_font_instance.render.assert_called_with("B2B", True, (255, 0, 255))
            
    def test_draw_fps_counter(self, renderer):
        """Test drawing FPS counter."""
        with patch('pygame.font.Font') as mock_font:
            mock_font_instance = Mock()
            mock_font.return_value = mock_font_instance
            mock_font_instance.render.return_value = Mock()
            
            renderer._current_fps = 45.5
            renderer._draw_fps_counter()
            
            # Should render FPS text
            mock_font_instance.render.assert_called_with("FPS: 45.5", True, (0, 255, 0))
            
    def test_draw_ghost_all_pieces(self, renderer, sample_board):
        """Test drawing ghost for all piece types."""
        renderer.visible = True
        
        # Mock settings and pygame
        with patch('ui.current_settings.get') as mock_get:
            mock_settings = Mock()
            mock_settings.show_combo = False
            mock_settings.show_b2b = False
            mock_settings.show_fps = False
            mock_get.return_value = mock_settings
            
            with patch('pygame.display.flip'):
                pieces = ["I", "O", "T", "S", "Z", "J", "L"]
                
                for piece in pieces:
                    # Should not raise any exceptions
                    renderer.draw_ghost(sample_board, piece, 0)
                    
    def test_draw_ghost_invalid_piece(self, renderer, sample_board):
        """Test drawing ghost with invalid piece type."""
        renderer.visible = True
        
        # Mock settings and pygame
        with patch('ui.current_settings.get') as mock_get:
            mock_settings = Mock()
            mock_settings.show_combo = False
            mock_settings.show_b2b = False
            mock_settings.show_fps = False
            mock_get.return_value = mock_settings
            
            with patch('pygame.display.flip'):
                # Should not crash with invalid piece
                renderer.draw_ghost(sample_board, "X", 0)
                
    def test_performance_monitoring(self, renderer):
        """Test performance monitoring functionality."""
        # Create a mock surface
        mock_surface = Mock()
        mock_surface.get_width.return_value = 640
        mock_surface.get_height.return_value = 480
        
        # Test good performance
        renderer.draw_performance_overlay(mock_surface, 60.0, 15.0)
        
        # Test poor performance
        renderer.draw_performance_overlay(mock_surface, 20.0, 50.0)
        
        # Should not raise any exceptions
