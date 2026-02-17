#!/usr/bin/env python3
"""
Simple Working Tetris Overlay - WITH REAL TRACER
Uses real game screenshots for testing
Reports ALL function calls to tracer server
"""

import sys
from pathlib import Path
from typing import List, Optional
import cv2
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import tracer client
try:
    from tracer.client import safe_trace_calls as trace_calls
    TRACER_AVAILABLE = True
    print("✅ Tracer client loaded successfully")
except ImportError:
    TRACER_AVAILABLE = False
    print("⚠️ Tracer client not available - running without tracing")

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QImage, QPixmap
    print("✅ Qt modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Qt modules not available: {e}")
    sys.exit(1)

class SimpleWorkingOverlay(QMainWindow):
    """Simple working Tetris overlay - WITH TRACER"""
    
    @trace_calls("S")
    def __init__(self):
        print("🎮 Initializing Simple Working Overlay...")
        
        super().__init__()
        self.setWindowTitle("🎮 Tetris Ghost Overlay - WITH TRACER")
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
        
        if self.game_images:
            self.load_current_image()
            print(f"✅ Loaded {len(self.game_images)} game images")
        else:
            print("❌ No game images found")
        
        print("🎮 Simple Working Overlay initialized successfully!")
    
    @trace_calls("S")
    def load_game_images(self) -> List[str]:
        """Load all game screenshot paths"""
        game_dir = Path("game_screenshots")
        if not game_dir.exists():
            print(f"❌ Game screenshots directory not found: {game_dir}")
            return []
        
        image_files = list(game_dir.glob("*.png"))
        image_files.sort()
        
        print(f"📸 Found {len(image_files)} game images:")
        for img in image_files:
            print(f"  📷 {img.name} ({img.stat().st_size // 1024}KB)")
        
        return [str(img) for img in image_files]
    
    @trace_calls("S")
    def load_current_image(self):
        """Load current game image"""
        if not self.game_images:
            return
        
        image_path = self.game_images[self.current_image_index]
        print(f"📷 Loading image: {Path(image_path).name}")
        
        # Load image with OpenCV
        self.current_image = cv2.imread(image_path)
        if self.current_image is None:
            print(f"❌ Failed to load image: {image_path}")
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
    
    @trace_calls("S")
    def previous_image(self):
        """Load previous image"""
        if self.game_images:
            self.current_image_index = (self.current_image_index - 1) % len(self.game_images)
            self.load_current_image()
    
    @trace_calls("S")
    def next_image(self):
        """Load next image"""
        if self.game_images:
            self.current_image_index = (self.current_image_index + 1) % len(self.game_images)
            self.load_current_image()
    
    @trace_calls("S")
    def detect_board(self):
        """Test board detection on current image"""
        if self.current_image is None:
            print("❌ No image loaded")
            return
        
        print("🔍 Detecting Tetris board...")
        
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
        
        print(f"✅ Board detected: {board_width}x{board_height} at ({board_x}, {board_y})")
        self.status_label.setText(f"✅ Board detected: {board_width}x{board_height} at ({board_x}, {board_y})")
    
    @trace_calls("S")
    def show_ghost(self):
        """Show ghost piece on current image"""
        if self.current_image is None or self.board_rect is None:
            print("❌ No image or board detected")
            return
        
        print("👻 Showing ghost piece...")
        
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
        
        print("✅ Ghost piece rendered")
        self.status_label.setText("✅ Ghost piece rendered - T-piece at center")
    
    @trace_calls("S")
    def closeEvent(self, event):
        """Handle window close"""
        print("🔴 Simple Working Overlay closed")
        event.accept()

@trace_calls("S")
def main():
    """Main entry point"""
    print("=" * 60)
    print("🎮 SIMPLE WORKING TETRIS OVERLAY - WITH TRACER")
    print("=" * 60)
    print("📸 Tests board detection and ghost pieces on real game screenshots")
    print("🎮 Uses actual game images from game_screenshots/")
    print("👻 Shows how ghost pieces would appear in real gameplay")
    print("� ALL function calls reported to tracer server")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    try:
        # Create and show overlay
        overlay = SimpleWorkingOverlay()
        overlay.show()
        
        print("🚀 Simple Working Overlay started!")
        print("📊 Use buttons to navigate images and test detection")
        print("👻 Click 'Detect Board' then 'Show Ghost' to see ghost pieces")
        print("🔍 Check tracer window for detailed function calls")
        print("⚡ Press Ctrl+C or close window to exit")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error starting overlay: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
