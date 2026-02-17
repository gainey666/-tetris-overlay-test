"""
Settings dialog for Tetris Overlay.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QSlider, QPushButton, QColorDialog, QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from ..core.config import OverlayConfig

# Import our logger bridge
try:
    import logger_bridge as log

# Import global function tracer
try:
    from tracer.client import safe_trace_calls as trace_calls
    TRACER_AVAILABLE = True
except ImportError:
    TRACER_AVAILABLE = False

    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False


class SettingsDialog(QDialog):
    """Settings dialog for configuring the overlay."""
    
    def __init__(self, config: OverlayConfig, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tetris Overlay Settings")
        self.setFixedSize(400, 300)
        
        self.config = config
        self._setup_ui()
        
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Opacity setting
        opacity_group = QGroupBox("Opacity")
        opacity_layout = QVBoxLayout()
        
        self.opacity_label = QLabel(f"Opacity: {int(self.config.opacity * 100)}%")
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(10)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(int(self.config.opacity * 100))
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        
        opacity_layout.addWidget(self.opacity_label)
        opacity_layout.addWidget(self.opacity_slider)
        opacity_group.setLayout(opacity_layout)
        layout.addWidget(opacity_group)
        
        # Color setting
        color_group = QGroupBox("Ghost Color")
        color_layout = QHBoxLayout()
        
        self.color_button = QPushButton("Choose Color")
        self.color_button.clicked.connect(self._on_color_changed)
        self.color_label = QLabel(self.config.ghost_colour)
        self.color_label.setStyleSheet(f"background-color: {self.config.ghost_colour}")
        
        color_layout.addWidget(self.color_button)
        color_layout.addWidget(self.color_label)
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _on_opacity_changed(self, value):
        """Handle opacity slider change."""
        self.config.opacity = value / 100.0
        self.opacity_label.setText(f"Opacity: {value}%")
    
    def _on_color_changed(self):
        """Handle color button click."""
        color = QColorDialog.getColor(QColor(self.config.ghost_colour), self)
        if color.isValid():
            self.config.ghost_colour = color.name()
            self.color_label.setStyleSheet(f"background-color: {color.name()}")
    
    def get_config(self) -> OverlayConfig:
        """Get the updated configuration."""
        return self.config
