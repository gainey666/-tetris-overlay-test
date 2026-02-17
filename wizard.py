#!/usr/bin/env python3
"""
Setup Wizard for Tetris Overlay.
Placeholder implementation - will be expanded.
"""

import sys
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

class SetupWizard(QDialog):
    """First-run setup wizard for Tetris Overlay."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tetris Overlay Setup")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Welcome message
        welcome = QLabel("Welcome to Tetris Overlay!")
        welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome)
        
        # Placeholder for setup steps
        placeholder = QLabel("Setup wizard coming soon...")
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

def main():
    """Run the setup wizard."""
    app = QApplication(sys.argv)
    wizard = SetupWizard()
    wizard.exec()
    return 0

if __name__ == "__main__":
    sys.exit(main())
