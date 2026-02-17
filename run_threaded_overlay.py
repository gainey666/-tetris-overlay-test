#!/usr/bin/env python3
"""
Threaded Tetris Overlay - Following senior dev architecture.
"""

import sys
import cv2
import numpy as np
import win32gui
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen
from pathlib import Path
from datetime import datetime

# -----------------------------------------------------------------
# Tracer import – safe fallback when the package is unavailable.
# -----------------------------------------------------------------
try:
    from tracer.client import safe_trace_calls as trace_calls
except Exception:  # pragma: no cover
    def trace_calls(*_, **__):  # type: ignore[misc]
        def _decorator(func):
            return func

        return _decorator

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from tetris_overlay.core.threaded_overlay import ThreadedOverlay
from tetris_overlay.core.tetromino_shapes import get_piece_shape, get_piece_color
from tetris_overlay.utils.logger import logger

# Setup file logging
def setup_file_logging():
    """Setup logging to file for debugging."""
    log_dir = Path.home() / ".tetris_overlay" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / f"overlay_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Redirect stdout and stderr to log file
    import sys
    sys.stdout = open(log_file, 'w', encoding='utf-8')
    sys.stderr = sys.stdout
    
    print(f"Logging to: {log_file}")
    return log_file

class ThreadedGhostOverlay(QWidget):
    """Threaded overlay that won't interfere with game rendering."""
    
    def __init__(self, target_hwnd):
        super().__init__()
        self.target_hwnd = target_hwnd
        self.frame_count = 0
        
        # Make window truly transparent
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Add Windows transparency flags
        try:
            from win32gui import SetWindowLong, GetWindowLong, GWL_EXSTYLE
            from win32con import WS_EX_LAYERED, WS_EX_TRANSPARENT
            hwnd = int(self.winId())
            ex_style = GetWindowLong(hwnd, GWL_EXSTYLE)
            SetWindowLong(hwnd, GWL_EXSTYLE, ex_style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
        except:
            pass
        
        # Position over target window
        self.update_position()
        
        # Initialize threaded overlay
        self.threaded_overlay = ThreadedOverlay(target_hwnd)
        
        # Fast UI timer (60 FPS for smooth rendering)
        self.timer = QTimer(self, timeout=self.update_overlay)
        self.timer.start(16)  # ~60 FPS
        
        # Screenshot timer
        self.screenshot_timer = QTimer(self, timeout=self.take_screenshot)
        self.screenshot_timer.start(30000)  # 30 seconds
        
        print("🎮 Threaded Tetris Overlay Started")
        print("📋 Architecture: Capture Thread → Analysis Thread → UI Thread")
        print("📸 Screenshots every 30 seconds")
        print("🎮 Press 1-7 to change pieces, R to rotate, ESC to quit")
        
    def update_position(self):
        """Position overlay over target window."""
        try:
            left, top, right, bottom = win32gui.GetWindowRect(self.target_hwnd)
            self.setGeometry(left, top, right - left, bottom - top)
        except:
            pass
    
    def update_overlay(self):
        """Update overlay with minimal processing."""
        try:
            self.frame_count += 1
            
            # Get ghost position from analysis thread
            ghost_pos = self.threaded_overlay.get_ghost_position()
            
            # Store for screenshot
            self.current_ghost_pos = ghost_pos
            
            # Trigger repaint
            self.update()
            
        except Exception as e:
            logger.error(f"Update error: {e}")
    
    def take_screenshot(self):
        """Take screenshot for debugging."""
        try:
            screenshots_dir = Path.home() / ".tetris_overlay" / "screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create a simple debug image showing ghost position
            debug_img = np.zeros((400, 600, 3), dtype=np.uint8)
            
            if hasattr(self, 'current_ghost_pos') and self.current_ghost_pos.valid:
                pos = self.current_ghost_pos
                color = get_piece_color(pos.piece_type)
                shape = get_piece_shape(pos.piece_type, pos.rotation)
                
                # Draw ghost piece
                cell_size = 30
                for x, y in shape:
                    screen_x = 100 + (pos.x // 30 + x) * cell_size
                    screen_y = 100 + (pos.y // 30 + y) * cell_size
                    
                    cv2.rectangle(debug_img, (screen_x, screen_y), 
                                 (screen_x + cell_size - 1, screen_y + cell_size - 1),
                                 color, thickness=cv2.FILLED)
                
                # Add debug text
                cv2.putText(debug_img, f"Piece: {pos.piece_type}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(debug_img, f"Position: ({pos.x}, {pos.y})", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(debug_img, f"Frame: {self.frame_count}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Save screenshot
            screenshot_path = screenshots_dir / f"threaded_overlay_{timestamp}.png"
            cv2.imwrite(str(screenshot_path), debug_img)
            
            print(f"📸 Screenshot saved: {screenshot_path}")
            
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
    
    def keyPressEvent(self, event):
        """Handle keyboard input."""
        # This would update the analysis thread's piece type
        # For now, just print the key press
        if event.key() == Qt.Key_1:
            print("🟦 I-piece selected")
        elif event.key() == Qt.Key_2:
            print("🟨 O-piece selected")
        elif event.key() == Qt.Key_3:
            print("🟪 T-piece selected")
        elif event.key() == Qt.Key_4:
            print("🟩 S-piece selected")
        elif event.key() == Qt.Key_5:
            print("🟥 Z-piece selected")
        elif event.key() == Qt.Key_6:
            print("🟦 J-piece selected")
        elif event.key() == Qt.Key_7:
            print("🟧 L-piece selected")
        elif event.key() == Qt.Key_R:
            print("🔄 Rotation requested")
        elif event.key() == Qt.Key_Escape:
            print("👋 Quitting...")
            self.close()
        
        self.update()
    
    def paintEvent(self, event):
        """Paint the overlay."""
        if hasattr(self, 'current_ghost_pos') and self.current_ghost_pos.valid:
            pos = self.current_ghost_pos
            
            # Get piece shape and color
            shape = get_piece_shape(pos.piece_type, pos.rotation)
            color = get_piece_color(pos.piece_type)
            
            # Calculate cell size based on window size
            cell_width = self.width() // 10
            cell_height = self.height() // 20
            
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw ghost piece
            ghost_color = QColor(*color, 128)  # Semi-transparent
            pen_color = QColor(*color, 255)
            
            painter.setPen(pen_color)
            painter.setBrush(ghost_color)
            
            for x, y in shape:
                screen_x = pos.x + x * cell_width
                screen_y = pos.y + y * cell_height
                
                rect = Qt.QRectF(screen_x, screen_y, cell_width, cell_height)
                painter.drawRect(rect)
            
            # Draw debug info
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(10, 20, f"Frame: {self.frame_count}")
            painter.drawText(10, 40, f"Piece: {pos.piece_type}")
            painter.drawText(10, 60, f"Pos: ({pos.x}, {pos.y})")

def main():
    """Run threaded overlay."""
    app = QApplication(sys.argv)
    
    # Auto-detect Tetris windows
    print("🔍 Detecting Tetris windows...")
    
    tetris_windows = []
    def enum_callback(hwnd, windows):
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and any(keyword in title.lower() for keyword in ['tetris', 'tetris.com']):
                    windows.append((hwnd, title))
        except Exception as e:
            print(f"   ❌ Error checking window {hwnd}: {e}")
        return True
    
    win32gui.EnumWindows(enum_callback, tetris_windows)
    
    if not tetris_windows:
        print("❌ No Tetris windows found!")
        return 1
    
    # Use the best Tetris window (prioritize actual games)
    best_window = None
    best_score = 0
    
    for hwnd, title in tetris_windows:
        score = 0
        title_lower = title.lower()
        
        if 'tetris effect' in title_lower:
            score = 100
        elif 'tetris.com' in title_lower:
            score = 90
        elif 'tetris' in title_lower and 'windsurf' not in title_lower:
            score = 50
        elif 'tetris' in title_lower:
            score = 10
        
        print(f"   Scoring '{title}': {score}")
        
        if score > best_score:
            best_score = score
            best_window = (hwnd, title)
    
    hwnd, title = best_window
    print(f"\n✅ Using window {hwnd} - {title} (score: {best_score})")
    
    try:
        overlay = ThreadedGhostOverlay(hwnd)
        overlay.show()
        overlay.raise_()
        overlay.activateWindow()
        print("✅ Threaded overlay window created and activated")
        
        # Handle cleanup on exit
        def cleanup():
            if hasattr(overlay, 'threaded_overlay'):
                overlay.threaded_overlay.stop()
        
        app.aboutToQuit.connect(cleanup)
        
        return app.exec()
    except Exception as e:
        print(f"❌ Failed to create overlay: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
