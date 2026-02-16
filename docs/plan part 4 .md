Project Plan – Settings GUI + Statistics Tracker (No Replay)
Target implementation time: ~45 minutes of continuous coding (≈ 3 working blocks).
Audience: AI‑assistant (e.g., “Windsurf IDE Cursor AI”) that will write the code with minimal human interaction.

Table of Contents
Goal Overview
Prerequisites & Dependencies
High‑Level Architecture
File & Folder Layout
Step‑by‑Step Implementation
5.1 Create a Settings data model
5.2 Persist Settings with TinyDB
5.3 Build the Qt Settings Dialog
5.4 Hook Settings into the Overlay Core
5.5 Add a Live Ghost Preview Widget
5.6 Expose a “Open Settings” hot‑key
5.7 Create the Statistics DB schema
5.8 Emit per‑frame stats from process_frames
5.9 Finalize match record on game‑over
5.10 Build the Stats Dashboard UI
5.11 Export CSV/JSON from the Dashboard
5.12 Add unit & UI tests
5.13 Extend CI workflow
Testing Checklist
Final Verification / Demo Steps
Estimated Time Breakdown
1️⃣ Goal Overview
Settings GUI – a non‑modal Qt window that lets the user edit:
ROI paths (left/right board rectangles)
Hot‑key map (F9 toggle, F1 settings, etc.)
Prediction‑agent selection (dellacherie / onnx / simple / mock)
Ghost‑piece colour & opacity
B2B / Combo visual toggles
Live preview inside the settings dialog that instantly shows the ghost shape with the chosen colour/opacity.
Statistics Tracker – automatically records per‑frame data into an SQLite DB, and provides a Qt dashboard that displays:
Summary of each match (score, lines, max combo, B2B streak, piece distribution)
Charts (score over time, combo streak, piece histogram)
Export to CSV/JSON for external analysis.
2️⃣ Prerequisites & Dependencies
Dependency	Install command	Reason
Python ≥ 3.11	python -m venv .venv && source .venv/bin/activate	Base interpreter
PySide6 (Qt bindings)	pip install pyside6	UI framework
tinydb (JSON‑backed DB for settings)	pip install tinydb	Simple persistent store
SQLModel (SQLite ORM)	pip install sqlmodel	Structured stats storage
matplotlib (charts)	pip install matplotlib	Dashboard visuals
pytest‑qt (UI tests)	pip install pytest-qt	Test the Qt UI
Other project deps (already in requirements.txt)	pip install -r requirements.txt	Existing overlay code
Add these to pyproject.toml / requirements.txt if they are not present.

3️⃣ High‑Level Architecture
+---------------------+        +----------------------------+
|  Settings UI (Qt)   | <----> |   TinyDB (settings.json)   |
+----------+----------+        +----------------------------+
           ^                               |
           | hot‑key (F1)                  | read on startup
           v                               v
+---------------------+        +----------------------------+
| Core Overlay Engine | <----> | SQLite (stats.db)           |
| run_overlay_core.py|        +----------------------------+
|   - Captures frames|                ^   ^
|   - Calls agents  |                |   |
|   - Emits events  |                |   |
+---------------------+        +----------------------------+
          ^                                  |
          | UI Dashboard (Qt)                 |
          +-----------------------------------+
Settings UI → writes JSON file via TinyDB.
Overlay core reads that file at start, and subscribes to changes (via a simple observer).
Overlay core emits StatEvent objects each frame → inserted into stats.db.
Dashboard UI queries stats.db and visualises the data.
4️⃣ File & Folder Layout
tetris_overlay_test/
│
├─ src/
│   ├─ agents/                # unchanged
│   └─ ...                    # existing modules
│
├─ ui/
│   ├─ settings_dialog.py     # Qt dialog + preview widget
│   └─ stats_dashboard.py    # Qt window + Matplotlib canvases
│
├─ stats/
│   ├─ db.py                  # SQLite init, models (SQLModel)
│   └─ collector.py          # helper to emit StatEvent from core
│
├─ config/
│   └─ config.json            # add "prediction_agent" key if missing
│
├─ settings.json              # TinyDB file (auto‑created on first run)
├─ stats.db                   # SQLite file (auto‑created)
│
├─ tests/
│   ├─ test_settings.py
│   ├─ test_stats_db.py
│   └─ test_ui_dashboard.py   # pytest‑qt
│
├─ .github/
│   └─ workflows/
│        └─ ci.yml           # extended CI (Qt, ffmpeg not needed)
│
└─ run_overlay_core.py       # will be updated to load settings & emit stats
5️⃣ Step‑by‑Step Implementation
NOTE: The AI should work top‑to‑bottom in the order listed. Each block includes:

File to create / modify
Core code skeleton (inline)
Brief description of what to implement
Time‑box estimate (≈ 5 min max per block).
5.1 Create a Settings data model
File: ui/settings_model.py (or ui/settings.py if you prefer a single file).
Contents: Python dataclass (or plain dict) that mirrors the JSON schema.
# ui/settings.py
from dataclasses import dataclass, field
from typing import Dict, Tuple

# ROI is stored as (left, top, width, height)
Rect = Tuple[int, int, int, int]

@dataclass
class GhostStyle:
    colour: Tuple[int, int, int] = (255, 255, 255)   # white
    opacity: float = 0.5                           # 0‑1

@dataclass
class Hotkeys:
    toggle_overlay: str = "f9"
    open_settings: str = "f1"
    debug_logging: str = "f2"
    quit: str = "esc"
    calibrate: str = "ctrl+alt+c"

@dataclass
class Settings:
    roi_left: Rect = (0, 0, 640, 360)
    roi_right: Rect = (0, 0, 640, 360)
    prediction_agent: str = "dellacherie"
    ghost: GhostStyle = GhostStyle()
    hotkeys: Hotkeys = Hotkeys()
    show_combo: bool = True
    show_b2b: bool = True
Implement a to_dict() / from_dict() helper if you want explicit conversion.

Time: 4 min.

5.2 Persist Settings with TinyDB
File: ui/settings_storage.py
Goal: Load settings on start, write on change, expose get() / set() API.
# ui/settings_storage.py
from tinydb import TinyDB, Query
from pathlib import Path
from .settings import Settings

DB_PATH = Path("settings.json")

def _db():
    return TinyDB(DB_PATH)

def load() -> Settings:
    if not DB_PATH.exists():
        # write defaults
        Settings().to_dict()  # will be defined below
        save(Settings())
    data = _db().all()[0]          # tinydb stores a list of docs
    return Settings(**data)

def save(settings: Settings) -> None:
    db = _db()
    db.truncate()                  # keep only one document
    db.insert(settings.to_dict())
Add to_dict method to Settings:
# inside Settings dataclass
def to_dict(self):
    return {
        "roi_left": list(self.roi_left),
        "roi_right": list(self.roi_right),
        "prediction_agent": self.prediction_agent,
        "ghost": {"colour": list(self.ghost.colour), "opacity": self.ghost.opacity},
        "hotkeys": self.hotkeys.__dict__,
        "show_combo": self.show_combo,
        "show_b2b": self.show_b2b,
    }
Time: 6 min.

5.3 Build the Qt Settings Dialog
File: ui/settings_dialog.py
Key parts:
SettingsDialog(QDialog) with tabs (QTabWidget).
Each tab contains appropriate widgets (QLineEdit for ROI, QComboBox for agent, QColorDialog button for colour, QSlider for opacity, QKeySequenceEdit for hot‑keys).
A LivePreviewWidget (sub‑class QWidget) that draws a dummy 10×20 board and calls OverlayRenderer.draw_ghost on a QPixmap.
apply_changes() writes to settings_storage.save() and emits a settings_changed signal.
# ui/settings_dialog.py
import sys
from PySide6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QColorDialog, QSlider,
    QComboBox, QCheckBox, QKeySequenceEdit, QMessageBox
)
from PySide6.QtCore import Signal, Qt, QSize
from PySide6.QtGui import QPainter, QColor
from .settings import Settings
from .settings_storage import load as load_settings, save as save_settings
from ..overlay_renderer import OverlayRenderer   # reuse ghost‑drawing logic


class LivePreviewWidget(QWidget):
    """Shows a 10×20 board + ghost piece with current colours."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 600)        # 30 px per cell
        self._ghost_colour = QColor(255,255,255,128)

    def set_ghost_style(self, colour: tuple, opacity: float):
        r,g,b = colour
        a = int(opacity*255)
        self._ghost_colour = QColor(r,g,b,a)
        self.update()

    def paintEvent(self, event):
        cell = 30
        qp = QPainter(self)
        # draw board grid
        qp.setPen(Qt.gray)
        for x in range(11):
            qp.drawLine(x*cell, 0, x*cell, 20*cell)
        for y in range(21):
            qp.drawLine(0, y*cell, 10*cell, y*cell)

        # draw a dummy ghost (just a 4‑cell piece, rotated 0)
        qp.setBrush(self._ghost_colour)
        qp.setPen(Qt.NoPen)
        # simple "T" shape example – you could import PIECE_SHAPES if you want all rotations
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

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _init_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # ---- General tab -------------------------------------------------
        self.tab_general = QWidget()
        tl = QVBoxLayout(self.tab_general)

        # ROI fields (two rows: left / right)
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

        # Opacity slider (0‑100)
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(int(self._settings.ghost.opacity*100))
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

        # preview updates when colour/opacity changes
        self.opacity_slider.valueChanged.connect(self._update_preview)

    # ------------------------------------------------------------------
    # Populate fields from loaded Settings
    # ------------------------------------------------------------------
    def _populate_fields(self):
        s = self._settings
        self.left_roi_edit.setText(",".join(map(str, s.roi_left)))
        self.right_roi_edit.setText(",".join(map(str, s.roi_right)))
        self.agent_combo.setCurrentText(s.prediction_agent)

        # ghost colour
        r,g,b = s.ghost.colour
        self.colour_btn.setStyleSheet(
            f"background-color: rgb({r},{g},{b});"
        )
        self.opacity_slider.setValue(int(s.ghost.opacity*100))

        # hotkeys
        self.toggle_edit.setKeySequence(s.hotkeys.toggle_overlay)
        self.open_edit.setKeySequence(s.hotkeys.open_settings)
        self.debug_edit.setKeySequence(s.hotkeys.debug_logging)
        self.quit_edit.setKeySequence(s.hotkeys.quit)
        self.calibrate_edit.setKeySequence(s.hotkeys.calibrate)

        # visual flags
        self.combo_chk.setChecked(s.show_combo)
        self.b2b_chk.setChecked(s.show_b2b)

        self._update_preview()

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def _pick_colour(self):
        col = QColorDialog.getColor()
        if col.isValid():
            self.colour_btn.setStyleSheet(
                f"background-color: {col.name()};"
            )
            self._update_preview()

    def _update_preview(self):
        # Extract colour + opacity from UI and push to preview
        style = self.colour_btn.styleSheet()
        # parse rgb from stylesheet `rgb(r,g,b)`
        import re
        m = re.search(r"rgb\((\d+),(\d+),(\d+)\)", style)
        if not m:
            return
        colour = tuple(map(int, m.groups()))
        opacity = self.opacity_slider.value() / 100.0
        self.preview.set_ghost_style(colour, opacity)

    def _collect_current_settings(self) -> Settings:
        # Parse ROI fields (very forgiving)
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

        # ghost style
        style = self.colour_btn.styleSheet()
        m = re.search(r"rgb\((\d+),(\d+),(\d+)\)", style)
        r,g,b = map(int, m.groups())
        s.ghost = Settings.GhostStyle(colour=(r,g,b), opacity=self.opacity_slider.value()/100.0)

        # hotkeys
        hk = Settings.Hotkeys()
        hk.toggle_overlay = self.toggle_edit.keySequence().toString()
        hk.open_settings = self.open_edit.keySequence().toString()
        hk.debug_logging = self.debug_edit.keySequence().toString()
        hk.quit = self.quit_edit.keySequence().toString()
        hk.calibrate = self.calibrate_edit.keySequence().toString()
        s.hotkeys = hk

        # visual flags
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
        # also update the preview immediately
        self._update_preview()

    def _accept(self):
        self._apply()
        self.accept()
Key points for the AI:

Use QKeySequenceEdit (Qt 6) for hot‑key editing.
Emit settings_changed signal so the overlay core can react without restarting.
The preview widget draws a static T‑shape; you can later import PIECE_SHAPES to render any rotation, but for a quick MVP the placeholder is enough.
Time: 10 min.

5.4 Hook Settings into the Overlay Core
File: run_overlay_core.py (modify near the top).
Tasks:
Import ui.settings_storage.load → CURRENT_SETTINGS.
Register the hot‑keys based on the loaded settings (instead of the hard‑coded ones).
Subscribe to settings_changed from the dialog (via a global signal or a simple callback).
Add a small observer class (or just a global mutable CURRENT_SETTINGS) that other modules can read.
# At the top of run_overlay_core.py
from ui.settings_storage import load as load_settings, save as save_settings
from ui.settings_dialog import SettingsDialog

CURRENT_SETTINGS = load_settings()

def _register_dynamic_hotkeys():
    # clear previous (keyboard library does not have a clear, so we restart)
    keyboard.unhook_all()
    hk = CURRENT_SETTINGS.hotkeys
    keyboard.add_hotkey(hk.toggle_overlay, toggle_overlay)
    keyboard.add_hotkey(hk.open_settings, lambda: SettingsDialog().exec())
    keyboard.add_hotkey(hk.debug_logging, _toggle_debug_logging)
    keyboard.add_hotkey(hk.quit, graceful_exit)
    keyboard.add_hotkey(hk.calibrate, start_calibrator)

_register_dynamic_hotkeys()

# Connect the Settings dialog signal to refresh hotkeys & ghost style
def _on_settings_changed(new_settings):
    global CURRENT_SETTINGS
    CURRENT_SETTINGS = new_settings
    _register_dynamic_hotkeys()
    # push new ghost style to the renderer (if it exists)
    if _OVERLAY_RENDERER:
        _OVERLAY_RENDERER.update_ghost_style(
            colour=new_settings.ghost.colour,
            opacity=new_settings.ghost.opacity,
        )
Add a helper method to OverlayRenderer:

# overlay_renderer.py
class OverlayRenderer:
    # existing code …

    def update_ghost_style(self, colour: tuple[int, int, int], opacity: float):
        self._ghost_colour = (*colour, int(opacity*255))
The process_frames function should now reference CURRENT_SETTINGS instead of hard‑coded values (e.g., CURRENT_SETTINGS.prediction_agent).

Time: 6 min.

5.5 Add a Live Ghost Preview Widget (already included above)
The preview is defined in LivePreviewWidget. No extra work is required beyond what’s in 5.3, but make sure OverlayRenderer.draw_ghost accepts colour/opacity parameters so the preview can reuse the same logic.

# overlay_renderer.py – modify draw_ghost signature
def draw_ghost(self, surface, column, rotation, piece_type="T",
               colour=None, opacity=0.5):
    # colour defaults to self._ghost_colour if None
    colour = colour or self._ghost_colour
    # use the piece shape from src.agents.prediction_agent_dellacherie.PIECE_SHAPES
    from src.agents.prediction_agent_dellacherie import PIECE_SHAPES
    shape = PIECE_SHAPES.get(piece_type, [[]])[rotation]
    cell_w, cell_h = self.cell_w, self.cell_h  # expose as class attrs
    for x_off, y_off in shape:
        x = (column + x_off) * cell_w
        y = (20 - y_off - 1) * cell_h   # flip Y to match board origin
        ghost_surf = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
        ghost_surf.fill(colour)          # rgba tuple
        surface.blit(ghost_surf, (x, y))
Time: 4 min.

5.6 Expose a “Open Settings” hot‑key (already covered)
Make sure the hot‑key uses the value from CURRENT_SETTINGS.hotkeys.open_settings. The dialog will be created on demand (SettingsDialog().exec()).

Time: 0 min (already in 5.4).

5.7 Create the Statistics DB schema
File: stats/db.py
# stats/db.py
from sqlmodel import SQLModel, Field, create_engine, Session, select
from pathlib import Path

DB_PATH = Path("stats.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

class Match(SQLModel, table=True):
    id: str = Field(primary_key=True)   # uuid4 string
    start_ts: float
    end_ts: float | None = None
    agent: str
    total_score: int = 0
    total_lines: int = 0
    max_combo: int = 0
    max_b2b: int = 0

class Event(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    match_id: str = Field(foreign_key="match.id")
    frame: int
    ts: float
    piece: str
    orientation: int
    lines_cleared: int
    combo: int
    b2b: bool
    tspin: bool
    latency_ms: float

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    return Session(engine)
Call init_db() once at program start (e.g., at the bottom of run_overlay_core.py).

Time: 5 min.

5.8 Emit per‑frame stats from process_frames
File: stats/collector.py
# stats/collector.py
import time
import uuid
from .db import get_session, Match, Event

_current_match_id: str | None = None
_frame_counter = 0

def start_new_match(agent_name: str):
    global _current_match_id, _frame_counter
    _current_match_id = str(uuid.uuid4())
    _frame_counter = 0
    with get_session() as s:
        s.add(Match(id=_current_match_id, start_ts=time.time(), agent=agent_name))
        s.commit()

def end_current_match():
    global _current_match_id
    if not _current_match_id:
        return
    with get_session() as s:
        stmt = select(Match).where(Match.id == _current_match_id)
        m = s.exec(stmt).one()
        m.end_ts = time.time()
        s.add(m)
        s.commit()
    _current_match_id = None

def record_event(frame: int,
                 piece: str,
                 orientation: int,
                 lines_cleared: int,
                 combo: int,
                 b2b: bool,
                 tspin: bool,
                 latency_ms: float):
    if not _current_match_id:
        return
    with get_session() as s:
        s.add(Event(
            match_id=_current_match_id,
            frame=frame,
            ts=time.time(),
            piece=piece,
            orientation=orientation,
            lines_cleared=lines_cleared,
            combo=combo,
            b2b=b2b,
            tspin=tspin,
            latency_ms=latency_ms
        ))
        s.commit()
Integrate into process_frames (near the end of the function, after the prediction is made):

# after drawing ghost and before FRAME_COUNTER += 1
from stats.collector import record_event

record_event(
    frame=FRAME_COUNTER,
    piece=pred["piece"],          # now obtained from piece_detector
    orientation=pred["target_rot"],
    lines_cleared=shared.get("lines_cleared", 0),   # you may need to compute it
    combo=prediction_agent.combo,   # if the agent tracks combo
    b2b=pred.get("is_b2b", False),
    tspin=pred.get("is_tspin", False),
    latency_ms=(datetime.datetime.utcnow().timestamp() - capture_start_ts) * 1000
)
Make sure process_frames measures capture_start_ts = time.time() right before the board capture.

Time: 8 min.

5.9 Finalize match record on game‑over
Trigger: When the overlay receives the Esc hot‑key, call stats.collector.end_current_match().
Update run_overlay_core.py:
def _graceful_exit():
    from stats.collector import end_current_match
    end_current_match()
    logging.info("Esc pressed – shutting down")
    from tetris_overlay_core import graceful_exit
    graceful_exit()
Also start a new match when the overlay boots (or when a new game is detected – for MVP just start on program start):

from stats.collector import start_new_match
start_new_match(CURRENT_SETTINGS.prediction_agent)
Time: 3 min.

5.10 Build the Stats Dashboard UI
File: ui/stats_dashboard.py
Key UI elements:

Match list (QTableView connected to a custom QAbstractTableModel that reads Match rows).
Detail area – when a row is selected, show three Matplotlib canvases:
Score over time (line plot)
Combo streak (bars)
Piece distribution (pie chart)
Export button → write CSV of all events for the selected match.
Skeleton:

# ui/stats_dashboard.py
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView,
    QPushButton, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from stats.db import get_session, Match, Event, init_db

class MatchTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()
        self._data = []
        self._load()

    def _load(self):
        with get_session() as s:
            self._data = s.exec(select(Match)).all()

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return 5   # columns: ID, start, end, score, lines

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        row = self._data[index.row()]
        col = index.column()
        if col == 0: return row.id[:8]   # short uuid
        if col == 1: return f"{row.start_ts:.2f}"
        if col == 2: return f"{(row.end_ts or 0):.2f}"
        if col == 3: return row.total_score
        if col == 4: return row.total_lines

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ["ID", "Start", "End", "Score", "Lines"][section]
        return str(section)

class StatsDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tetris Overlay – Statistics")
        self.resize(900, 600)

        layout = QHBoxLayout(self)

        # ---------- Left: match table ----------
        self.table = QTableView()
        self.model = MatchTableModel()
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.SingleSelection)
        layout.addWidget(self.table, 1)

        # ---------- Right: charts ----------
        right = QVBoxLayout()
        self.fig_score, self.ax_score = plt.subplots()
        self.canvas_score = FigureCanvas(self.fig_score)
        right.addWidget(self.canvas_score, 2)

        self.fig_combo, self.ax_combo = plt.subplots()
        self.canvas_combo = FigureCanvas(self.fig_combo)
        right.addWidget(self.canvas_combo, 2)

        self.fig_piece, self.ax_piece = plt.subplots()
        self.canvas_piece = FigureCanvas(self.fig_piece)
        right.addWidget(self.canvas_piece, 2)

        # ---------- Export button ----------
        btn_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export CSV")
        btn_layout.addStretch()
        btn_layout.addWidget(self.export_btn)
        right.addLayout(btn_layout)

        layout.addLayout(right, 3)

        # ---------- Signals ----------
        self.table.selectionModel().currentChanged.connect(self._load_detail)
        self.export_btn.clicked.connect(self._export_csv)

    # ------------------------------------------------------------------
    def _load_detail(self, current, previous):
        if not current.isValid():
            return
        match_id = self.model._data[current.row()].id
        with get_session() as s:
            events = s.exec(select(Event).where(Event.match_id == match_id)).all()

        # Score over time (cumulative)
        frames = [e.frame for e in events]
        scores = [e.lines_cleared for e in events]  # you can replace with a running total
        self.ax_score.clear()
        self.ax_score.plot(frames, scores, label="Lines per frame")
        self.ax_score.set_xlabel("Frame")
        self.ax_score.set_ylabel("Lines cleared")
        self.ax_score.legend()
        self.canvas_score.draw()

        # Combo streak
        combos = [e.combo for e in events]
        self.ax_combo.clear()
        self.ax_combo.bar(frames, combos, width=1, color="green")
        self.ax_combo.set_xlabel("Frame")
        self.ax_combo.set_ylabel("Combo")
        self.canvas_combo.draw()

        # Piece distribution
        from collections import Counter
        cnt = Counter(e.piece for e in events)
        pieces, counts = zip(*cnt.items())
        self.ax_piece.clear()
        self.ax_piece.pie(counts, labels=pieces, autopct="%1.1f%%")
        self.canvas_piece.draw()

    # ------------------------------------------------------------------
    def _export_csv(self):
        if not self.table.selectionModel().hasSelection():
            QMessageBox.warning(self, "No match selected", "Select a match first.")
            return
        idx = self.table.selectionModel().currentIndex()
        match_id = self.model._data[idx.row()].id
        with get_session() as s:
            events = s.exec(select(Event).where(Event.match_id == match_id)).all()
        if not events:
            QMessageBox.information(self, "Empty", "No events to export.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", f"{match_id}.csv", "CSV Files (*.csv)")
        if not path:
            return
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["frame","ts","piece","orientation","lines_cleared",
                             "combo","b2b","tspin","latency_ms"])
            for e in events:
                writer.writerow([e.frame, e.ts, e.piece, e.orientation,
                                 e.lines_cleared, e.combo,
                                 int(e.b2b), int(e.tspin), e.latency_ms])
        QMessageBox.information(self, "Exported", f"Saved to {path}")
Make the dashboard launchable from a hot‑key (e.g., Ctrl+Alt+S). Add that binding to the dynamic hot‑key registration in run_overlay_core.py.
Time: 12 min (including imports and a quick sanity test).

5.11 Export CSV/JSON from the Dashboard (already done)
The _export_csv method above writes a straightforward CSV. If you want JSON as well, duplicate the loop with json.dump([e.__dict__ for e in events], f, indent=2).

Time: 2 min (optional).

5.12 Add unit & UI tests
File: tests/test_settings.py
def test_settings_roundtrip(tmp_path):
    from ui.settings_storage import save, load, Settings
    s = Settings()
    s.roi_left = (1,2,640,360)
    s.ghost.colour = (10,20,30)
    s.ghost.opacity = 0.7
    save(s)
    loaded = load()
    assert loaded.roi_left == s.roi_left
    assert loaded.ghost.colour == s.ghost.colour
    assert loaded.ghost.opacity == s.ghost.opacity
File: tests/test_stats_db.py
def test_match_event_cycle(tmp_path):
    from stats.db import init_db, get_session, Match, Event
    from stats.collector import start_new_match, record_event, end_current_match
    # use a temporary DB file
    from stats import db
    db.DB_PATH = tmp_path / "stats.db"
    init_db()

    start_new_match("simple")
    for i in range(5):
        record_event(frame=i, piece="T", orientation=0,
                     lines_cleared=0, combo=i, b2b=False, tspin=False, latency_ms=10.0)
    end_current_match()

    with get_session() as s:
        assert s.exec(select(Match)).first() is not None
        evs = s.exec(select(Event)).all()
        assert len(evs) == 5
        assert evs[-1].combo == 4
File: tests/test_ui_dashboard.py (pytest‑qt)
def test_dashboard_load(qtbot):
    from ui.stats_dashboard import StatsDashboard
    w = StatsDashboard()
    qtbot.addWidget(w)
    # just make sure it shows without crashing (requires a DB with at least one match)
    w.show()
    qtbot.waitExposed(w)
Add pytest-qt to requirements.txt (or pyproject.toml).

Time: 8 min.

5.13 Extend CI workflow
Edit .github/workflows/ci.yml:

name: CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install PySide6 pytest-qt  # UI deps
      - name: Run tests
        run: |
          pytest -v tests/
No need for ffmpeg now (replay removed).

Time: 2 min.

6️⃣ Testing Checklist (run after implementation)
Test	Command	Expected result
Unit settings round‑trip	pytest -q tests/test_settings.py	Pass
Stats DB insert/fetch	pytest -q tests/test_stats_db.py	Pass
UI dashboard launches	pytest -q tests/test_ui_dashboard.py	Pass (no crash)
Full app start	python run_overlay_core.py	Overlay appears, ghost renders, hot‑key F1 opens Settings, Ctrl+Alt+S opens Stats Dashboard, settings changes persist.
Hot‑key changes	Edit hot‑keys in Settings, close dialog, press new hot‑key → expected action occurs.	Works without restart.
Ghost colour/opacity change	Adjust colour/opacity → live preview updates and on‑screen ghost updates instantly.	Visible shift.
Stats saved after exit	Play a few seconds, press Esc. Open Stats Dashboard → match appears with non‑zero events.	Data present.
Export CSV	Select match → click Export → file saved, open in a spreadsheet → rows correspond to events.	CSV correct.
7️⃣ Final Verification / Demo Steps (what you’ll do while cooking)
Start the app

source .venv/bin/activate     # if you use a venv
python run_overlay_core.py
Verify:

Ghost follows predicted piece.
Press F1 → Settings window appears.
Change ghost colour → overlay changes instantly.
Change a hot‑key (e.g., set toggle to F8) → close Settings → press F8 → overlay toggles.

Play a short game (≈ 20 s). Press Esc to quit.

Open Stats Dashboard (Ctrl+Alt+S).

Verify a new match row is listed.
Click it → three charts appear.
Click Export CSV, open the file, confirm rows.
Run the CI locally (pytest -q) – all 11 tests (including the new ones) should pass.

If everything works, you can hand the repo over and go cook. 🎉

8️⃣ Estimated Time Breakdown (≈ 45 min)
Block	Approx. Minutes
Settings model & TinyDB persistance	10
Qt Settings dialog (incl. live preview)	15
Hook settings into core & hot‑key registration	6
OverlayRenderer colour/opacity API	4
Stats DB schema + collector functions	8
Dashboard UI (table + 3 charts)	12
Unit/UI tests + CI tweak	8
Buffer for adjustments / sanity runs	5
Total	≈ 45 min (plus a few minutes of “cook‑time” verification)
