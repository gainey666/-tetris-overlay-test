📚 Very‑Detailed Implementation Roadmap
Project: -tetris-overlay-test – Real‑time Tetris overlay with prediction agents, live‑settings UI, statistics tracking, and a full CI pipeline.

Goal for this sprint: Wire‑up everything that has already been added (settings UI, stats DB, collector, dashboard, dynamic hot‑keys, proper frame loop, and ghost rendering) so the application can be launched and left running unattended while you cook. The plan below is deliberately long and granular – copy‑paste it into a markdown file (PLAN.md) and feed it to your LLM “Windsurf” AI. The LLM can then execute each step autonomously, committing the changes one‑by‑one, running the tests, and finally opening the overlay for you.

📦 Table of Contents
High‑Level Objectives
Prerequisites & Environment
Repository Overview (Current State)
Architectural Blueprint (What We’ll End Up With)
[Step‑by‑Step Implementation Plan]
5.1 Create a Central Settings Singleton
5.2 Dynamic Hot‑Key Registration
5.3 OverlayRenderer Enhancements (ghost style & shape)
5.4 Replace “new renderer per frame” with a Global Renderer
5.5 Add a Proper 30 FPS Frame Loop (worker thread)
5.6 Integrate the Statistics Collector (start/end/record)
5.7 Expose the Stats Dashboard via a Hot‑Key
5.8 Finish Piece‑Detection Integration (stub → real)
5.9 Persist Settings Changes & Reactive Updates
5.10 Add Robust Error Handling & Logging
5.11 Write / Extend Test Suite (unit, integration, UI)
5.12 Upgrade CI Workflow (Qt, SQLite, coverage)
5.13 Documentation & Quick‑Start Guide
5.14 Performance‑Testing & Profiling
5.15 Final Verification Checklist & Release Tag
Estimated Time per Major Block (for the LLM)
Potential Pitfalls & How the LLM Should Recover
Commit‑Message Conventions (so the repo stays tidy)
1️⃣ High‑Level Objectives
#	Objective	Success Criterion
A	Frame loop runs continuously at ~30 FPS, never crashes, and updates the overlay each tick.	python run_overlay_core.py prints “Processed boards …” every frame, CPU usage stays < 15 % on a typical laptop.
B	Ghost rendering shows the correct tetromino shape (I/O/T/S/Z/J/L) with the colour/opacity selected in Settings.	Visual inspection: ghost matches piece type, rotation, colour matches preview in Settings UI.
C	Settings UI (Qt) can be opened with the configured hot‑key (default F1). Any change is persisted instantly and reflected in the running overlay without restart.	Change ghost colour → ghost updates live; change hot‑key → new hot‑key works.
D	Statistics tracking records a row per frame (piece, lines cleared, combo, B2B, latency) into an SQLite DB (stats.db).	After a match, opening Stats Dashboard shows a non‑empty table; export CSV contains > 0 rows.
E	Stats Dashboard can be opened via hot‑key (default Ctrl+Alt+S) and displays line‑score, combo, piece distribution charts.	Dashboard loads, chart axes are populated, export buttons generate files.
F	CI runs on every push, executes the full test suite (including the new UI tests) and passes.	GitHub Actions badge shows “green”.
G	Documentation (README.md, HOTKEYS.md, docs/) is up‑to‑date and clearly shows how to run the overlay, open the UI, and view the dashboard.	git clone … && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python run_overlay_core.py works out‑of‑the‑box.
H	Performance – the frame loop stays under ~30 ms per iteration (≈ 30 FPS).	Test script prints average frame time < 35 ms.
2️⃣ Prerequisites & Environment
Tool	Version	Install Command
Python	3.11+	pyenv install 3.11 && pyenv local 3.11
virtualenv	–	python -m venv .venv
pip	latest	.venv/bin/pip install --upgrade pip
Dependencies	see requirements.txt – includes opencv-python, pygame, tinydb, sqlmodel, PySide6, pytest, pytest‑qt, ruff, mypy	.venv/bin/pip install -r requirements.txt
ffmpeg	(optional – not needed for this sprint)	sudo apt‑get install ffmpeg
Git	–	git config user.name "Your Name" / git config user.email "you@domain"
GitHub CLI (optional)	–	gh auth login – handy for creating PRs automatically.
Note for the LLM: All commands must be run inside the repository’s root directory. The LLM should cd into the repo before any file manipulation.

3️⃣ Repository Overview (Current State)
tetris-overlay-test/
│
├─ ui/
│   ├─ settings.py                 ← dataclass model for all user options
│   ├─ settings_storage.py        ← TinyDB read/write helpers
│   ├─ settings_dialog.py         ← Qt Settings dialog + LivePreviewWidget
│   ├─ stats_dashboard.py        ← Qt dashboard with Matplotlib charts
│   └─ current_settings.py        ← (to be added) singleton that holds CURRENT
│
├─ stats/
│   ├─ db.py                      ← SQLModel schema (Match, Event) + engine
│   └─ collector.py               ← start_new_match / end_current_match / record_event
│
├─ src/
│   └─ agents/ …                 ← prediction agents (dellacherie, onnx, …)
│
├─ run_overlay_core.py           ← entry point (currently missing frame loop, hot‑key logic)
├─ overlay_renderer.py           ← draws ghost (placeholder)
├─ capture.py, dual_capture.py, …
├─ roi_calibrator.py, roi_capture.py, next_queue_capture.py
├─ tests/
│   ├─ test_settings.py
│   ├─ test_stats_db.py
│   ├─ test_ui_dashboard.py
│   └─ … (other existing tests)
│
├─ .github/workflows/
│   ├─ ci.yml
│   └─ ci_python.yml
│
├─ requirements.txt
└─ README.md, HOTKEYS.md, docs/
Missing Integration Points (the “old” code the senior reviewer saw):

No import of pygame in run_overlay_core.py.
process_frames() never executed.
A brand‑new OverlayRenderer() is created on each frame → F9 toggle never works.
Hard‑coded piece "T" and orientation 0.
Stats collector never started / never records events.
Hot‑keys still hard‑coded in tetris_overlay_core._register_hotkeys().
Ghost colour/opacity never reaches the renderer (Settings UI only changes its own preview).
Dashboard hot‑key (open_stats) not wired.
All of those gaps will be closed in the plan below.

4️⃣ Architectural Blueprint (What the Final System Looks Like)
                     ┌───────────────────────┐
                     │  Settings JSON (TinyDB)│
                     └─────────▲─────────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │  ui/current_settings.py  │ (singleton)
                 └───────▲───────┬───────────┘
                         │       │
          ┌──────────────┘       └───────────────┐
          │                                        │
  ┌───────▼───────┐                        ┌─────▼───────┐
  │   Settings    │                        │  Hot‑keys   │
  │   Dialog      │←─ user edits ──►emit──►│  Manager    │
  │   (Qt)       │                        │ (dynamic)  │
  └───────▲───────┘                        └─────▲───────┘
          │                                        │
          │   (settings_changed)                   │
          └───────────────────────►────────────────┘
                         │
                         ▼
               ┌───────────────────────┐
               │  run_overlay_core.py   │
               │  – loads CURRENT      │
               │  – starts frame loop  │
               │  – registers hot‑keys│
               └───────▲───────▲───────┘
                       │       │
   ┌───────────────────┘       └─────────────────────┐
   │                                                 │
   ▼                                                 ▼
┌───────────────────────┐                    ┌───────────────────────┐
│  Frame Worker Thread   │───►process_frames──►│  OverlayRenderer      │
│  (30 FPS)             │                    │  – draws ghost       │
└───────▲───────▲───────┘                    └───────▲───────▲───────┘
        │       │                                    │       │
        │       │                                    │       │
        │       │               ┌────────────────────┘       │
        │       │               │                            │
        │       │               ▼                            ▼
        │   ┌───────────────────────────────────┐   ┌───────────────────────┐
        │   │  stats/collector.py               │   │  piece_detector.py   │
        │   │  – start_new_match / record_event │   │  (stub → real)      │
        │   └───────────────────────────────────┘   └───────────────────────┘
        │
        ▼
 ┌───────────────────────┐
 │  stats/db.py (SQLite)  │
 └─────────────▲─────────┘
               │
               ▼
   ┌───────────────────────┐
   │  ui/stats_dashboard   │
   │  (Qt + Matplotlib)   │
   └───────────────────────┘
All communication is via the singleton CURRENT and the Qt signals – no global mutable state spread across modules.

5️⃣ Step‑by‑Step Implementation Plan
How the LLM should work:

Clone the repo (or work on the existing local copy).
Create a new branch (feature/full‑integration‑v2).
Iterate through the numbered sub‑steps below. After each sub‑step, the LLM should run the tests (pytest -q) and commit with the prescribed commit message. If a test fails, the LLM should open the failing file, apply the minimal fix, re‑run the test, and only then commit.
Push the branch and open a PR. The CI will automatically run.
When all tests pass, the LLM should tag the commit (v2.0‑full‑integration) and generate a short release note.
Below each sub‑step is a code snippet ready to be inserted (the LLM can copy‑paste). If a file does not exist yet, create it. If it already exists, overwrite only the sections highlighted (using # === BEGIN PATCH === … # === END PATCH === markers).

5.1 Create a Central Settings Singleton
File: ui/current_settings.py (new file)

# === BEGIN PATCH ===
"""Singleton that holds the current Settings instance.

All modules must import `CURRENT` from this file – it will always contain the
most‑recent settings (in‑memory) and will be persisted automatically when the
Settings dialog emits `settings_changed`.
"""
from .settings_storage import load as _load, save as _save
from .settings import Settings

# Load (or create defaults) at import time
CURRENT: Settings = _load()

def update(new: Settings) -> None:
    """Replace the global instance and persist to TinyDB."""
    global CURRENT
    CURRENT = new
    _save(new)
# === END PATCH ===
Commit: feat(settings): add singleton CURRENT for runtime settings

5.2 Dynamic Hot‑Key Registration
File: tetris_overlay_core.py – replace the existing _register_hotkeys block.

# === BEGIN PATCH ===
# Remove the old _register_hotkeys() implementation (around line 158) and add:

def _register_dynamic_hotkeys():
    """Register all hot‑keys according to the live Settings."""
    # First clear any existing bindings (important when re‑loading after Settings change)
    keyboard.unhook_all()

    hk = CURRENT.hotkeys  # CURRENT comes from ui.current_settings

    # Core overlay hot‑keys
    keyboard.add_hotkey(hk.toggle_overlay, toggle_overlay)               # F9
    keyboard.add_hotkey(hk.open_settings, lambda: SettingsDialog().exec())
    keyboard.add_hotkey(hk.debug_logging, _toggle_debug_logging)
    keyboard.add_hotkey(hk.quit, _graceful_exit)
    keyboard.add_hotkey(hk.calibrate, start_calibrator)

    # Stats dashboard hot‑key
    keyboard.add_hotkey(hk.open_stats, lambda: StatsDashboard().show())
# === END PATCH ===
Additional imports (add near the top of run_overlay_core.py after existing imports):

# === BEGIN PATCH ===
from ui.current_settings import CURRENT, update as update_settings
from ui.settings_dialog import SettingsDialog
from ui.stats_dashboard import StatsDashboard
# === END PATCH ===
Hook the Settings‑changed signal (right after creating renderer at the bottom of the file, before run_overlay is called):

# === BEGIN PATCH ===
# Create the global renderer (we will reuse it)
renderer = OverlayRenderer()

# Connect SettingsDialog signals to runtime updater
_settings_dialog = SettingsDialog()
def _apply_new_settings(new):
    update_settings(new)          # persist & replace CURRENT
    _register_dynamic_hotkeys()  # re‑register with new key bindings
    # Update renderer ghost style immediately
    renderer.update_ghost_style(colour=new.ghost.colour,
                               opacity=new.ghost.opacity)
    # Also update visual flags (combo / B2B) – stored in CURRENT, the renderer can read them
    # (Renderer will query CURRENT.show_combo / show_b2b when drawing)
_Settings_dialog.settings_changed.connect(_apply_new_settings)
# NOTE: we do NOT auto‑show the dialog; the user opens it via hot‑key
# === END PATCH ===
Call _register_dynamic_hotkeys() early (right after loading the settings, before any thread starts):

# After loading settings (line ~49)
_register_dynamic_hotkeys()
Commit: feat(hotkeys): dynamic registration from Settings singleton

5.3 OverlayRenderer Enhancements
File: overlay_renderer.py – add colour/opacity handling and optional shape logic.

# === BEGIN PATCH ===
import pygame
from src.agents.prediction_agent_dellacherie import PIECE_SHAPES   # for real shapes

class OverlayRenderer:
    def __init__(self):
        flags = pygame.NOFRAME | pygame.SRCALPHA
        self.screen = pygame.display.set_mode((1, 1), flags)
        self.visible = False
        self._ghost_colour = (255, 255, 255, 128)   # default white semi‑transparent
        logging.info("OverlayRenderer initialized (hidden)")

    # ------------------------------------------------------------------
    # Public API used by SettingsDialog
    # ------------------------------------------------------------------
    def update_ghost_style(self, colour: tuple[int, int, int], opacity: float):
        """Receive new RGBA style from Settings (opacity 0‑1)."""
        r, g, b = colour
        a = int(opacity * 255)
        self._ghost_colour = (r, g, b, a)

    # ------------------------------------------------------------------
    # Ghost drawing – now uses the stored colour and the actual tetromino shape
    # ------------------------------------------------------------------
    def draw_ghost(self, surface, column, rotation, piece_type="T"):
        """Draw a ghost piece using the current colour/opacity."""
        cell_w = cell_h = 30          # TODO: expose as configurable cell size?
        shape = PIECE_SHAPES.get(piece_type, PIECE_SHAPES["T"])[rotation]

        for dx, dy in shape:
            # Board origin is bottom‑left → flip Y
            x = (column + dx) * cell_w
            y = (20 - dy - 1) * cell_h    # 20 rows high
            ghost = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
            ghost.fill(self._ghost_colour)
            surface.blit(ghost, (x, y))
# === END PATCH ===
If the import of PIECE_SHAPES fails because the module path is different, the LLM should fallback to a simple placeholder shape (as the original rectangle) and log a warning.

Commit: feat(renderer): ghost colour/opacity + real tetromino shapes

5.4 Replace “new renderer per frame” with the Global Renderer
In run_overlay_core.py, delete the lines that create a fresh OverlayRenderer inside process_frames (lines 103‑107). Replace with the global renderer defined earlier.

# === BEGIN PATCH ===
# Inside process_frames(), replace:
#    overlay = OverlayRenderer()
#    if overlay.visible:
#        overlay.draw_ghost(...)
#        pygame.display.flip()
# with:

if renderer.visible:
    renderer.draw_ghost(
        renderer.screen,
        pred["target_col"],
        pred["target_rot"],
        piece_type=pred.get("piece", "T")
    )
    pygame.display.flip()
# === END PATCH ===
Commit: refactor(renderer): use single global OverlayRenderer instance

5.5 Add a Proper 30 FPS Frame Loop
File: run_overlay_core.py – add a worker thread at the bottom (after initializing renderer).

# === BEGIN PATCH ===
import time
from stats import collector as stats_collector

def _frame_worker():
    """Background thread that drives the overlay at ~30 FPS."""
    target_fps = 30
    frame_interval = 1.0 / target_fps
    while True:
        start = time.time()
        try:
            process_frames()
        except Exception as exc:
            logging.error("Fatal error in frame loop: %s", exc, exc_info=True)
        # Sleep the remainder of the frame interval
        elapsed = time.time() - start
        sleep = max(0.0, frame_interval - elapsed)
        time.sleep(sleep)

# ------------------------------------------------------------------
# Start statistics tracking & the frame loop
# ------------------------------------------------------------------
stats_collector.start_new_match(CURRENT.prediction_agent)

# Launch the worker thread (daemon → exits automatically on program exit)
threading.Thread(target=_frame_worker, daemon=True, name="OverlayFrameLoop").start()
# ------------------------------------------------------------------
# Finally, start the overlay UI / hot‑key listener
# ------------------------------------------------------------------
logging.info("Overlay core initializing – press Esc to exit")
run_overlay(renderer=renderer, calibration_func=start_calibration)
# === END PATCH ===
Commit: feat(loop): background 30 FPS frame worker + stats start

5.6 Integrate the Statistics Collector
Inside process_frames, after drawing the ghost and before FRAME_COUNTER += 1, record the event.

# === BEGIN PATCH ===
# At the very top of process_frames (right after the function line)
frame_start_ts = time.time()   # for latency measurement

# ... existing code that captures images, runs prediction ...

# After drawing the ghost:
if renderer.visible:
    renderer.draw_ghost(
        renderer.screen,
        pred["target_col"],
        pred["target_rot"],
        piece_type=pred.get("piece", "T")
    )
    pygame.display.flip()

# Record per‑frame stats (use placeholder values where we don't have real data yet)
stats_collector.record_event(
    frame=FRAME_COUNTER,
    piece=pred.get("piece", "T"),
    orientation=pred.get("target_rot", 0),
    lines_cleared=0,                # TODO: replace with real line‑clear detection
    combo=0,                        # TODO: replace with real combo tracking
    b2b=False,                     # TODO: replace with real B2B detection
    tspin=False,                   # TODO: replace with real T‑Spin detection
    latency_ms=(time.time() - frame_start_ts) * 1000,
)
# === END PATCH ===
Commit: feat(stats): record per‑frame events from process_frames

5.7 Expose the Stats Dashboard via a Hot‑Key
Already covered in 5.2 (added keyboard.add_hotkey(hk.open_stats, lambda: StatsDashboard().show())).
Extra safety: Ensure the dashboard is created once (Qt requires a single QApplication). The Dashboard class itself creates a QApplication only when run as a script (if __name__ == "__main__"). When launched from the hot‑key we need to reuse the existing Qt event loop.

Add a tiny helper at the top of run_overlay_core.py:

# === BEGIN PATCH ===
# Helper to launch a Qt window from a non‑Qt thread (hot‑key callback)
def _show_dashboard():
    """Create and show the stats dashboard (Qt)."""
    # If a QApplication already exists (because overlay uses pygame → no Qt), we create one now.
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    dash = StatsDashboard()
    dash.show()
    # Run the Qt event loop in a non‑blocking way:
    #   - If we are already inside a Qt exec() (unlikely), just return.
    #   - Otherwise we start a separate thread to exec the loop.
    if not app.exec_():
        pass   # exec_ returns when the last window closes
# === END PATCH ===
Replace the hot‑key registration line in 5.2:

keyboard.add_hotkey(hk.open_stats, _show_dashboard)
Commit: feat(dashboard): safe Qt launch from hot‑key

5.8 Finish Piece‑Detection Integration
File: piece_detector.py (new file). For MVP we’ll implement a very simple colour‑based detector that looks at the first queue image (queue_images[0]) and decides the piece based on the dominant colour.

# === BEGIN PATCH ===
"""Very‑simple piece detector – placeholder for a real model.

The function returns a dict with:
    "piece": one‑character string from {"I","O","T","S","Z","J","L"}
    "orientation": int 0‑3 (index into PIECE_SHAPES)
"""
import numpy as np
from PIL import Image

# Approximate HSV hue ranges for the classic Tetris piece colours.
_HUE_RANGES = {
    "I": (  0,  10),   # cyan (≈180° → 0‑10 after modulo 180 in OpenCV)
    "O": ( 20,  30),   # yellow
    "T": ( 80, 100),   # purple/magenta
    "S": ( 50,  70),   # green
    "Z": ( 10,  20),   # red/orange
    "J": (120, 140),   # blue
    "L": (140, 160),   # orange‑red
}

def _mean_hue(img: Image.Image) -> float:
    """Return the average hue (0‑179) of an RGB image."""
    import cv2
    arr = np.array(img.convert("RGB"))
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    hue = hsv[..., 0]
    # discard completely black pixels which have undefined hue
    mask = hsv[..., 1] > 0
    if mask.sum() == 0:
        return 0.0
    return float(hue[mask].mean())

def detect_piece(queue_images: list[Image.Image]) -> dict:
    """Detect the next piece from the first queue image."""
    if not queue_images:
        raise ValueError("Empty next‑queue – cannot detect piece")
    img = queue_images[0]
    hue = _mean_hue(img)
    # Find the closest matching range
    for piece, (low, high) in _HUE_RANGES.items():
        if low <= hue <= high:
            return {"piece": piece, "orientation": 0}
    # Fallback – default to T
    return {"piece": "T", "orientation": 0}
# === END PATCH ===
Update process_frames to use this detector (replace the hard‑coded "T" and orientation):

# === BEGIN PATCH ===
# Right after grabbing the queue images:
queue_info = detect_piece(queue_images)    # <-- new import at file top
piece_name = queue_info["piece"]
piece_rot  = queue_info["orientation"]

# Predict using the actual piece
pred = prediction_agent.handle({
    "board": left_board,
    "piece": piece_name,
    "orientation": piece_rot,
})
# === END PATCH ===
Add the import at the top of run_overlay_core.py:

# === BEGIN PATCH ===
from piece_detector import detect_piece
# === END PATCH ===
Commit: feat(piece_detection): simple hue‑based detector + integration

5.9 Persist Settings Changes & Reactive Updates
The SettingsDialog already emits settings_changed. We have already wired it to update_settings in 5.2. To ensure the renderer reads visual flags (show_combo, show_b2b) on every draw, adjust OverlayRenderer._update_surface (or better, modify draw_ghost to respect CURRENT.show_combo etc.):

# === BEGIN PATCH ===
# Inside OverlayRenderer.draw_ghost (after drawing the ghost):
if CURRENT.show_combo:
    # Render a tiny green bar just above the ghost as a visual combo indicator
    combo_surface = pygame.Surface((30, 5), pygame.SRCALPHA)
    combo_surface.fill((0, 255, 0, 180))
    surface.blit(combo_surface, (column * 30, (20 - 0) * 30 - 5))

if CURRENT.show_b2b:
    # Render a red outline around the ghost for B2B
    pygame.draw.rect(surface,
                     (255, 0, 0, 180),
                     (column * 30, (20 - max(dy for _, dy in shape) - 1) * 30,
                     30 * len(shape), 30,
                     2)
# === END PATCH ===
If the LLM cannot import CURRENT directly (circular import), it can import it from ui.current_settings inside the method.

Commit: feat(renderer): visual combo/B2B indicators controlled by Settings

5.10 Add Robust Error Handling & Logging
File: run_overlay_core.py – wrap the whole frame loop in a try/except and log unhandled exceptions. Also ensure the logger writes JSON telemetry (already set up).

# === BEGIN PATCH ===
def _frame_worker():
    target_fps = 30
    frame_interval = 1.0 / target_fps
    while True:
        start = time.time()
        try:
            process_frames()
        except Exception as exc:
            logging.exception("Unhandled exception in frame loop")
        # keep FPS stable
        elapsed = time.time() - start
        time.sleep(max(0.0, frame_interval - elapsed))
# === END PATCH ===
Add a small helper for graceful shutdown that also flushes the telemetry logger:

# === BEGIN PATCH ===
def _graceful_exit():
    from stats import collector as stats_collector
    stats_collector.end_current_match()
    logging.info("Esc pressed – shutting down")
    # Force flush of telemetry logger
    for h in logging.getLogger("telemetry").handlers:
        h.flush()
    from tetris_overlay_core import graceful_exit
    graceful_exit()
# === END PATCH ===
Commit: fix(logging): ensure telemetry flushed on exit + robust frame loop

5.11 Write / Extend Tests
5.11.1 Unit Test for Settings Persistence
File: tests/test_settings.py (new).

# === BEGIN PATCH ===
import os
from ui.settings_storage import save, load, Settings
import json

def test_settings_roundtrip(tmp_path):
    # Use a temporary file for TinyDB
    db_path = tmp_path / "settings.json"
    # Monkey‑patch DB_PATH inside the module
    from ui import settings_storage as ss
    ss.DB_PATH = db_path

    s = Settings()
    s.roi_left = (10, 20, 640, 360)
    s.ghost.colour = (100, 150, 200)
    s.ghost.opacity = 0.8
    s.hotkeys.toggle_overlay = "f5"
    save(s)

    loaded = load()
    assert loaded.roi_left == (10, 20, 640, 360)
    assert loaded.ghost.colour == (100, 150, 200)
    assert loaded.ghost.opacity == 0.8
    assert loaded.hotkeys.toggle_overlay == "f5"
# === END PATCH ===
5.11.2 Integration Test for Frame Loop (mocked captures)
Create a mock capture that returns a solid image (so the board extraction will be deterministic).

File: tests/test_frame_loop.py

# === BEGIN PATCH ===
import pytest, threading, time
from unittest import mock
from run_overlay_core import process_frames, FRAME_COUNTER, renderer
from ui.current_settings import CURRENT

# Mock DualScreenCapture to return dummy PIL images
@pytest.fixture(autouse=True)
def mock_capture(monkeypatch):
    from PIL import Image
    dummy = Image.new("RGB", (200, 400), (0, 0, 0))   # black board
    class DummyCapture:
        def grab(self): return dummy
    # Patch DualScreenCapture and shared UI / queue captures
    monkeypatch.setattr("dual_capture.DualScreenCapture", lambda: mock.Mock(grab=lambda: (dummy, dummy)))
    monkeypatch.setattr("shared_ui_capture.capture_shared_ui", lambda: {"score": dummy, "wins": dummy, "timer": dummy})
    monkeypatch.setattr("next_queue_capture.capture_next_queue", lambda: [])
    yield

def test_process_frames_runs_once():
    # Ensure the renderer is visible so draw_ghost is called
    renderer.visible = True
    start = FRAME_COUNTER
    process_frames()
    assert FRAME_COUNTER == start + 1
# === END PATCH ===
5.11.3 Qt UI Tests (already present) – add a sanity test for the dashboard opening.
File: tests/test_ui_dashboard.py

# === BEGIN PATCH ===
import pytest
from PySide6.QtWidgets import QApplication
from ui.stats_dashboard import StatsDashboard

@pytest.fixture(scope="session")
def app():
    return QApplication.instance() or QApplication([])

def test_dashboard_can_open(qtbot, app):
    dash = StatsDashboard()
    qtbot.addWidget(dash)
    dash.show()
    qtbot.waitExposed(dash)
    # No crash → pass
# === END PATCH ===
5.11.4 Run all tests
Add a CI step for UI tests (already present in ci_python.yml). Ensure pytest-qt is installed in CI.

Update .github/workflows/ci_python.yml (add pytest-qt to install list).

# === BEGIN PATCH ===
- name: Install test dependencies
  run: |
    pip install -r requirements.txt
    pip install pytest-qt
# === END PATCH ===
Commit: test: add settings persistence, frame‑loop, and UI sanity tests

5.12 Upgrade CI Workflow
Ensure Qt libraries are available on Ubuntu runners (they are pre‑installed).
Run ruff and mypy for lint & static typing.
Edit .github/workflows/ci.yml (or create a new job).

# === BEGIN PATCH ===
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install deps
        run: |
          pip install -r requirements.txt
          pip install ruff mypy
      - name: Run ruff
        run: ruff .
      - name: Run mypy
        run: mypy .
# === END PATCH ===
Commit: ci: add lint & type‑checking jobs

5.13 Documentation & Quick‑Start Guide
README.md – Add a section “Running the overlay with the new UI” with commands.
Create HOTKEYS.md – List default hot‑keys and mention they’re configurable via Settings.
File: HOTKEYS.md

# Hot‑keys (default values)

| Action                     | Default key | Configurable via Settings → Hotkeys tab |
|---------------------------|------------|----------------------------------------|
| Toggle ghost overlay      | **F9**      | `hotkeys.toggle_overlay`               |
| Open Settings dialog      | **F1**      | `hotkeys.open_settings`                |
| Debug logging toggle      | **F2**      | `hotkeys.debug_logging`                |
| Quit (Esc)                | **Esc**    | `hotkeys.quit`                         |
| Calibrate ROIs            | **Ctrl+Alt+C** | `hotkeys.calibrate`               |
| Open Statistics Dashboard | **Ctrl+Alt+S** | `hotkeys.open_stats`               |
Update README.md (add a “Quick Start” block).

## Quick Start

```bash
git clone https://github.com/gainey666/-tetris-overlay-test.git
cd -tetris-overlay-test
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run_overlay_core.py
Press F1 to open the Settings UI – change ghost colour, opacity, hot‑keys, etc.
Press Ctrl+Alt+S to view the Statistics Dashboard after a match.
Press F9 to toggle the ghost overlay on‑screen.

**Commit:** `docs: add HOTKEYS.md and update README with UI workflow`

---

### 5.14 Performance‑Testing & Profiling  

Create a small script (`benchmark_frame_time.py`) that runs the frame worker for a few seconds and prints average frame time.

```python
# === BEGIN PATCH ===
# benchmark_frame_time.py – run manually to verify ~30 FPS
import time, threading
from run_overlay_core import process_frames, FRAME_COUNTER, renderer
from stats import collector as stats_collector
from ui.current_settings import CURRENT

def _run():
    stats_collector.start_new_match(CURRENT.prediction_agent)
    start = time.time()
    frames = 0
    while frames < 200:   # ~6‑7 seconds at 30 FPS
        t0 = time.time()
        process_frames()
        frames += 1
        time.sleep(max(0, (1/30) - (time.time() - t0)))
    elapsed = time.time() - start
    print(f"Processed {frames} frames in {elapsed:.2f}s → {frames/elapsed:.1f} FPS")
    stats_collector.end_current_match()

threading.Thread(target=_run, daemon=True).start()
# === END PATCH ===
Manual Execution:

python benchmark_frame_time.py
# Expected output: "Processed 200 frames in 6.8s → 29.4 FPS"
Add this script in the repo root (it won’t be part of CI).

Commit: perf: add simple benchmark script for frame‑rate verification

5.15 Final Verification Checklist & Release Tag
After all patches are merged (the LLM should run these steps automatically):

✅	Action
1	git checkout feature/full-integration-v2
2	pytest -q → all tests pass (≥ 11).
3	ruff . → no lint errors.
4	mypy . → passes (or minimal ignore comments).
5	Run the overlay manually: python run_overlay_core.py.
6	Verify hot‑keys work (F1, F9, Ctrl+Alt+S, etc.).
7	Change ghost colour in Settings → ghost updates instantly.
8	Play a short Tetris session, press Esc.
9	Open Stats Dashboard → a match appears, charts populated, export CSV works.
10	Run python benchmark_frame_time.py → FPS ≥ 28.
11	Push branch, open PR, let GitHub Actions run.
12	After CI is green, merge to main.
13	Tag the commit: git tag -a v2.0-full-integration -m "Full overlay integration, settings UI, stats tracking" and git push origin v2.0-full-integration.
14	Update README.md badge to point to the new release (optional).
Release note (auto‑generated by the LLM):

v2.0 – Full integration

- 30 FPS frame loop with background worker
- Dynamic hot‑key registration (configurable via Settings UI)
- Qt Settings dialog with live ghost preview, colour & opacity picker, hot‑key editor, visual‑flags
- Real tetromino ghost rendering (shape & rotation) with configurable colour/opacity
- Statistics collector (SQLite + SQLModel) + per‑frame event logging
- Qt Statistics Dashboard (line‑score, combo, piece distribution) with CSV/JSON export
- Graceful shutdown flushes telemetry logs
- Comprehensive test suite (settings persistence, frame loop, UI sanity)
- CI pipeline now runs lint, type‑checking, and UI tests
- Documentation refreshed (README, HOTKEYS)
Commit: chore(release): v2.0 – full overlay integration

6️⃣ Estimated Time per Major Block (for the LLM)
Block	Approx. minutes (LLM)
5.1 Singleton Settings	5
5.2 Dynamic Hot‑Keys	12
5.3 OverlayRenderer (colour + shape)	10
5.4 Global Renderer usage	4
5.5 Frame Worker thread	8
5.6 Stats Collector start/end/record	9
5.7 Dashboard hot‑key launch	6
5.8 Simple Piece Detector	8
5.9 Reactive Updates (flags, colour)	7
5.10 Error handling & logging	5
5.11 Tests (add/extend)	15
5.12 CI upgrades (ruff, mypy, pytest‑qt)	6
5.13 Docs (README + HOTKEYS)	5
5.14 Benchmark script	4
5.15 Verification & tagging	5
Total	~116 min (≈ 2 hrs) – the LLM can run many of these steps unattended while you’re away.
7️⃣ Potential Pitfalls & How the LLM Should Recover
Pitfall	Symptom	LLM Recovery Strategy
pygame not imported → NameError on pygame.display.flip()	Crash on first frame	Ensure import pygame is present at top of run_overlay_core.py. If still missing, add pip install pygame to CI install step.
Circular import between ui.current_settings and overlay_renderer	ImportError or AttributeError when CURRENT is accessed	Use local imports inside methods (from ui.current_settings import CURRENT) to break the cycle. LLM should move imports inside functions as needed.
Hot‑key registration fails because Qt blocks the main thread	Hot‑keys never fire	Ensure run_overlay_core registers hot‑keys before starting the OverlayRenderer event loop. Also, keyboard runs in its own thread, not UI thread.
Stats DB file lock error (SQLite “database is locked”)	Exceptions during record_event	Use short‑lived sessions (with get_session() as s:) – already done. If still fails, add PRAGMA journal_mode=WAL; on engine creation (patch stats/db.py).
Qt “QApplication already exists” when opening dashboard from hot‑key	Crash with “QApplication already instantiated”	Helper _show_dashboard() checks QApplication.instance() and creates only if None. If the dashboard is already open, just raise_() it to front.
Tests failing because of absolute paths (e.g., TinyDB writes to repo root)	FileNotFoundError in CI	In test fixtures, override DB_PATH to a temporary directory (tmp_path). LLM already included that in test patches.
Missing opencv-python bindings for cv2 in CI	ImportError in run_overlay_core	Ensure opencv-python is listed in requirements.txt and installed in CI before tests.
PySide6 missing on CI	ImportError for PySide6	Add PySide6 to requirements.txt (already there). CI runners have Qt libs; pip install PySide6 works.
CI timing out on UI tests (Qt windows need a display)	GitHub Actions kills the job	Use the xvfb action to provide a virtual X server. Add to CI YAML:
- name: Set up Xvfb
  uses: xvfb-action@v1
  with:
    screen: 0 1024x768x24
| LLM must add that step before running UI tests. | | Mypy errors after adding new imports | Type errors | Add # type: ignore where appropriate or improve type hints. LLM can run mypy locally to see exact failures and fix them. | | Keyboard hot‑key strings not normalized (e.g., "F9" vs "f9") | Hot‑keys don’t trigger | Normalise all hot‑key strings to lower‑case when reading from Settings (hk.toggle_overlay.lower()). LLM should add .lower() in _register_dynamic_hotkeys. |

8️⃣ Commit‑Message Conventions
The LLM should follow the Conventional Commits style. Example templates:

feat(settings): add singleton CURRENT for runtime settings
feat(hotkeys): dynamic registration from Settings singleton
feat(renderer): ghost colour/opacity + real tetromino shapes
refactor(renderer): use single global OverlayRenderer instance
feat(loop): background 30 FPS frame worker + stats start
feat(stats): record per‑frame events from process_frames
feat(dashboard): safe Qt launch from hot‑key
feat(piece_detection): simple hue‑based detector + integration
feat(renderer): visual combo/B2B indicators controlled by Settings
fix(logging): ensure telemetry flushed on exit + robust frame loop
test: add settings persistence, frame‑loop, and UI sanity tests
ci: add lint & type‑checking jobs
docs: add HOTKEYS.md and update README with UI workflow
perf: add simple benchmark script for frame‑rate verification
chore(release): v2.0 – full overlay integration
The LLM should amend any failing commit (e.g., if tests fail after a patch) before moving to the next step.

🎉 All Done!
Follow the plan above verbatim, and the LLM will:

Wire the core loop so the overlay updates at ~30 FPS.
Expose a full‑featured Settings UI (colour, opacity, hot‑keys, visual flags).
Render real tetromino ghosts with the chosen style.
Collect per‑frame statistics and store them in SQLite.
Show a statistics dashboard on demand, with export capability.
Persist user preferences and reload them on start‑up.
Run a robust CI pipeline with lint, type checking, unit/UI tests.
Provide documentation for end‑users.
All that remains is to let the LLM churn through the patches (≈ 2 hours of CPU time) while you step away and enjoy your cooking. When the LLM finishes, you’ll have a production‑ready overlay ready for testers or for your own Tetris‑coaching sessions. 🚀

Good luck, and happy coding! (the LLM will do the heavy lifting).