import logging
import pygame

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
        logging.info("OverlayRenderer initialized (hidden)")

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

    def draw_ghost(self, surface, column, rotation, piece_type="T", is_tspin=False, is_b2b=False, combo=0):
        """Draw a semi-transparent ghost piece with special move indicators."""
        cell_w = 30
        cell_h = 30
        
        # Use the current ghost style
        ghost_surface = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
        ghost_surface.fill(self._ghost_colour)
        
        # Draw the ghost piece (simple rectangle for now - can be enhanced with real shapes)
        x = column * cell_w
        y = (20 - 1) * cell_h  # Position at bottom of board
        surface.blit(ghost_surface, (x, y))
        
        # Draw special move indicators above the ghost
        indicator_y = y - 10
        
        if is_tspin:
            font = pygame.font.Font(None, 20)
            text = font.render("TSPIN", True, (255, 255, 255))
            text_rect = text.get_rect(center=(x + cell_w // 2, indicator_y))
            surface.blit(text, text_rect)
            indicator_y -= 15
        
        if is_b2b:
            font = pygame.font.Font(None, 20)
            text = font.render("B2B", True, (255, 255, 255))
            text_rect = text.get_rect(center=(x + cell_w // 2, indicator_y))
            surface.blit(text, text_rect)
            indicator_y -= 15
        
        if combo > 0:
            font = pygame.font.Font(None, 20)
            text = font.render(f"x{combo}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(x + cell_w // 2, indicator_y))
            surface.blit(text, text_rect)

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
