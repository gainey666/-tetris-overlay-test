"""
Window selection wizard for Tetris Overlay.
"""

import win32gui
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QLabel, QPushButton, QGroupBox, QMessageBox)
from PySide6.QtCore import Qt
from typing import List, Tuple, Optional

from ..core.config import OverlayConfig


class WindowPickerDialog(QDialog):
    """Dialog for selecting the target Tetris window."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Tetris Window")
        self.setFixedSize(600, 400)
        self.selected_hwnd: Optional[int] = None
        
        self._setup_ui()
        self._populate_windows()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel("Select the Tetris game window from the list below:")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Window list
        self.window_list = QListWidget()
        self.window_list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.window_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._populate_windows)
        button_layout.addWidget(self.refresh_btn)
        
        self.select_btn = QPushButton("Select")
        self.select_btn.clicked.connect(self.accept)
        self.select_btn.setEnabled(False)
        button_layout.addWidget(self.select_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def _populate_windows(self):
        """Populate the window list with visible windows."""
        self.window_list.clear()
        self.windows = self._get_visible_windows()
        
        for hwnd, title in self.windows:
            self.window_list.addItem(f"{hwnd}: {title}")
    
    def _get_visible_windows(self) -> List[Tuple[int, str]]:
        """Get list of visible windows."""
        windows = []
        
        def enum_callback(hwnd, windows_list):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and len(title) > 0:  # Skip empty titles
                    windows_list.append((hwnd, title))
            return True
        
        win32gui.EnumWindows(enum_callback, windows)
        return windows
    
    def _on_selection_changed(self):
        """Handle window selection change."""
        selected = self.window_list.currentItem()
        if selected:
            self.select_btn.setEnabled(True)
            # Extract hwnd from the item text
            text = selected.text()
            hwnd_str = text.split(":")[0]
            self.selected_hwnd = int(hwnd_str)
        else:
            self.select_btn.setEnabled(False)
            self.selected_hwnd = None
    
    def get_selected_hwnd(self) -> Optional[int]:
        """Get the selected window handle."""
        return self.selected_hwnd


def run_wizard() -> Optional[OverlayConfig]:
    """Run the window selection wizard."""
    app = None
    
    # Create QApplication if it doesn't exist
    from PySide6.QtWidgets import QApplication

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

    if not QApplication.instance():
        app = QApplication([])
    
    dialog = WindowPickerDialog()
    
    if dialog.exec() == QDialog.Accepted:
        hwnd = dialog.get_selected_hwnd()
        if hwnd:
            return OverlayConfig.create_default(hwnd)
    
    return None


if __name__ == "__main__":
    config = run_wizard()
    if config:
        print(f"Selected window: {config.target_hwnd}")
        print(f"Config: {config.json()}")
    else:
        print("No window selected")
