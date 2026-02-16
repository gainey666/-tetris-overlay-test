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
        logging.info("OverlayRenderer initialized (hidden)")

    def draw_ghost(self, surface, column, rotation, piece_type="T"):
        """Draw a semi-transparent ghost piece with actual tetromino shape."""
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
        
        # Draw the piece shape
        ghost_color = (0, 255, 0, 96)  # Semi-transparent green
        for x, y in shape:
            rect = pygame.Rect(x * cell_w, y * cell_h, cell_w, cell_h)
            pygame.draw.rect(ghost_surface, ghost_color, rect)
            pygame.draw.rect(ghost_surface, (0, 255, 0, 128), rect, 2)  # Border
        
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
