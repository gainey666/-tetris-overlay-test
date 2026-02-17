"""
Main overlay widget for displaying ghost pieces.
"""

import cv2
import numpy as np
import win32gui
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QPixmap, QImage
import sys
from typing import Optional
from pathlib import Path
from datetime import datetime

from .config import OverlayConfig
from .capture import grab_window
from .tetromino_shapes import get_piece_shape, get_piece_color
from .detection import find_tetris_board, detect_game_state
from ..utils.logger import logger


class GhostOverlay(QWidget):
    """Transparent overlay widget for displaying ghost pieces."""
    
    def __init__(self, config: OverlayConfig, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Make window transparent and click-through
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        
        # Add WS_EX_LAYERED and WS_EX_TRANSPARENT for true transparency
        from win32gui import SetWindowLong, GetWindowLong, GWL_EXSTYLE
        from win32con import WS_EX_LAYERED, WS_EX_TRANSPARENT
        
        try:
            hwnd = int(self.winId())
            ex_style = GetWindowLong(hwnd, GWL_EXSTYLE)
            SetWindowLong(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
        except:
            pass  # If this fails, continue without it
        
        self.config = config
        self._current_pixmap: Optional[QPixmap] = None
        self.board_area: Optional[tuple] = None
        self.game_state: Optional[dict] = None
        self.frame_count = 0
        
        # Setup timer for updates (slower to avoid interference)
        self.timer = QTimer(self, timeout=self.update_frame)
        self.timer.start(1000 // min(config.refresh_rate, 15))  # Cap at 15 FPS
        
        # Setup screenshot timer (every 30 seconds)
        self.screenshot_timer = QTimer(self, timeout=self.take_screenshot)
        self.screenshot_timer.start(30000)  # 30 seconds
        
        # Position window over target
        self.update_target_geometry()
        
        logger.info(f"GhostOverlay initialized for window {config.target_hwnd}")
        
    def update_target_geometry(self):
        """Position the overlay window over the target window."""
        try:
            if self.config.target_hwnd > 0:
                left, top, right, bottom = win32gui.GetWindowRect(self.config.target_hwnd)
                self.setGeometry(left, top, right - left, bottom - top)
            else:
                # For testing, center on screen
                from PySide6.QtGui import QGuiApplication
                screen = QGuiApplication.primaryScreen().geometry()
                self.setGeometry(screen.width()//2 - 100, screen.height()//2 - 100, 200, 200)
        except Exception as e:
            print(f"Failed to position window: {e}")
    
    def update_frame(self):
        """Update the overlay frame."""
        try:
            self.frame_count += 1
            
            # Only capture if we have a valid window handle
            if self.config.target_hwnd > 0:
                # Grab the game screen
                img = grab_window(self.config.target_hwnd)
                
                # Find the Tetris board
                if self.board_area is None:
                    self.board_area = find_tetris_board(img)
                    if self.board_area:
                        logger.info(f"Found Tetris board at {self.board_area}")
                    else:
                        logger.warning("Could not find Tetris board")
                
                # Detect game state
                if self.board_area:
                    self.game_state = detect_game_state(img, self.board_area)
                
                # Render ghost piece
                ghost = self.render_ghost(img)
                
                # Convert numpy to QPixmap
                h, w, _ = ghost.shape
                img_qt = QImage(ghost.data, w, h, w * 3, QImage.Format_BGR888)
                self._current_pixmap = QPixmap.fromImage(img_qt)
            else:
                # Create a simple test overlay without window capture
                test_img = np.zeros((200, 200, 3), dtype=np.uint8)
                # Draw a green rectangle
                test_img[50:150, 50:150] = [0, 255, 0]
                h, w, _ = test_img.shape
                img_qt = QImage(test_img.data, w, h, w * 3, QImage.Format_BGR888)
                self._current_pixmap = QPixmap.fromImage(img_qt)
            
            # Trigger repaint
            self.update()
            
        except Exception as e:
            logger.error(f"Failed to update frame: {e}")
            # Don't let errors crash the overlay
            pass
    
    def take_screenshot(self):
        """Take a screenshot of what the overlay sees."""
        try:
            if self.config.target_hwnd > 0:
                # Grab the game screen
                img = grab_window(self.config.target_hwnd)
                
                # Create screenshots directory
                screenshots_dir = Path.home() / ".tetris_overlay" / "screenshots"
                screenshots_dir.mkdir(parents=True, exist_ok=True)
                
                # Save screenshot with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = screenshots_dir / f"tetris_capture_{timestamp}.png"
                
                # Save the raw capture
                cv2.imwrite(str(screenshot_path), img)
                
                # Also save the processed version with overlay
                processed_img = self.render_ghost(img)
                processed_path = screenshots_dir / f"tetris_overlay_{timestamp}.png"
                cv2.imwrite(str(processed_path), processed_img)
                
                # Record screenshot time for indicator
                self._last_screenshot_time = datetime.now().timestamp()
                
                logger.info(f"Screenshot saved: {screenshot_path}")
                logger.info(f"Overlay screenshot saved: {processed_path}")
                
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
    
    def render_ghost(self, frame: np.ndarray) -> np.ndarray:
        """
        Render a real Tetris ghost piece on the frame.
        """
        overlay = frame.copy()
        h, w, _ = overlay.shape
        
        # For now, show a T-piece ghost in the center
        piece_type = "T"
        rotation = 0
        
        # Get piece shape and color
        shape = get_piece_shape(piece_type, rotation)
        color = get_piece_color(piece_type)
        
        # Calculate cell size (assuming 10x20 grid)
        cell_width = w // 10
        cell_height = h // 20
        
        # Draw ghost piece in center of board
        center_x = 5  # Center column
        center_y = 10  # Center row
        
        for x, y in shape:
            # Convert to screen coordinates
            screen_x = (center_x + x) * cell_width
            screen_y = (center_y + y) * cell_height
            
            # Draw semi-transparent rectangle
            ghost_color = (*color, 128)  # Add alpha
            cv2.rectangle(overlay, 
                         (screen_x, screen_y), 
                         (screen_x + cell_width - 1, screen_y + cell_height - 1),
                         ghost_color, thickness=cv2.FILLED)
            
            # Draw outline
            cv2.rectangle(overlay, 
                         (screen_x, screen_y), 
                         (screen_x + cell_width - 1, screen_y + cell_height - 1),
                         color, thickness=1)
        
        # Add debug info
        cv2.putText(overlay, f"Board: {w}x{h}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(overlay, f"Cell: {cell_width}x{cell_height}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(overlay, f"Piece: {piece_type}", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(overlay, f"Frame: {self.frame_count}", (10, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        
        # Add screenshot indicator
        if hasattr(self, '_last_screenshot_time'):
            time_since = datetime.now().timestamp() - self._last_screenshot_time
            if time_since < 2:  # Show for 2 seconds after screenshot
                cv2.putText(overlay, "📸 SCREENSHOT TAKEN", (10, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Blend with target opacity
        alpha = self.config.opacity
        beta = 1.0 - alpha
        blended = cv2.addWeighted(frame, beta, overlay, alpha, 0)
        
        return blended
    
    def paintEvent(self, event):
        """Paint the overlay."""
        if self._current_pixmap is not None:
            painter = QPainter(self)
            painter.drawPixmap(QRect(0, 0, self.width(), self.height()),
                           self._current_pixmap)
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.timer.stop()
        super().closeEvent(event)


def main():
    """Main entry point for the overlay."""
    app = QApplication(sys.argv)
    
    # For testing, create a simple overlay without window capture
    config = OverlayConfig(target_hwnd=0)  # 0 means no target window
    config.opacity = 0.3  # Make it more visible for testing
    
    overlay = GhostOverlay(config)
    overlay.show()
    
    print("Test overlay started - showing green rectangle")
    print("Press Ctrl+C to exit")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
