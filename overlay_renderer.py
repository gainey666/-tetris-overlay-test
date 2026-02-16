import logging
import pygame

from tetris_overlay_core import window_filter, ScreenCapture
from window_manager import load_cache

pygame.init()


class OverlayRenderer:
    def __init__(self):
        flags = pygame.NOFRAME | pygame.SRCALPHA
        self.screen = pygame.display.set_mode((1, 1), flags)
        self.visible = False
        logging.info("OverlayRenderer initialized (hidden)")

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
            self.screen = pygame.display.set_mode(size, pygame.NOFRAME | pygame.SRCALPHA)
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
