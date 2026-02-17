⚠️ TL;DR (Read this first – you’re in a mess)
*Your repo is a broken prototype that crashes at import time, has no installer, no UI, no tests, no error handling, and no documentation. In short: nothing a non‑technical user could ever run.

You could continue patching the spaghetti code, but you’ll spin your wheels forever. The only realistic way forward is to keep the repository, throw away the broken parts, and rebuild the core on a clean skeleton – essentially “mold the old repo into a new, professional product**.

Below is a no‑fluff, step‑by‑step, battle‑ready plan that:

Salvages what you can (config handling, any useful utility scripts, the Git history).
Creates a modern, test‑driven, modular codebase on top of it.
Delivers a working overlay, a one‑click installer, full docs, and a support channel – all in ~3 weeks.
If you skip any of these phases you’ll stay stuck in the “never works” loop forever.

1️⃣ BLUNT ASSESSMENT – WHY YOU’RE STUCK
Area	What you have	What it actually means
Code quality	Random mix of pygame, win32gui, Qt imports that all contradict each other.	Impossible to run – Python raises ImportError or “cannot find DLL” as soon as you python main.py.
Architecture	One monolithic main.py that does everything (capture, process, render, UI).	Spaghetti of side‑effects – no way to unit‑test, no way to replace one piece without breaking everything.
Dependencies	requirements.txt with unpinned, outdated versions (pygame==2.0.0, opencv-python).	Version hell – a fresh virtual env will pull the latest pygame which dropped support for the SDL flag you rely on, causing immediate crashes.
Testing	A couple of import‑only tests that always pass.	Fake QA – you have no confidence the program does anything.
User experience	“Run python overlay.py and edit config.json by hand.”	Non‑technical users will give up at the first error.
Build/Distribution	Nothing – you ship raw .py files.	No installer → you can’t sell or even give it to a friend without dragging them through a Python installation tutorial.
Documentation	One‑line README for developers.	No user guide → zero adoption.
Bottom line: the codebase is a dead end. Trying to “fix” it line‑by‑line will cost you weeks of debugging that never ends. The only sane path is to replace the broken core while preserving the repository history and any reusable assets.

2️⃣ OVERALL STRATEGY – “MOLD, NOT REPLACE”
Create a fresh project skeleton on a new branch (refactor/v1).
Move all broken modules to a legacy/ directory (keep them for reference, but they are not compiled or packaged).
Preserve:
config.json schema (or evolve it).
Any utility scripts you actually use (e.g., image_processing.py if it contains useful OpenCV functions).
The original Git history (so you can still blame‑hunt).
Introduce a modern stack:
Qt (PySide6) for all UI – wizard, settings, system‑tray.
Win32 layered window for the overlay (transparent, click‑through).
OpenCV only for screen capture and simple image analysis (detect the game board).
Pydantic (or dataclasses) for a strict Config model with validation.
Incrementally add: tests → installer → docs → support.
That way you don’t lose the repository identity, you avoid re‑inventing the wheel, and you gain a clean, maintainable foundation that can be shipped tomorrow.

3️⃣ PHASE 0 – FOUNDATION (Day 0‑1)
Task	Owner	Effort	Acceptance
Branch & clean – create refactor/v1, push.	Lead Dev	0.5 d	New branch visible, work on it only.
Move dead code – legacy/ folder, add a README.md explaining why it’s dead.	Lead Dev	0.5 d	All imports that crash are gone from src/.
Add LICENSE (MIT), .gitignore, pyproject.toml (PEP‑621) with pinned dependencies.	Dev 1	0.5 d	git status shows no stray files, poetry install works in a clean venv.
Set up CI – GitHub Actions workflow: ruff, black, pytest, build (PyInstaller) on Windows‑latest.	Dev 2	0.5 d	PR fails if lint or build fails.
Add pre‑commit hook (ruff, black, isort).	Dev 2	0.25 d	Commits auto‑format.
Create src/ package layout (src/tetris_overlay/__init__.py, core/, ui/, utils/).	Lead Dev	0.25 d	import tetris_overlay works.
Result – a clean, lint‑passable, buildable skeleton ready for real code.

4️⃣ PHASE 1 – MINIMAL WORKING OVERLAY (Day 2‑5)
Goal: A transparent window that draws a static “ghost piece” on top of a user‑selected Tetris window.
Everything else (auto‑detect, settings, installer) can be added later.

4.1 Choose the right overlay technique
Option	Pros	Cons	Verdict
Qt‑based transparent window (Qt::FramelessWindowHint + Qt::WA_TranslucentBackground)	Pure Python, easy to integrate with UI, cross‑window stacking works on Windows 10+.	Slightly higher CPU if you redraw every frame.	Chosen – you already need Qt for the wizard, so reuse it.
win32 layered window (UpdateLayeredWindow)	Very low‑latency, true click‑through.	Requires win32 API fiddling, extra C‑type boilerplate.	Not needed for a 30 FPS overlay.
DirectX hook (d3d9)	Highest performance, works with games that use hardware acceleration.	Requires C++ DLL, out of scope for a 3‑week rebuild.	Reject.
4.2 Core modules to implement
src/
 └─ tetris_overlay/
     ├─ __init__.py
     ├─ core/
     │   ├─ overlay.py          # Transparent Qt widget, draw loop
     │   ├─ capture.py          # OpenCV screen grab of target HWND
     │   ├─ detection.py        # Simple ROI finder (color‑threshold + contour)
     │   └─ config.py           # Pydantic model + I/O
     ├─ ui/
     │   ├─ wizard.py           # First‑run dialog (manual window pick)
     │   └─ settings_dialog.py # Slider for opacity, colour, hotkeys
     └─ utils/
         └─ logger.py           # loguru wrapper
4.2.1 core/config.py (example)
from pydantic import BaseModel, Field, validator
from pathlib import Path

class OverlayConfig(BaseModel):
    target_hwnd: int = Field(..., description="Window handle of the Tetris client")
    opacity: float = Field(0.6, ge=0.0, le=1.0, description="Overlay opacity")
    ghost_colour: str = Field("#00FF00", regex=r"^#(?:[0-9A-Fa-f]{6})$")
    refresh_rate: int = Field(30, ge=10, le=60)

    @validator("target_hwnd")
    def hwnd_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("HWND must be a positive integer")
        return v

    @classmethod
    def load(cls, path: Path) -> "OverlayConfig":
        if not path.exists():
            raise FileNotFoundError(f"{path} not found")
        return cls.parse_raw(path.read_text())

    def save(self, path: Path) -> None:
        path.write_text(self.json(indent=2))
Why this matters: Strong validation eliminates the “JSON typo” crashes you’re seeing now.

4.2.2 core/capture.py
import cv2
import numpy as np
import win32gui, win32ui, win32con, win32api
from .config import OverlayConfig

def bbox_from_hwnd(hwnd: int) -> tuple[int, int, int, int]:
    """Return (left, top, right, bottom) of the window client area."""
    rect = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = rect
    # optionally strip window decorations with GetClientRect + MapWindowPoints
    return left, top, right, bottom

def grab_window(hwnd: int) -> np.ndarray:
    left, top, right, bottom = bbox_from_hwnd(hwnd)
    width, height = right - left, bottom - top

    hwindc = win32gui.GetWindowDC(hwnd)
    srcdc = win32ui.CreateDCFromHandle(hwindc)
    memdc = srcdc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(srcdc, width, height)
    memdc.SelectObject(bmp)

    memdc.BitBlt((0, 0), (width, height), srcdc, (0, 0), win32con.SRCCOPY)

    # Convert the raw data to a numpy array
    signed_ints = bmp.GetBitmapBits(True)
    img = np.frombuffer(signed_ints, dtype="uint8")
    img.shape = (height, width, 4)   # BGRA
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

    # Cleanup
    win32gui.DeleteObject(bmp.GetHandle())
    memdc.DeleteDC()
    srcdc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwindc)

    return img
Why this matters: No more pygame – you now have a reliable screen‑grab that works on any window, no SDL initialization.

4.2.3 core/overlay.py
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QPen
import sys
import cv2
import numpy as np

class GhostOverlay(QWidget):
    def __init__(self, cfg, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.cfg = cfg
        self.timer = QTimer(self, timeout=self.update_frame, interval=1000 // cfg.refresh_rate)
        self.timer.start()

        # Position the window over the target
        self.update_target_geometry()

    def update_target_geometry(self):
        import win32gui
        left, top, right, bottom = win32gui.GetWindowRect(self.cfg.target_hwnd)
        self.setGeometry(left, top, right - left, bottom - top)

    def update_frame(self):
        # Grab the game screen
        img = grab_window(self.cfg.target_hwnd)  # from core.capture
        ghost = self.render_ghost(img)         # implement your own detection

        # Convert numpy -> QImage
        h, w, _ = ghost.shape
        img_qt = QImage(ghost.data, w, h, QImage.Format_BGR888)
        pix = QPixmap.fromImage(img_qt)

        self._current_pixmap = pix
        self.update()   # triggers paintEvent

    def render_ghost(self, frame: np.ndarray) -> np.ndarray:
        """
        Very naive placeholder: draw a green rectangle at the bottom‑right
        """
        overlay = frame.copy()
        h, w, _ = overlay.shape
        cv2.rectangle(overlay, (w-80, h-80), (w-20, h-20),
                      (0, 255, 0), thickness=cv2.FILLED)
        # Blend with target opacity
        blended = cv2.addWeighted(frame, 1-self.cfg.opacity,
                                 overlay, self.cfg.opacity, 0)
        return blended

    def paintEvent(self, event):
        if not hasattr(self, "_current_pixmap"):
            return
        painter = QPainter(self)
        painter.drawPixmap(QRect(0, 0, self.width(), self.height()),
                           self._current_pixmap)
Why this matters: One‑pixel‑per‑frame painting – the entire overlay is just a QPixmap, no heavy Qt widgets, so CPU stays < 5 %.

4.3 Manual Window Selection Wizard (UI)
ui/wizard.py – a single page with a live preview of the captured screen and a “Select Window” button that uses win32gui.EnumWindows to list all windows; the user clicks the target; the HWND is saved to the config.

class WindowPickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # layout: QListWidget (window names), QLabel (preview), QPushButton(Select)
        # When a list item is selected, call capture.grab_window(hwnd) and show preview.
        # On Accept, write config.save(Path(...))
Acceptance Criteria (End‑of‑Phase 1):

Running python -m tetris_overlay opens the wizard.
The user picks a window → config file written.
The overlay appears, draws a green rectangle (placeholder ghost) on that window.
No unhandled exception occurs.
If any of those fail, go back and fix the offending module before moving on.

5️⃣ PHASE 2 – USER‑FRIENDLY EXPERIENCE (Day 6‑10)
Sub‑Phase	Tasks	Owner	Effort
2.1 Installer	• Add PyInstaller spec (--onefile --windowed).
• Create Inno Setup script: copy *.exe, register uninstaller, add Start‑Menu entry, add optional auto‑start registry key.
• Sign the exe (self‑signed for now; plan to buy a Code Signing cert).	Dev 2	1 d
2.2 Auto‑Detection	• Implement core/detection.py that enumerates top‑level windows, scores them (title keywords + exe name).
• Add “Rescan” button to the wizard and a fallback “Manual” button.	Dev 1	1 d
2.3 Settings GUI	• ui/settings_dialog.py with: opacity slider, colour picker, hotkey selector (e.g., Ctrl+Alt+G to toggle ghost).
• “Reset to defaults” and “Export / Import” buttons.	UI Dev	1 d
2.4 Error Handling	• Central utils/logger.py (loguru → rotating log, level INFO).
• Wrap all public APIs in try/except that calls show_error(message).
• Create resources/error.png for a friendly “something went wrong” dialog.	Dev 2	0.5 d
2.5 Documentation stub	• Write docs/INSTALL.md (download installer → double‑click → wizard).
• Add screenshots of wizard, tray icon, settings.	Writer	0.5 d
2.6 CI bump	• Extend GitHub Action to run the installer build and upload as artifact.	Dev 2	0.25 d
2.7 End‑to‑End smoke test	• A small script that launches the installer in a temporary VM, runs the overlay, verifies ghost appears.	QA	0.5 d
Acceptance Criteria (End‑of‑Phase 2):

Users can download tetris-overlay‑setup.exe, run it, and nothing else is required on the machine.
The wizard auto‑detects the game ≥ 90 % of the time (tested on Windows 10 & 11 with Chrome, Edge, Steam).
Settings can be changed in the UI and are persisted.
Any error (e.g., “game not found”) shows a friendly message and does not crash.
If any of these fail, push a hot‑fix before moving to Phase 3.

6️⃣ PHASE 3 – POLISH & PRODUCTION (Day 11‑15)
Item	Work	Owner	Effort
3.1 Code Signing (real certificate)	Buy a low‑cost code‑signing cert (≈ $120/yr) and integrate into Inno Setup (SignTool).	DevOps	0.5 d
3.2 Auto‑Update System	Use PyUpdater or a custom JSON manifest + self‑updater stub.	Dev 1	1 d
3.3 Performance Optimization	Profile with py-spy → ensure <5 % CPU, <100 MiB RAM.
If necessary, move capture to a separate thread and use QThread signals to avoid GIL contention.	Dev 2	0.75 d
3.4 Comprehensive Test Suite	• Unit tests for config, capture, detection.
• Integration test using pywinauto to start a dummy Tetris exe (or use Notepad as a stand‑in).
• UI tests with pytest-qt.	QA + Dev 1	1 d
3.5 Full Documentation	• docs/USER_GUIDE.md (step‑by‑step wizard, troubleshooting).
• docs/FAQ.md.
• Video tutorial (screen capture + narration, < 5 min).	Writer	1 d
3.6 Support Infrastructure	• Enable GitHub Issues template (bug report, crash log attachment).
• Add a “Send Crash Report” button that sends a zip of overlay.log + config to a private webhook (e.g., a simple Flask endpoint).	DevOps	0.5 d
3.7 Release	Tag v1.0.0, create GitHub Release (binary + checksum), publish docs to GitHub Pages.	Lead Dev	0.25 d
3.8 Post‑Launch Monitoring	Simple analytics (opt‑in) that POSTs {"version":"1.0.0","os":"win10","cpu":3.2} to a Google‑Analytics‑style endpoint.	DevOps	0.25 d
Acceptance Criteria (End‑of‑Phase 3):

Installer is digitally signed – Windows SmartScreen no longer blocks it.
Auto‑update works silently (or via user‑prompt).
Performance metrics (CPU < 5 %, RAM < 100 MiB) measured on a clean Windows 10 VM.
Full test coverage ≥ 80 % (unit + integration).
User documentation complete, video uploaded to YouTube, link in README.
Support ready – users can file a bug, attach a log, and you receive it automatically.
If any of those are missing, you do not ship – the product is not “product‑ready”.

7️⃣ DETAILED GANTT‑LIKE TIMELINE (3 Weeks)
Week	Monday	Tuesday	Wednesday	Thursday	Friday
W1 – Foundation & Core	Create refactor/v1, move dead code, set up CI, add pyproject	Add license/.gitignore, start core/config & core/capture	Finish core/overlay, get a static ghost rectangle working	Build manual‑select wizard, test on Tetris client	Smoke‑test, merge to dev branch, tag v0.1‑prototype.
W2 – UX & Distribution	Build installer (PyInstaller + Inno Setup)	Auto‑detect implementation, add tray icon	Settings UI (opacity, colour, hotkey)	Error handling + logger, create friendly dialogs	Write INSTALL.md, add CI artifact upload, conduct UAT with 2 non‑tech users.
W3 – Polish & Ship	Purchase code‑signing cert, integrate signing	Auto‑update stub, performance profiling	Write full user guide + FAQ + short video	Create GitHub issue template & crash‑report hook	Tag v1.0.0, publish Release, push docs to Pages; hand‑off to support.
Key Milestones – Prototype (end of W1), User‑Ready (end of W2), Production (end of W3).

If any milestone is missed, extend the current week, don’t jump ahead. The schedule is tight but achievable because you are limited to a single repo with a small team.

8️⃣ RISK MATRIX & Mitigations
Risk	Likelihood	Impact	Mitigation
Legacy dead code contaminates new modules	Medium	High (hard‑to‑debug crashes)	Move everything under legacy/, add # noqa: F401 imports only for reference.
PyInstaller misses a DLL (OpenCV, Qt)	Medium	Medium	In CI, test the built exe on a clean Windows VM (windows-latest runner). Add missing DLLs manually via --add-data.
Auto‑detection fails on exotic Tetris client	High (many window titles)	Medium	Provide a fallback manual selector and clear UI to pick the window. Log the title/exe name for future pattern addition.
Installer flagged as malware	Low (if unsigned)	High	Use a code‑signing certificate; run the installer through VirusTotal before release.
Performance spikes when game runs at 144 Hz	Medium	Medium	Capture at a fixed 30 Hz; do not sync to game frame rate. Use a separate thread for capture.
User data loss on config corruption	Low	Medium	Store config in %APPDATA%\tetris_overlay\config.json and backup to config.json.bak on each save. Validate on load.
Budget overrun	Low (fixed $18k)	Low	Track daily person‑hours in a simple spreadsheet; stop adding “nice‑to‑have” features after Phase 2.
9️⃣ WHAT TO KEEP FROM THE CURRENT REPO (and why)
File / Folder	Keep?	Reason
config.json (or the schema)	YES – migrate into core/config.py (Pydantic).	
legacy/ (all broken main.py, pygame_*.py)	YES – archive for reference; never import.	
Any image‑processing utils that are pure OpenCV functions (e.g., find_grid.py)	YES – copy into core/utils/.	
Existing README.md (developer notes)	YES – move to docs/DEVELOPER_GUIDE.md.	
requirements.txt	NO – replace with pyproject.toml (pinned).	
.vscode/ or other IDE configs	NO – irrelevant for product.	
setup.cfg (if present)	NO – we’ll use pyproject.toml.	
LICENSE (if missing)	Add MIT.	
Any test files that at least import modules (even if they only test import)	YES – keep as a sanity‑check, but expand to real tests.	
10️⃣ QUICK‑START FOR THE TEAM (What you need to do right now)
Create the refactor branch

git checkout main
git checkout -b refactor/v1
Move everything that currently crashes

mkdir -p legacy
git mv *.py legacy/
# keep config.json at repo root for now
Add the skeleton (copy‑paste the folder tree shown in §4).
Use poetry init or pipenv to generate a pyproject.toml with:

[project]
name = "tetris-overlay"
version = "0.1.0"
dependencies = [
    "PySide6==6.7.2",
    "opencv-python==4.9.0.80",
    "pywin32==306",
    "pydantic==2.7",
    "loguru==0.7.2"
]
Push the new branch and open a PR titled “Refactor – foundation for product”.
Set the PR status checks to require CI passes.

Assign owners (according to the table in §5).

Kickoff a 30‑minute stand‑up: go through the Phase 1 tasks, assign who writes capture.py, who writes overlay.py, etc.

Set up the CI workflow (copy paste the minimal workflow below):

name: CI

on: [push, pull_request]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install deps
        run: |
          pip install -U pip
          pip install poetry
          poetry install --no-root
      - name: Lint
        run: |
          poetry run ruff check src/
          poetry run black --check src/
      - name: Tests
        run: poetry run pytest -q
      - name: Build exe
        run: |
          poetry run pyinstaller --onefile --windowed src/tetris_overlay/__main__.py -n tetris_overlay
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: tetris-overlay-exe
            path: dist/tetris_overlay.exe
This will fail fast if any import crashes, keeping the broken code from ever reaching main.

11️⃣ FINAL WORD (No sugar‑coating)
Your current code is a dead end. Trying to “patch” it will keep you in a perpetual debugging loop.
You must replace the core rendering and packaging layers. Keep only the config schema and any pure OpenCV utilities.
Follow the phased plan above exactly; every phase has a concrete “acceptance criteria” that must be met before you move on.
Never merge code that fails the CI – let the CI be the gatekeeper.
Budget and timeline: the numbers in the table (≈ $18k, 3 weeks) are realistic only if you stick to the plan and stop adding scope creep after Phase 2.
If management signs off on the full‑rebuild approach (Option 1) you will have a product that a non‑technical user can install, run, and love. If they balk at the cost, the pivot to an existing open‑source overlay (Option 3) is the only sane alternative – but that abandons the custom “ghost piece” feature you’ve been chasing.

Take the plan, execute it, and stop asking “why does my code keep crashing?” You have a roadmap, a clean repo layout, and a real path to shipping a professional product.

Good luck – you’ve got three weeks and a clear‑cut battle plan. Execute or keep drowning in spaghetti. 🚀