#!/usr/bin/env python3
"""
Test Tetris Overlay using real game screenshots
Tests OCR and piece detection on real game images
"""

import sys
import os
import time
from pathlib import Path
from typing import List, Tuple, Optional
import cv2
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QPen
    print("✅ Qt modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Qt modules not available: {e}")
    sys.exit(1)

try:
    from tetris_overlay.core.detection import find_tetris_board, detect_game_state
    from tetris_overlay.core.tetromino_shapes import get_piece_shape, get_piece_color
    print("✅ Tetris overlay modules loaded successfully")
except ImportError as e:
    print(f"⚠️ Tetris overlay modules not available: {e}")
    print("📊 Using basic image processing for testing")

class GameImageTester(QMainWindow):
    """Test overlay using real game screenshots"""
    
    def __init__(self):
        super().__init__()
        print("🎮 Initializing Game Image Tester...")
        
        self.setWindowTitle("🎮 Tetris Overlay - Game Image Test")
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
        
        self.ocr_button = QPushButton("📝 Test OCR")
        self.ocr_button.clicked.connect(self.test_ocr)
        controls_layout.addWidget(self.ocr_button)
        
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
        
        print("🎮 Game Image Tester initialized successfully!")
    
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
        self.status_label.setText(f"📷 Image {self.current_image_index + 1}/{len(self.game_images)}: {Path(image_path).name}")
    
    def previous_image(self):
        """Load previous image"""
        if self.game_images:
            self.current_image_index = (self.current_image_index - 1) % len(self.game_images)
            self.load_current_image()
    
    def next_image(self):
        """Load next image"""
        if self.game_images:
            self.current_image_index = (self.current_image_index + 1) % len(self.game_images)
            self.load_current_image()
    
    def detect_board(self):
        """Test board detection on current image"""
        if self.current_image is None:
            print("❌ No image loaded")
            return
        
        print("🔍 Detecting Tetris board...")
        
        try:
            # Try to find Tetris board
            board_rect = find_tetris_board(self.current_image)
            
            if board_rect:
                x, y, w, h = board_rect
                print(f"✅ Board found: ({x}, {y}, {w}, {h})")
                
                # Draw board rectangle on image
                result_image = self.current_image.copy()
                cv2.rectangle(result_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Display result
                height, width, channel = result_image.shape
                bytes_per_line = 3 * width
                q_image = QImage(result_image.data, width, height, bytes_per_line, QImage.Format_BGR888)
                pixmap = QPixmap.fromImage(q_image)
                self.image_label.setPixmap(pixmap.scaled(750, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                
                self.board_rect = board_rect
                self.status_label.setText(f"✅ Board detected: ({x}, {y}, {w}, {h})")
            else:
                print("❌ No board found")
                self.status_label.setText("❌ No Tetris board detected")
                
        except Exception as e:
            print(f"❌ Board detection failed: {e}")
            self.status_label.setText(f"❌ Board detection error: {e}")
    
    def test_ocr(self):
        """Test OCR on current image"""
        if self.current_image is None:
            print("❌ No image loaded")
            return
        
        print("📝 Testing OCR on game image...")
        
        try:
            # If we have a board rect, crop it
            if self.board_rect:
                x, y, w, h = self.board_rect
                board_image = self.current_image[y:y+h, x:x+w]
                print(f"📷 Cropped board area: ({x}, {y}, {w}, {h})")
            else:
                # Use full image
                board_image = self.current_image
                print("📷 Using full image for OCR")
            
            # Convert to grayscale for OCR
            gray = cv2.cvtColor(board_image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold for better OCR
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Display processed image
            height, width = thresh.shape
            bytes_per_line = width
            q_image = QImage(thresh.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap.scaled(750, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            print("✅ OCR preprocessing completed")
            self.status_label.setText("✅ OCR preprocessing completed - ready for character recognition")
            
        except Exception as e:
            print(f"❌ OCR test failed: {e}")
            self.status_label.setText(f"❌ OCR error: {e}")
    
    def closeEvent(self, event):
        """Handle window close"""
        print("🔴 Game Image Tester closed")
        event.accept()

def main():
    """Main entry point"""
    print("=" * 60)
    print("🎮 TETRIS OVERLAY - GAME IMAGE TEST")
    print("=" * 60)
    print("📸 Tests OCR and board detection on real game screenshots")
    print("🎮 Uses actual game images from game_screenshots/")
    print("🔍 Perfect for debugging without needing a running game")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    try:
        # Create and show tester
        tester = GameImageTester()
        tester.show()
        
        print("🚀 Game Image Tester started!")
        print("📊 Use buttons to navigate images and test detection")
        print("⚡ Press Ctrl+C or close window to exit")
        
        return app.exec()
        
    except Exception as e:
        print(f"❌ Error starting tester: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
