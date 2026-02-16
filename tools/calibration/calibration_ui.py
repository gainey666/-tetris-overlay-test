import logging
import pygame
from pygame.locals import QUIT, KEYDOWN, K_ESCAPE, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION, NOFRAME, SRCALPHA

from window_manager import get_active_tetris_hwnd, save_cache, clamp_roi
from dual_roi_manager import set_roi_pair
import logging


def start_calibration():
    rois = []
    while len(rois) < 2:
        rect = _run_one_drag()
        rois.append([rect.left, rect.top, rect.width, rect.height])
        logging.info(f"ROI {len(rois)} saved: {rois[-1]}")
        if len(rois) < 2:
            print("Draw second ROI for opponent board...")
    set_roi_pair(rois)

def _run_one_drag():
    pygame.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), NOFRAME | SRCALPHA)
    pygame.display.set_caption("Tetris ROI Calibration – Drag to select, Esc to cancel")
    overlay = pygame.Surface(screen.get_size(), SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    selecting = False
    rect_start = (0, 0)
    rect = pygame.Rect(0, 0, 0, 0)
    clock = pygame.time.Clock()
    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == QUIT:
                running = False
                break
            if ev.type == KEYDOWN and ev.key == K_ESCAPE:
                logging.info("Calibration cancelled by user")
                running = False
                break
            if ev.type == MOUSEBUTTONDOWN and ev.button == 1:
                selecting = True
                rect_start = ev.pos
                rect.topleft = ev.pos
                rect.size = (0, 0)
            if ev.type == MOUSEMOTION and selecting:
                x0, y0 = rect_start
                x1, y1 = ev.pos
                rect.left = min(x0, x1)
                rect.top = min(y0, y1)
                rect.width = abs(x1 - x0)
                rect.height = abs(y1 - y0)
            if ev.type == MOUSEBUTTONUP and ev.button == 1 and selecting:
                selecting = False
                pygame.quit()
                return rect
        screen.blit(overlay, (0, 0))
        if selecting or rect.width or rect.height:
            pygame.draw.rect(screen, (255, 255, 255, 200), rect, width=2)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
    return pygame.Rect(0, 0, 0, 0)
