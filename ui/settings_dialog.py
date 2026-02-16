"""Qt Settings dialog with live ghost preview."""

import sys
import re
from PySide6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QColorDialog, QSlider,
    QComboBox, QCheckBox, QKeySequenceEdit, QMessageBox
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPainter, QColor, QKeySequence
from .settings import Settings
from .settings_storage import load as load_settings, save as save_settings


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
    settings_changed = Signal(Settings)   # emitted after OK

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tetris Overlay – Settings")
        self.resize(500, 500)

        self._settings = load_settings()
        self._init_ui()
        self._populate_fields()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # ---- General tab -------------------------------------------------
        self.tab_general = QWidget()
        tl = QVBoxLayout(self.tab_general)

        # ROI fields
        self.left_roi_edit = QLineEdit()
        self.right_roi_edit = QLineEdit()
        tl.addWidget(QLabel("Left board ROI (x,y,w,h):"))
        tl.addWidget(self.left_roi_edit)
        tl.addWidget(QLabel("Right board ROI (x,y,w,h):"))
        tl.addWidget(self.right_roi_edit)

        # Prediction agent selector
        self.agent_combo = QComboBox()
        self.agent_combo.addItems(["dellacherie", "onnx", "simple", "mock"])
        tl.addWidget(QLabel("Prediction agent:"))
        tl.addWidget(self.agent_combo)

        self.tabs.addTab(self.tab_general, "General")

        # ---- Ghost tab ----------------------------------------------------
        self.tab_ghost = QWidget()
        tg = QVBoxLayout(self.tab_ghost)

        # Colour picker
        self.colour_btn = QPushButton("Pick colour")
        self.colour_btn.clicked.connect(self._pick_colour)
        tg.addWidget(self.colour_btn)

        # Opacity slider (0-100)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        tg.addWidget(QLabel("Opacity:"))
        tg.addWidget(self.opacity_slider)

        # Live preview
        self.preview = LivePreviewWidget()
        tg.addWidget(QLabel("Live preview:"))
        tg.addWidget(self.preview)

        self.tabs.addTab(self.tab_ghost, "Ghost")

        # ---- Hotkeys tab -------------------------------------------------
        self.tab_hotkeys = QWidget()
        th = QVBoxLayout(self.tab_hotkeys)

        self.toggle_edit = QKeySequenceEdit()
        self.open_edit = QKeySequenceEdit()
        self.debug_edit = QKeySequenceEdit()
        self.quit_edit = QKeySequenceEdit()
        self.calibrate_edit = QKeySequenceEdit()
        self.stats_edit = QKeySequenceEdit()

        th.addWidget(QLabel("Toggle overlay (default F9):"))
        th.addWidget(self.toggle_edit)
        th.addWidget(QLabel("Open settings (default F1):"))
        th.addWidget(self.open_edit)
        th.addWidget(QLabel("Debug logging (default F2):"))
        th.addWidget(self.debug_edit)
        th.addWidget(QLabel("Quit (Esc):"))
        th.addWidget(self.quit_edit)
        th.addWidget(QLabel("Calibrate (Ctrl+Alt+C):"))
        th.addWidget(self.calibrate_edit)
        th.addWidget(QLabel("Open Stats (Ctrl+Alt+S):"))
        th.addWidget(self.stats_edit)

        self.tabs.addTab(self.tab_hotkeys, "Hotkeys")

        # ---- Flags tab ----------------------------------------------------
        self.tab_flags = QWidget()
        tf = QVBoxLayout(self.tab_flags)

        self.combo_chk = QCheckBox("Show combo visual")
        self.b2b_chk = QCheckBox("Show B2B visual")
        tf.addWidget(self.combo_chk)
        tf.addWidget(self.b2b_chk)

        self.tabs.addTab(self.tab_flags, "Visual Flags")

        # ---- Buttons ------------------------------------------------------
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        self.apply_btn = QPushButton("Apply")
        btn_layout.addStretch()
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self._accept)
        self.apply_btn.clicked.connect(self._apply)
        self.cancel_btn.clicked.connect(self.reject)

        # Preview updates when colour/opacity changes
        self.opacity_slider.valueChanged.connect(self._update_preview)

    def _populate_fields(self):
        s = self._settings
        self.left_roi_edit.setText(",".join(map(str, s.roi_left)))
        self.right_roi_edit.setText(",".join(map(str, s.roi_right)))
        self.agent_combo.setCurrentText(s.prediction_agent)

        # Ghost colour
        r,g,b = s.ghost.colour
        self.colour_btn.setStyleSheet(
            f"background-color: rgb({r},{g},{b});"
        )
        self.opacity_slider.setValue(int(s.ghost.opacity*100))

        # Hotkeys
        self.toggle_edit.setKeySequence(QKeySequence(s.hotkeys.toggle_overlay))
        self.open_edit.setKeySequence(QKeySequence(s.hotkeys.open_settings))
        self.debug_edit.setKeySequence(QKeySequence(s.hotkeys.debug_logging))
        self.quit_edit.setKeySequence(QKeySequence(s.hotkeys.quit))
        self.calibrate_edit.setKeySequence(QKeySequence(s.hotkeys.calibrate))
        self.stats_edit.setKeySequence(QKeySequence(s.hotkeys.open_stats))

        # Visual flags
        self.combo_chk.setChecked(s.show_combo)
        self.b2b_chk.setChecked(s.show_b2b)

        self._update_preview()

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
            s.ghost = Settings.GhostStyle(colour=(r,g,b), opacity=self.opacity_slider.value()/100.0)

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
