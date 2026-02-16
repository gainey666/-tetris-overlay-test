import logging
import pygame
import numpy as np
from typing import Tuple, Optional, List
from tetromino_shapes import get_piece_shape, get_piece_color
from ui.current_settings import get

from tetris_overlay_core import window_filter, ScreenCapture
from window_manager import load_cache

pygame.init()

# Tetromino shapes (same as in prediction_agent_dellacherie.py)
PIECE_SHAPES = {
    "I": [
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [(0, 0), (0, 1), (0, 2), (0, 3)],
    ],
    "O": [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
        [(0, 0), (1, 0), (2, 0), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 0), (1, 0), (2, 0), (2, 1)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 0), (1, 0), (2, 0), (0, 1)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}


class OverlayRenderer:
    def __init__(self):
        flags = pygame.NOFRAME | pygame.SRCALPHA
        self.screen = pygame.display.set_mode((640, 480), flags)
        self.visible = False
        pygame.display.set_caption("Tetris Overlay")
        
        # Default ghost style - will be overwritten by settings
        self._ghost_colour = (255, 255, 255, 128)  # RGBA
        logging.info("Overlay renderer for Tetris ghost pieces.")

    def update_counters(self, combo=0, b2b=False):
        """Update combo and B2B counters for display."""
        self.combo_counter = combo
        self.b2b_counter = self.b2b_counter + 1 if b2b else 0

    def update_ghost_style(self, colour: tuple[int, int, int], opacity: float):
        """Update ghost piece colour and opacity."""
        self._ghost_colour = (*colour, int(opacity * 255))

    def draw_stats(self, surface):
        """Draw combo and B2B stats on the overlay."""
        if self.combo_counter > 1 or self.b2b_counter > 0:
            font = pygame.font.Font(None, 24)
            
            if self.combo_counter > 1:
                combo_text = font.render(f"Combo x{self.combo_counter}", True, (0, 255, 255))
                surface.blit(combo_text, (10, 10))
            
            if self.b2b_counter > 0:
                b2b_text = font.render(f"B2B x{self.b2b_counter}", True, (255, 215, 0))
                surface.blit(b2b_text, (10, 40))

    def draw_performance(self, surface):
        """Draw FPS and performance info on the overlay."""
        from performance_monitor import performance_monitor
        
        stats = performance_monitor.get_stats()
        fps = stats['fps']
        avg_frame_time = stats['avg_frame_time'] * 1000  # Convert to ms
        
        # Choose color based on performance
        if fps >= 25:
            color = (0, 255, 0)  # Green - good
        elif fps >= 15:
            color = (255, 255, 0)  # Yellow - OK
        else:
            color = (255, 0, 0)  # Red - poor
        
        font = pygame.font.Font(None, 20)
        fps_text = font.render(f"FPS: {fps:.1f}", True, color)
        frame_text = font.render(f"Frame: {avg_frame_time:.1f}ms", True, color)
        
        # Draw in top-right corner
        surface.blit(fps_text, (surface.get_width() - 100, 10))
        surface.blit(frame_text, (surface.get_width() - 100, 30))

    def draw_ghost(self, board: np.ndarray, piece_type: str = "T", rotation: int = 0, 
                   is_tspin: bool = False, is_b2b: bool = False, combo: int = 0):
        """Draw ghost piece showing where current piece would land.
        
        Args:
            board: 10x20 numpy array representing the game board
            piece_type: Type of tetromino ('I', 'O', 'T', 'S', 'Z', 'J', 'L')
            rotation: Rotation state (0-3)
            is_tspin: Whether this is a T-spin move
            is_b2b: Whether this is a back-to-back clear
            combo: Current combo count
        """
        if not self.visible:
            return
            
        # Get current settings for visual flags
        settings = get()
        
        # Clear screen
        self.screen.fill((0, 0, 0, 0))
        
        # Get piece shape using the new tetromino_shapes module
        try:
            shape = get_piece_shape(piece_type, rotation)
        except:
            # Fallback to simple T shape if piece type invalid
            shape = [(4,0), (3,1), (4,1), (5,1)]
        
        # Find landing position (gravity simulation)
        landing_y = self._find_landing_position(board, shape)
        
        # Draw ghost piece with real tetromino shape
        self._draw_tetromino_ghost(shape, landing_y)
        
        # Draw special move indicators if enabled
        if getattr(settings, 'show_combo', True) and combo > 0:
            self._draw_combo_indicator(combo)
            
        if getattr(settings, 'show_b2b', True) and is_b2b:
            self._draw_b2b_indicator()
            
        if getattr(settings, 'show_fps', False):
            self._draw_fps_counter()
            
        # Update display
        pygame.display.flip()
        
    def _find_landing_position(self, board: np.ndarray, shape: List[Tuple[int, int]]) -> int:
        """Find the Y position where the piece would land."""
        for y in range(20):
            for px, py in shape:
                board_y = y + py
                if board_y >= 20 or (board_y >= 0 and board[px, board_y] != 0):
                    return y - 1
        return 19
        
    def _draw_tetromino_ghost(self, shape: List[Tuple[int, int]], landing_y: int):
        """Draw ghost piece with real tetromino shape."""
        cell_size = 30
        board_offset_x = 50
        board_offset_y = 50
        
        # Create surface for ghost with alpha
        ghost_surface = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
        
        # Apply visual effects based on settings
        settings = get()
        outline_only = getattr(settings.ghost, 'outline_only', False)
        
        for px, py in shape:
            x = board_offset_x + px * cell_size
            y = board_offset_y + landing_y * cell_size + py * cell_size
            
            if outline_only:
                # Draw outline only
                pygame.draw.rect(self.screen, self._ghost_colour, 
                               (x, y, cell_size, cell_size), 2)
            else:
                # Draw filled ghost with alpha
                ghost_surface.fill(self._ghost_colour)
                self.screen.blit(ghost_surface, (x, y))
                
                # Add subtle border for visibility
                border_color = (*self._ghost_colour[:3], min(255, self._ghost_colour[3] + 50))
                pygame.draw.rect(self.screen, border_color, 
                               (x, y, cell_size, cell_size), 1)
                
    def _draw_combo_indicator(self, combo: int):
        """Draw combo counter."""
        font = pygame.font.Font(None, 36)
        text = font.render(f"COMBO x{combo}", True, (255, 255, 0))
        self.screen.blit(text, (50, 10))
        
    def _draw_b2b_indicator(self):
        """Draw back-to-back indicator."""
        font = pygame.font.Font(None, 36)
        text = font.render("B2B", True, (255, 0, 255))
        self.screen.blit(text, (250, 10))
        
    def _draw_fps_counter(self):
        """Draw FPS counter."""
        # This would be updated from the frame worker
        fps = getattr(self, '_current_fps', 30)
        font = pygame.font.Font(None, 24)
        text = font.render(f"FPS: {fps:.1f}", True, (0, 255, 0))
        self.screen.blit(text, (550, 10))

    def toggle(self):
        self.visible = not self.visible
        logging.info("Overlay visibility=%s", self.visible)
        if self.visible:
            self._update_surface()

    def _update_surface(self):
        # Use consolidated window filtering
        windows = window_filter()
        if not windows:
            logging.warning("No Tetris window found")
            return

        # Get the best window (highest score)
        hwnd = max(windows.items(), key=lambda item: item[1])[0]

        try:
            cache = load_cache()
            roi = cache.get("roi", [0, 0, 640, 360])

            # Convert ROI format from [x0, y0, x1, y1] to (left, top, width, height)
            if len(roi) == 4:
                capture_rect = (roi[0], roi[1], roi[2] - roi[0], roi[3] - roi[1])
            else:
                capture_rect = tuple(roi)

            capture = ScreenCapture(capture_rect)
            img = capture.grab()
            surface = pygame.image.fromstring(img.tobytes(), img.size, "RGB")
            size = surface.get_size()
            self.screen = pygame.display.set_mode(
                size, pygame.NOFRAME | pygame.SRCALPHA
            )
            self.screen.blit(surface, (0, 0))
            ghost = pygame.Surface((80, 40), pygame.SRCALPHA)
            ghost.fill((0, 255, 0, 96))
            self.screen.blit(ghost, (20, 20))
            pygame.display.update()
            logging.info("Overlay surface refreshed (hwnd=%s)", hwnd)

        except Exception as e:
            logging.error(f"Failed to update overlay surface: {e}")
            self.visible = False

    def run_loop(self):
        while True:
            pygame.event.pump()
            pygame.time.wait(10)
