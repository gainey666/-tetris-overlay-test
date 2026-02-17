"""Qt Settings dialog with live ghost preview."""

import sys
import re
import json
from PySide6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QColorDialog, QSlider,
    QComboBox, QCheckBox, QKeySequenceEdit, QMessageBox,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox,
    QTextEdit, QScrollArea
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPainter, QColor, QKeySequence
from .settings import Settings
from .settings_storage import load as load_settings, save as save_settings
import jsonschema


class LivePreviewWidget(QWidget):
    """Shows a 10×20 board + ghost piece with current colours."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 600)        # 30px per cell
        self._ghost_colour = QColor(255,255,255,128)
        self._piece_type = "T"
        self._rotation = 0

    def set_ghost_style(self, colour: tuple, opacity: float):
        r,g,b = colour
        a = int(opacity*255)
        self._ghost_colour = QColor(r,g,b,a)
        self.update()

    def set_piece_type(self, piece_type: str, rotation: int = 0):
        self._piece_type = piece_type
        self._rotation = rotation
        self.update()

    def paintEvent(self, event):
        cell = 30
        qp = QPainter(self)
        
        # Draw board grid
        qp.setPen(QColor(200, 200, 200))
        for x in range(11):
            qp.drawLine(x*cell, 0, x*cell, 20*cell)
        for y in range(21):
            qp.drawLine(0, y*cell, 10*cell, y*cell)

        # Draw ghost piece
        qp.setBrush(self._ghost_colour)
        qp.setPen(Qt.NoPen)
        
        # Simple T shape for preview
        ghost_cells = [(4,0), (3,1), (4,1), (5,1)]
        
        for cx,cy in ghost_cells:
            qp.drawRect(cx*cell, cy*cell, cell, cell)


class SettingsDialog(QDialog):
    """Settings dialog with tabs and live preview."""
    settings_changed = Signal(Settings)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tetris Overlay Settings")
        self.setModal(True)
        self.resize(800, 600)
        
        self.settings = load_settings()
        self._validation_errors = {}
        
        self._setup_ui()
        self._load_settings()
        
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self._create_general_tab()
        self._create_ghost_tab()
        self._create_hotkeys_tab()
        self._create_visual_flags_tab()
        self._create_advanced_tab()
        
        layout.addWidget(self.tabs)
        
        # Dialog buttons
        buttons = QHBoxLayout()
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self._reset_to_defaults)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply_settings)
        
        self.ok_btn = QPushButton("OK")
        self.ok_btn.clicked.connect(self._ok_clicked)
        
        buttons.addWidget(self.reset_btn)
        buttons.addStretch()
        buttons.addWidget(self.cancel_btn)
        buttons.addWidget(self.apply_btn)
        buttons.addWidget(self.ok_btn)
        
        layout.addLayout(buttons)
        
    def _create_general_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ROI Group
        roi_group = QGroupBox("Region of Interest")
        roi_layout = QFormLayout(roi_group)
        
        self.roi_left_edit = QLineEdit()
        self.roi_left_edit.setPlaceholderText("x,y,width,height")
        roi_layout.addRow("Left ROI:", self.roi_left_edit)
        
        self.roi_right_edit = QLineEdit()
        self.roi_right_edit.setPlaceholderText("x,y,width,height")
        roi_layout.addRow("Right ROI:", self.roi_right_edit)
        
        # Agent Selection
        self.agent_combo = QComboBox()
        self.agent_combo.addItems(["Dellacherie", "Bertilsson"])
        agent_layout = QFormLayout()
        agent_layout.addRow("Prediction Agent:", self.agent_combo)
        
        agent_group = QGroupBox("AI Agent")
        agent_group.setLayout(agent_layout)
        
        layout.addWidget(roi_group)
        layout.addWidget(agent_group)
        layout.addStretch()
        
        self.tabs.addTab(widget, "General")
        
    def _create_ghost_tab(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Left side - Controls
        controls = QVBoxLayout()
        
        # Color picker
        color_group = QGroupBox("Ghost Color")
        color_layout = QFormLayout(color_group)
        
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self._choose_color)
        color_layout.addRow("Color:", self.color_btn)
        
        # Opacity slider
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.valueChanged.connect(self._update_opacity_label)
        self.opacity_label = QLabel("50%")
        
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        color_layout.addRow("Opacity:", opacity_layout)
        
        controls.addWidget(color_group)
        
        # Visual effects
        effects_group = QGroupBox("Visual Effects")
        effects_layout = QFormLayout(effects_group)
        
        self.outline_only_cb = QCheckBox("Outline Only")
        effects_layout.addRow("Style:", self.outline_only_cb)
        
        self.fade_effect_cb = QCheckBox("Fade Animation")
        effects_layout.addRow("Effects:", self.fade_effect_cb)
        
        controls.addWidget(effects_group)
        controls.addStretch()
        
        # Right side - Live preview
        self.preview = LivePreviewWidget()
        preview_group = QGroupBox("Live Preview")
        preview_layout = QVBoxLayout(preview_group)
        preview_layout.addWidget(self.preview)
        
        layout.addLayout(controls, 1)
        layout.addWidget(preview_group, 2)
        
        self.tabs.addTab(widget, "Ghost")
        
    def _create_hotkeys_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        hotkeys_group = QGroupBox("Hotkey Configuration")
        hotkeys_layout = QFormLayout(hotkeys_group)
        
        self.hotkey_edits = {}
        hotkey_names = [
            ("toggle_overlay", "Toggle Overlay"),
            ("open_settings", "Open Settings"),
            ("open_stats", "Open Statistics"),
            ("debug_logging", "Debug Logging"),
            ("quit", "Quit Application"),
            ("calibrate", "Calibrate ROIs")
        ]
        
        for key, label in hotkey_names:
            edit = QKeySequenceEdit()
            self.hotkey_edits[key] = edit
            hotkeys_layout.addRow(label + ":", edit)
        
        layout.addWidget(hotkeys_group)
        layout.addStretch()
        
        self.tabs.addTab(widget, "Hotkeys")
        
    def _create_visual_flags_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        flags_group = QGroupBox("Visual Flags")
        flags_layout = QFormLayout(flags_group)
        
        self.show_combo_cb = QCheckBox("Show Combo Indicator")
        flags_layout.addRow("Combo:", self.show_combo_cb)
        
        self.show_b2b_cb = QCheckBox("Show B2B Indicator")
        flags_layout.addRow("B2B:", self.show_b2b_cb)
        
        self.show_fps_cb = QCheckBox("Show FPS Counter")
        flags_layout.addRow("Performance:", self.show_fps_cb)
        
        self.debug_mode_cb = QCheckBox("Debug Mode")
        flags_layout.addRow("Debug:", self.debug_mode_cb)
        
        layout.addWidget(flags_group)
        layout.addStretch()
        
        self.tabs.addTab(widget, "Visual Flags")
        
    def _create_advanced_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Advanced settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout(advanced_group)
        
        self.fps_spinbox = QSpinBox()
        self.fps_spinbox.setRange(10, 60)
        self.fps_spinbox.setValue(30)
        advanced_layout.addRow("Target FPS:", self.fps_spinbox)
        
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setRange(100, 5000)
        self.timeout_spinbox.setValue(1000)
        advanced_layout.addRow("Frame Timeout (ms):", self.timeout_spinbox)
        
        layout.addWidget(advanced_group)
        
        # Validation status
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setMaximumHeight(100)
        
        validation_group = QGroupBox("Validation Status")
        validation_layout = QVBoxLayout(validation_group)
        validation_layout.addWidget(self.validation_text)
        
        layout.addWidget(validation_group)
        layout.addStretch()
        
        self.tabs.addTab(widget, "Advanced")
        
    def _choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self._ghost_color = (color.red(), color.green(), color.blue())
            self.color_btn.setStyleSheet(f"background-color: {color.name()}")

    def _pick_colour(self):
        current_color = self.colour_btn.palette().color(self.colour_btn.backgroundRole())
        col = QColorDialog.getColor(current_color, self)
        if col.isValid():
            self.colour_btn.setStyleSheet(
                f"background-color: {col.name()};"
            )
            self._update_preview()

    def _update_preview(self):
        # Extract colour + opacity from UI and push to preview
        style = self.colour_btn.styleSheet()
        # Parse rgb from stylesheet `rgb(r,g,b)`
        m = re.search(r"rgb\((\d+),(\d+),(\d+)\)", style)
        if not m:
            return
        colour = tuple(map(int, m.groups()))
        opacity = self.opacity_slider.value() / 100.0
        self.preview.set_ghost_style(colour, opacity)

    def _collect_current_settings(self) -> Settings:
        # Parse ROI fields
        def _parse_rect(txt):
            try:
                nums = [int(v.strip()) for v in txt.split(",")]
                if len(nums) != 4:
                    raise ValueError
                return tuple(nums)
            except Exception:
                raise ValueError(f"Bad ROI: {txt}")

        s = Settings()
        s.roi_left = _parse_rect(self.left_roi_edit.text())
        s.roi_right = _parse_rect(self.right_roi_edit.text())
        s.prediction_agent = self.agent_combo.currentText()

        # Ghost style
        style = self.colour_btn.styleSheet()
        m = re.search(r"rgb\((\d+),(\d+),(\d+)\)", style)
        if m:
            r,g,b = map(int, m.groups())
            s.ghost = GhostStyle(colour=(r,g,b), opacity=self.opacity_slider.value()/100.0)

        # Hotkeys
        hk = Settings.Hotkeys()
        hk.toggle_overlay = self.toggle_edit.keySequence().toString().lower()
        hk.open_settings = self.open_edit.keySequence().toString().lower()
        hk.debug_logging = self.debug_edit.keySequence().toString().lower()
        hk.quit = self.quit_edit.keySequence().toString().lower()
        hk.calibrate = self.calibrate_edit.keySequence().toString().lower()
        hk.open_stats = self.stats_edit.keySequence().toString().lower()
        s.hotkeys = hk

        # Visual flags
        s.show_combo = self.combo_chk.isChecked()
        s.show_b2b = self.b2b_chk.isChecked()
        
        return s

    def _apply(self):
        try:
            new = self._collect_current_settings()
        except ValueError as e:
            QMessageBox.warning(self, "Invalid input", str(e))
            return
        save_settings(new)
        self.settings_changed.emit(new)

    def _accept(self):
        self._apply()
        self.accept()

    def _reset_to_defaults(self):
        """Reset all settings to defaults."""
        reply = QMessageBox.question(
            self, 
            "Reset to Defaults", 
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            from .settings import Settings
            default_settings = Settings()
            self._settings = default_settings
            self._populate_fields()
            self._update_preview()
