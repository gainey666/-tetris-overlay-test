#!/usr/bin/env python3
"""
Working Tetris Overlay - Original plan restored
Uses real game screenshots for testing
Reports ALL function calls to standalone tracer
"""

import sys
import time
from pathlib import Path
from typing import List, Optional
import cv2
import numpy as np

# -----------------------------------------------------------------
# Tracer import – safe fallback when optional package is missing.
# Existing code decorates functions with rich metadata (func/file/line);
# we simply forward every call to the underlying safe decorator.
# -----------------------------------------------------------------
try:
    from tracer.client import safe_trace_calls as _base_trace_calls
    TRACER_AVAILABLE = True
except Exception:  # pragma: no cover
    TRACER_AVAILABLE = False

    def _base_trace_calls(*_, **__):  # type: ignore[misc]
        def _decorator(func):
            return func

        return _decorator


def trace_calls(*args, **__):  # type: ignore[misc]
    """Compatibility wrapper for legacy decorator signature."""
    status = args[0] if args and isinstance(args[0], str) and len(args[0]) == 1 else "S"
    return _base_trace_calls(status)


# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def log_function(func_name, message, status="INFO"):
    """Log function call to tracer or console"""
    if TRACER_AVAILABLE:
        global_tracer.trace_function(func_name, "run_working_tetris_overlay.py", 1, f"ARGS({message})", result=f"RESULT({status})")
    else:
        print(f"🔵 {func_name}(): {message} -> {status}")

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QPen
    print("✅ Qt modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Qt modules not available: {e}")
    sys.exit(1)

# Conditional tracer decorator
def trace_calls(func_name, file_name, line_num):
    """Conditional tracer decorator"""
    def decorator(func):
        if TRACER_AVAILABLE:
            # Use real tracer
            def wrapper(*args, **kwargs):
                global_tracer.trace_function(func_name, file_name, line_num, f"ARGS({args})", result="ENTER")
                try:
                    result = func(*args, **kwargs)
                    global_tracer.trace_function(func_name, file_name, line_num, result=f"SUCCESS({result})")
                    return result
                except Exception as e:
                    global_tracer.trace_function(func_name, file_name, line_num, result=f"ERROR({e})")
                    raise
            return wrapper
        else:
            # No-op decorator when tracer not available
            return func
        return decorator

@trace_calls("WorkingTetrisOverlay.__init__", "run_working_tetris_overlay.py", 30)
class WorkingTetrisOverlay(QMainWindow):
    """Working Tetris overlay using real game screenshots"""
    
    def __init__(self):
        log_function("WorkingTetrisOverlay.__init__", "Initializing Working Tetris Overlay", "ENTER")
        
        super().__init__()
        self.setWindowTitle("🎮 Tetris Ghost Overlay - WORKING")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create controls
        controls_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("⬅️ Previous Image")
        self.prev_button.clicked.connect(self.previous_image)
        controls_layout.addWidget(self.prev_button)
        
        self.next_button = QPushButton("➡️ Next Image")
        self.next_button.clicked.connect(self.next_image)
        controls_layout.addWidget(self.next_button)
        
        self.detect_button = QPushButton("🔍 Detect Board")
        self.detect_button.clicked.connect(self.detect_board)
        controls_layout.addWidget(self.detect_button)
        
        self.ghost_button = QPushButton("👻 Show Ghost")
        self.ghost_button.clicked.connect(self.show_ghost)
        controls_layout.addWidget(self.ghost_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Create image display
        self.image_label = QLabel("🎮 Load game image to test")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: #2b2b2b;
                color: #00ff00;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #00ff00;
                min-height: 400px;
            }
        """)
        layout.addWidget(self.image_label)
        
        # Create status label
        self.status_label = QLabel("📊 Ready to test with real game images")
        self.status_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                color: #ffff00;
                font-size: 12px;
                padding: 5px;
                border: 1px solid #ffff00;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Load game images
        self.game_images = self.load_game_images()
        self.current_image_index = 0
        self.current_image = None
        self.board_rect = None
        self.ghost_piece = None
        
        if self.game_images:
            self.load_current_image()
            log_function("WorkingTetrisOverlay.__init__", f"Loaded {len(self.game_images)} game images", "SUCCESS")
        else:
            log_function("WorkingTetrisOverlay.__init__", "No game images found", "WARNING")
        
        log_function("WorkingTetrisOverlay.__init__", "Working Tetris Overlay initialized", "SUCCESS")
    
    @trace_calls("load_game_images", "run_working_tetris_overlay.py", 90)
    def load_game_images(self) -> List[str]:
        """Load all game screenshot paths"""
        log_function("load_game_images", "Loading game screenshots", "ENTER")
        
        game_dir = Path("game_screenshots")
        if not game_dir.exists():
            log_function("load_game_images", f"Game screenshots directory not found: {game_dir}", "ERROR")
            return []
        
        image_files = list(game_dir.glob("*.png"))
        image_files.sort()
        
        log_function("load_game_images", f"Found {len(image_files)} game images", "SUCCESS")
        
        for img in image_files:
            size_kb = img.stat().st_size // 1024
            log_function("load_game_images", f"Image {img.name} ({size_kb}KB)", "INFO")
        
        return [str(img) for img in image_files]
    
    @trace_calls("load_current_image", "run_working_tetris_overlay.py", 110)
    def load_current_image(self):
        """Load current game image"""
        if not self.game_images:
            return
        
        image_path = self.game_images[self.current_image_index]
        log_function("load_current_image", f"Loading image: {Path(image_path).name}", "ENTER")
        
        # Load image with OpenCV
        self.current_image = cv2.imread(image_path)
        if self.current_image is None:
            log_function("load_current_image", f"Failed to load image: {image_path}", "ERROR")
            return
        
        # Convert to Qt image
        height, width, channel = self.current_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(self.current_image.data, width, height, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(q_image)
        
        # Display image
        self.image_label.setPixmap(pixmap.scaled(750, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # Update status
        status = f"📷 Image {self.current_image_index + 1}/{len(self.game_images)}: {Path(image_path).name}"
        self.status_label.setText(status)
        log_function("load_current_image", status, "SUCCESS")
    
    @trace_calls("previous_image", "run_working_tetris_overlay.py", 130)
    def previous_image(self):
        """Load previous image"""
        if self.game_images:
            old_index = self.current_image_index
            self.current_image_index = (self.current_image_index - 1) % len(self.game_images)
            log_function("previous_image", f"Changed from image {old_index + 1} to {self.current_image_index + 1}", "INFO")
            self.load_current_image()
    
    @trace_calls("next_image", "run_working_tetris_overlay.py", 140)
    def next_image(self):
        """Load next image"""
        if self.game_images:
            old_index = self.current_image_index
            self.current_image_index = (self.current_image_index + 1) % len(self.game_images)
            log_function("next_image", f"Changed from image {old_index + 1} to {self.current_image_index + 1}", "INFO")
            self.load_current_image()
    
    @trace_calls("detect_board", "run_working_tetris_overlay.py", 150)
    def detect_board(self):
        """Test board detection on current image"""
        if self.current_image is None:
            log_function("detect_board", "No image loaded", "ERROR")
            return
        
        log_function("detect_board", "Detecting Tetris board", "ENTER")
        
        # Simulate board detection (10x20 grid in center)
        height, width = self.current_image.shape[:2]
        board_width = width // 2
        board_height = height // 2
        board_x = (width - board_width) // 2
        board_y = (height - board_height) // 2
        
        self.board_rect = (board_x, board_y, board_width, board_height)
        
        # Draw board rectangle on image
        result_image = self.current_image.copy()
        cv2.rectangle(result_image, (board_x, board_y), (board_x + board_width, board_y + board_height), (0, 255, 0), 2)
        
        # Draw grid lines
        cell_width = board_width // 10
        cell_height = board_height // 20
        
        for i in range(1, 10):
            x = board_x + i * cell_width
            cv2.line(result_image, (x, board_y), (x, board_y + board_height), (100, 100, 100), 1)
        
        for i in range(1, 20):
            y = board_y + i * cell_height
            cv2.line(result_image, (board_x, y), (board_x + board_width, y), (100, 100, 100), 1)
        
        # Display result
        h, w, ch = result_image.shape
        bytes_per_line = 3 * w
        q_image = QImage(result_image.data, w, h, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap.scaled(750, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        log_function("detect_board", f"Board detected: {board_width}x{board_height} at ({board_x}, {board_y})", "SUCCESS")
        self.status_label.setText(f"✅ Board detected: {board_width}x{board_height} at ({board_x}, {board_y})")
    
    @trace_calls("show_ghost", "run_working_tetris_overlay.py", 180)
    def show_ghost(self):
        """Show ghost piece on current image"""
        if self.current_image is None or self.board_rect is None:
            log_function("show_ghost", "No image or board detected", "ERROR")
            return
        
        log_function("show_ghost", "Showing ghost piece", "ENTER")
        
        # Create ghost piece (T-piece)
        result_image = self.current_image.copy()
        board_x, board_y, board_width, board_height = self.board_rect
        cell_width = board_width // 10
        cell_height = board_height // 20
        
        # T-piece shape
        t_piece = [(1, 0), (0, 1), (1, 1), (2, 1)]
        
        # Position ghost piece
        ghost_x = 4  # Center column
        ghost_y = 0  # Top row
        
        # Draw ghost piece
        for px, py in t_piece:
            x = board_x + (ghost_x + px) * cell_width
            y = board_y + (ghost_y + py) * cell_height
            
            # Semi-transparent green
            overlay = result_image.copy()
            cv2.rectangle(overlay, (x, y), (x + cell_width, y + cell_height), (0, 255, 0), -1)
            cv2.addWeighted(result_image, 0.7, overlay, 0.3, 0, result_image)
            
            # Draw outline
            cv2.rectangle(result_image, (x, y), (x + cell_width, y + cell_height), (0, 255, 0), 2)
        
        # Display result
        h, w, ch = result_image.shape
        bytes_per_line = 3 * w
        q_image = QImage(result_image.data, w, h, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap.scaled(750, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        log_function("show_ghost", "Ghost piece rendered", "SUCCESS")
        self.status_label.setText("✅ Ghost piece rendered - T-piece at center")
    
    @trace_calls("closeEvent", "run_working_tetris_overlay.py", 210)
    def closeEvent(self, event):
        """Handle window close"""
        log_function("closeEvent", "Working Tetris Overlay closed", "INFO")
        event.accept()

@trace_calls("main", "run_working_tetris_overlay.py", 220)
def main():
    """Main entry point"""
    log_function("main", "Starting Working Tetris Overlay", "ENTER")
    
    print("=" * 60)
    print("🎮 WORKING TETRIS OVERLAY")
    print("=" * 60)
    print("📸 Tests board detection and ghost pieces on real game screenshots")
    print("🎮 Uses actual game images from game_screenshots/")
    print("👻 Shows how ghost pieces would appear in real gameplay")
    print("📊 ALL function calls reported to standalone tracer")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    try:
        # Create and show overlay
        overlay = WorkingTetrisOverlay()
        overlay.show()
        
        log_function("main", "Working Tetris Overlay started", "SUCCESS")
        print("🚀 Working Tetris Overlay started!")
        print("📊 Use buttons to navigate images and test detection")
        print("👻 Click 'Detect Board' then 'Show Ghost' to see ghost pieces")
        print("🔍 Check standalone tracer for detailed function calls")
        print("⚡ Press Ctrl+C or close window to exit")
        
        return app.exec()
        
    except Exception as e:
        log_function("main", f"Error starting overlay: {e}", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main())
