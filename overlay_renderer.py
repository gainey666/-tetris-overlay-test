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
        self.screen = pygame.display.set_mode((1, 1), flags)
        self.visible = False
        self.combo_counter = 0
        self.b2b_counter = 0
        self._ghost_colour = (0, 255, 0, 96)  # Default green
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
            
            # Draw combo counter
            if self.combo_counter > 1:
                combo_text = font.render(f"Combo x{self.combo_counter}", True, (255, 255, 255))
                surface.blit(combo_text, (10, 10))
            
            # Draw B2B counter
            if self.b2b_counter > 0:
                b2b_text = font.render(f"B2B x{self.b2b_counter}", True, (255, 215, 0))
                surface.blit(b2b_text, (10, 40))

    def draw_ghost(self, surface, column, rotation, piece_type="T", is_tspin=False, is_b2b=False, combo=0):
        """Draw a semi-transparent ghost piece with special move indicators."""
        cell_w = 30
        cell_h = 30
        
        # Get the shape for this piece type and rotation
        if piece_type not in PIECE_SHAPES:
            piece_type = "T"  # Fallback to T piece
        
        shapes = PIECE_SHAPES[piece_type]
        if rotation >= len(shapes):
            rotation = 0  # Fallback to first rotation
        shape = shapes[rotation]
        
        # Create a semi-transparent surface
        max_x = max(x for x, y in shape) + 1
        max_y = max(y for x, y in shape) + 1
        ghost_surface = pygame.Surface((max_x * cell_w, max_y * cell_h), pygame.SRCALPHA)
        
        # Choose ghost color based on special moves or use configured style
        if is_tspin:
            ghost_color = (255, 0, 255, 128)  # Purple for T-Spin
        elif is_b2b:
            ghost_color = (255, 215, 0, 128)  # Gold for B2B
        elif combo > 0:
            ghost_color = (0, 255, 255, 128)  # Cyan for combo
        else:
            ghost_color = self._ghost_colour  # Use configured colour
        
        # Draw the piece shape
        for x, y in shape:
            rect = pygame.Rect(x * cell_w, y * cell_h, cell_w, cell_h)
            pygame.draw.rect(ghost_surface, ghost_color, rect)
            pygame.draw.rect(ghost_surface, (*ghost_color[:3], 200), rect, 2)  # Border
        
        # Draw special indicators
        if is_tspin:
            # Draw "TSPIN" text
            font = pygame.font.Font(None, 20)
            text = font.render("TSPIN", True, (255, 255, 255))
            text_rect = text.get_rect(center=(max_x * cell_w // 2, -10))
            ghost_surface.blit(text, text_rect)
        
        if is_b2b:
            # Draw "B2B" text
            font = pygame.font.Font(None, 20)
            text = font.render("B2B", True, (255, 255, 255))
            text_rect = text.get_rect(center=(max_x * cell_w // 2, -10))
            ghost_surface.blit(text, text_rect)
        
        if combo > 1:
            # Draw combo counter
            font = pygame.font.Font(None, 20)
            text = font.render(f"x{combo}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(max_x * cell_w // 2, -10))
            ghost_surface.blit(text, text_rect)
        
        # Blit the ghost to the main surface at the predicted column
        ghost_x = column * cell_w
        ghost_y = 0  # Start at top of board
        surface.blit(ghost_surface, (ghost_x, ghost_y))

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
