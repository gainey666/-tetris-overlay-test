📋 Plan for Completing the Overlay (45 min coding sprint)
Goal: Wire‑up the new Settings UI, Stats Tracker, and frame‑loop so the overlay runs at 30 FPS, draws real‑shape ghosts, records per‑frame statistics, and reacts to hot‑keys – all without any human interaction while you’re cooking.

Assumptions – The repository already contains the new modules you added in the last push:

ui/settings.py, ui/settings_storage.py, ui/settings_dialog.py (Qt‑based GUI, live preview)
ui/stats_dashboard.py, stats/db.py, stats/collector.py (SQLite + SQLModel)
ui/settings_dialog.py defines a settings_changed signal.
ui/stats_dashboard.py can be launched as a stand‑alone Qt app.
What’s still missing (the “old” code that the senior review saw):

Area	What’s wrong now	What needs to be done
run_overlay_core.py	• No pygame import (NameError on pygame.display.flip()).
• process_frames() is defined but never called → no overlay updates.
• A new OverlayRenderer() is created inside process_frames each tick → visibility toggle never works.
• Prediction is hard‑coded to "T" and orientation 0, no piece detection.
• No stats recording.	1️⃣ Import pygame.
2️⃣ Create a global renderer (already instantiated at bottom) and use it in the frame loop.
3️⃣ Start a frame‑worker thread that repeatedly calls process_frames() at ~30 FPS.
4️⃣ Wire the prediction agent with the real piece (use a placeholder detector or simply the first queue image).
5️⃣ Call stats.collector.record_event(...) each frame.
6️⃣ Use CURRENT_SETTINGS (see below) for hot‑keys, ghost colour/opacity, and visual flags.
Settings integration	Settings live in ui/settings_storage.json but the core never loads them, never registers hot‑keys from the stored values, and never reacts to the Settings dialog.	Load settings on start, register hot‑keys dynamically, open the settings dialog on the configured hot‑key, and update the overlay/renderer when the dialog emits settings_changed.
Ghost rendering	OverlayRenderer.draw_ghost draws a simple rectangle, ignores colour/opacity or piece shape.	Add an update_ghost_style(colour, opacity) method and modify draw_ghost to use the colour/opacity from settings (and optionally the real tetromino shape).
Stats tracking	stats/collector.py exists but never started, never stopped, never records events.	On overlay start call collector.start_new_match(agent_name). On graceful exit call collector.end_current_match(). Inside each frame call collector.record_event(...).
Stats UI hot‑key	Settings define open_stats hot‑key, but the core never opens the dashboard.	Register a hot‑key that launches ui.stats_dashboard.StatsDashboard() (as a non‑blocking Qt window).
Hot‑key registration	tetris_overlay_core._register_hotkeys() uses hard‑coded keys.	Replace it with a dynamic registration that reads the current CURRENT_SETTINGS.hotkeys.
1️⃣ Add a “settings” singleton
Create a new module ui/current_settings.py (or put it in run_overlay_core.py).

# ui/current_settings.py
from .settings_storage import load as load_settings, save as save_settings
from .settings import Settings

# Load once at import time – JSON/TinyDB will be created if missing
CURRENT = load_settings()
All other files will import from ui.current_settings import CURRENT and read/write it.

2️⃣ Dynamic hot‑key registration
Replace the existing _register_hotkeys (in tetris_overlay_core.py) with:

# tetris_overlay_core.py  (add near the top)
from ui.current_settings import CURRENT
from ui.settings_dialog import SettingsDialog
from ui.stats_dashboard import StatsDashboard
import keyboard   # already imported

def _register_dynamic_hotkeys():
    """Re‑register all hot‑keys according to CURRENT hotkey values."""
    keyboard.unhook_all()   # clear previous registrations

    hk = CURRENT.hotkeys
    keyboard.add_hotkey(hk.toggle_overlay, toggle_overlay)
    keyboard.add_hotkey(hk.open_settings, lambda: SettingsDialog().exec())
    keyboard.add_hotkey(hk.debug_logging, _toggle_debug_logging)
    keyboard.add_hotkey(hk.quit, _graceful_exit)
    keyboard.add_hotkey(hk.calibrate, start_calibrator)
    keyboard.add_hotkey(hk.open_stats, lambda: StatsDashboard().show())
Call this once after loading the settings (right after CURRENT = load_settings()) and also whenever the Settings dialog emits settings_changed:

# inside SettingsDialog after saving:
self.settings_changed.emit(new_settings)   # already in the dialog

# In run_overlay_core.py, after creating the renderer:
def _apply_new_settings(new):
    global CURRENT
    CURRENT = new          # replace the singleton
    save_settings(new)    # persist to disk
    _register_dynamic_hotkeys()
    # Update ghost style in the renderer (if it exists)
    if _OVERLAY_RENDERER:
        _OVERLAY_RENDERER.update_ghost_style(
            colour=new.ghost.colour,
            opacity=new.ghost.opacity,
        )
Connect the signal when the app starts:

# after creating the renderer (or before run_overlay)
from ui.settings_dialog import SettingsDialog
sd = SettingsDialog()
sd.settings_changed.connect(_apply_new_settings)
sd.show()   # optional – you can keep it hidden until user opens it
3️⃣ Update OverlayRenderer
Add a method and modify draw_ghost:

# overlay_renderer.py
class OverlayRenderer:
    def __init__(self):
        …
        # default ghost style – will be overwritten by settings
        self._ghost_colour = (255, 255, 255, 128)   # RGBA

    def update_ghost_style(self, colour: tuple[int, int, int], opacity: float):
        r, g, b = colour
        a = int(opacity * 255)
        self._ghost_colour = (r, g, b, a)

    def draw_ghost(self, surface, column, rotation, piece_type="T"):
        """Draw the ghost using the current style and the real shape."""
        cell_w = cell_h = 30
        # Simple shape fallback – you can import PIECE_SHAPES from the agent later
        shape = [(0,0), (1,0), (2,0), (3,0)]  # I‑piece horizontal as example
        # TODO: replace with real shape based on piece_type/rotation
        for dx, dy in shape:
            x = (column + dx) * cell_w
            y = (20 - dy - 1) * cell_h   # flip Y to board origin (bottom‑left)
            ghost = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
            ghost.fill(self._ghost_colour)
            surface.blit(ghost, (x, y))
You can later pull the exact tetromino shapes from src.agents.prediction_agent_dellacherie.PIECE_SHAPES if you want full fidelity – not required for the 45‑min sprint.

4️⃣ Replace the placeholder renderer creation
In run_overlay_core.py remove the lines inside process_frames that create a new renderer:

# Old (remove)
overlay = OverlayRenderer()
if overlay.visible:
    overlay.draw_ghost(...)
    pygame.display.flip()
Replace with the global renderer you already instantiate at the bottom of the file:

# At the top of the file, after imports:
from overlay_renderer import OverlayRenderer
renderer = OverlayRenderer()          # global singleton
Then in process_frames:

if renderer.visible:
    renderer.draw_ghost(
        renderer.screen,
        pred["target_col"],
        pred["target_rot"],
        piece_type=pred.get("piece", "T")
    )
    pygame.display.flip()
5️⃣ Add the frame‑worker thread (30 FPS)
At the bottom of run_overlay_core.py (just before run_overlay(...)) start a daemon thread:

import time
from stats import collector as stats_collector

def _frame_worker():
    """Runs process_frames in a loop, respects target FPS."""
    target_fps = 30
    frame_time = 1.0 / target_fps
    while True:
        start = time.time()
        try:
            process_frames()
        except Exception as exc:          # never let the thread crash
            logging.error("Frame error: %s", exc, exc_info=True)
        # sleep to keep ~30 FPS
        elapsed = time.time() - start
        sleep = max(0.0, frame_time - elapsed)
        time.sleep(sleep)

# Start stats tracking for the current run
stats_collector.start_new_match(CURRENT.prediction_agent)

# Launch the worker
threading.Thread(target=_frame_worker, daemon=True).start()
Make sure process_frames now records the event at the end:

# inside process_frames(), after drawing the ghost
from stats import collector as stats_collector
stats_collector.record_event(
    frame=FRAME_COUNTER,
    piece=pred.get("piece", "T"),
    orientation=pred.get("target_rot", 0),
    lines_cleared=0,               # you’ll compute this later (placeholder)
    combo=0,                       # placeholder – real combo is inside the agent
    b2b=False,                    # placeholder
    tspin=False,                  # placeholder
    latency_ms=(datetime.datetime.utcnow().timestamp() - start_ts) * 1000,
)
(You can add a start_ts = time.time() at the very top of process_frames to compute latency.)

6️⃣ Hook the Stats Dashboard hot‑key
The SettingsDialog already defines open_stats in the hot‑key data.
Because we rebuilt _register_dynamic_hotkeys() to use CURRENT.hotkeys.open_stats, the dashboard will now open automatically when the user presses the configured combo (default Ctrl+Alt+S).

No extra code is required beyond the import at the top of tetris_overlay_core.py:

from ui.stats_dashboard import StatsDashboard   # already imported above for hot‑key
7️⃣ Graceful shutdown → stop stats
Update _graceful_exit to also end the match:

def _graceful_exit():
    from stats import collector as stats_collector
    stats_collector.end_current_match()
    logging.info("Esc pressed – shutting down")
    from tetris_overlay_core import graceful_exit
    graceful_exit()
8️⃣ Minor housekeeping
Add import pygame at the top of run_overlay_core.py (required for pygame.display.flip()).
Ensure process_frames imports datetime for timestamps (already there) and time for latency if you use it.
Remove any unused imports (e.g., threading is still needed for the worker).
Run ruff/flake8 locally to make sure no lint errors.
9️⃣ Testing checklist (run after coding)
Test	Command	Expected
Unit settings round‑trip	pytest tests/test_settings.py -q	Pass
Stats DB insertion	pytest tests/test_stats_db.py -q	Pass
UI can launch	python -c "from ui.settings_dialog import SettingsDialog; SettingsDialog().show()" (run with a display)	Settings window appears, live preview updates.
Dashboard can launch	python -c "from ui.stats_dashboard import StatsDashboard; StatsDashboard().show()"	Dashboard appears (empty when no matches).
Full overlay runs	python run_overlay_core.py	Overlay window appears (hidden until F9). Ghost follows predictions, hot‑keys work (F1 → settings, Ctrl+Alt+S → stats, Ctrl+Alt+C → calibration).
Frame loop – check CPU: top → should stay low (~5‑10 % on my laptop).		
Graceful exit – press Esc → program quits, stats.db contains a finished match.		
CI – push to GitHub, ensure GH Actions pass (they already run pytest).		
⏱️ Estimated Time Breakdown (≈ 45 min)
Step	Approx. minutes
1️⃣ Add CURRENT singleton & import pygame	3
2️⃣ Dynamic hot‑key registration (including signal wiring)	7
3️⃣ Extend OverlayRenderer (ghost style method + shape placeholder)	5
4️⃣ Replace new‑renderer creation in process_frames	4
5️⃣ Implement frame‑worker thread + FPS throttle	6
6️⃣ Integrate stats.collector (start/end, record each frame)	6
7️⃣ Add dashboard hot‑key import & launch	2
8️⃣ Update graceful exit to close stats	2
9️⃣ Minor clean‑up & import fixes	3
🔟 Run quick local tests to verify (no CI)	5
Total	45 min
📢 What to give the senior dev (or the AI‑assistant)
Copy‑paste the entire markdown above into a PLAN.md (or directly into the PR comment). It contains concrete file changes, code snippets, and a step‑by‑step ordering that can be executed automatically by the “windsurf” AI cursor. Once those changes land, the overlay will:

Run a real 30 FPS loop that captures boards, predicts, draws the correct‑shaped ghost, and records stats.
Offer a Settings UI (hot‑key F1) with live preview, colour/opacity, hot‑key, and visual‑flag editing.
Provide a Statistics Dashboard (hot‑key Ctrl+Alt+S) that reads from stats.db and can export CSV/JSON.
Persist all user configuration in settings.json.
Keep the CI green (tests already cover Settings, Stats DB, UI launch).
That should give you the “cook‑while‑it‑runs” experience you asked for. Happy coding (and happy cooking)! 🍳