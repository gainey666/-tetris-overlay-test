#!/usr/bin/env python3
"""
Test overlay that shows real Tetris ghost pieces.
"""

import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QKeyEvent
import numpy as np
from PySide6.QtGui import QImage, QPixmap
import cv2

# Import our Tetris shapes
sys.path.append('src')
from tetris_overlay.core.tetromino_shapes import get_piece_shape, get_piece_color

class TetrisTestOverlay(QWidget):
    """Test overlay that shows real Tetris ghost pieces."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tetris Ghost Piece Test")
        self.setFixedSize(300, 600)  # Standard Tetris board ratio
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        # Remove click-through so we can capture keyboard input
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Center on screen
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(screen.width()//2 - 150, screen.height()//2 - 300, 300, 600)
        
        # Current piece state
        self.current_piece = "T"
        self.current_rotation = 0
        self.show_ghost = True
        
        # Make sure window can receive keyboard input
        self.setFocusPolicy(Qt.StrongFocus)
        self.raise_()
        self.activateWindow()
        
        print("🎮 TETRIS GHOST PIECE TEST")
        print("📋 CONTROLS:")
        print("   1-7: Change piece type (I,O,T,S,Z,J,L)")
        print("   R: Rotate piece")
        print("   G: Toggle ghost visibility")
        print("   ESC: Quit")
        print("⚠️  Click on the window to give it focus!")
        
    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard input."""
        if event.key() == Qt.Key_1:
            self.current_piece = "I"
            print("🟦 Changed to I-piece (Cyan)")
        elif event.key() == Qt.Key_2:
            self.current_piece = "O"
            print("🟨 Changed to O-piece (Yellow)")
        elif event.key() == Qt.Key_3:
            self.current_piece = "T"
            print("🟪 Changed to T-piece (Purple)")
        elif event.key() == Qt.Key_4:
            self.current_piece = "S"
            print("🟩 Changed to S-piece (Green)")
        elif event.key() == Qt.Key_5:
            self.current_piece = "Z"
            print("🟥 Changed to Z-piece (Red)")
        elif event.key() == Qt.Key_6:
            self.current_piece = "J"
            print("🟦 Changed to J-piece (Blue)")
        elif event.key() == Qt.Key_7:
            self.current_piece = "L"
            print("🟧 Changed to L-piece (Orange)")
        elif event.key() == Qt.Key_R:
            self.current_rotation = (self.current_rotation + 1) % 4
            print(f"🔄 Rotation: {self.current_rotation}")
        elif event.key() == Qt.Key_G:
            self.show_ghost = not self.show_ghost
            print(f"👻 Ghost {'visible' if self.show_ghost else 'hidden'}")
        elif event.key() == Qt.Key_Escape:
            print("👋 Quitting...")
            self.close()
        else:
            super().keyPressEvent(event)
        
        self.update()
    
    def paintEvent(self, event):
        """Draw the Tetris board and ghost piece."""
        painter = QPainter(self)
        
        # Draw board background (semi-transparent)
        painter.fillRect(0, 0, 300, 600, QColor(0, 0, 0, 50))
        
        # Draw grid lines
        painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
        for i in range(11):  # 10 columns + 1
            x = i * 30
            painter.drawLine(x, 0, x, 600)
        for i in range(21):  # 20 rows + 1
            y = i * 30
            painter.drawLine(0, y, 300, y)
        
        if self.show_ghost:
            # Draw ghost piece
            shape = get_piece_shape(self.current_piece, self.current_rotation)
            color = get_piece_color(self.current_piece)
            
            # Center the piece
            center_x = 5
            center_y = 10
            
            for x, y in shape:
                # Convert to screen coordinates
                screen_x = (center_x + x) * 30
                screen_y = (center_y + y) * 30
                
                # Draw semi-transparent ghost piece
                ghost_color = QColor(*color, 128)
                painter.fillRect(screen_x, screen_y, 29, 29, ghost_color)
                
                # Draw outline
                painter.setPen(QPen(QColor(*color), 2))
                painter.drawRect(screen_x, screen_y, 29, 29)

def main():
    """Run the Tetris overlay test."""
    app = QApplication(sys.argv)
    
    overlay = TetrisTestOverlay()
    overlay.show()
    
    print("✅ Tetris ghost piece test started")
    print("🎮 You should see a Tetris board with a purple T-piece ghost")
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
