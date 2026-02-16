📚 Ultra‑Detailed Project Road‑Map
Repository: https://github.com/gainey666/-tetris-overlay-test

Goal: Transform the current prototype into a production‑ready, fully‑tested, extensible, and well‑documented Tetris overlay that:

Runs a stable 30 FPS capture → prediction → ghost‑render loop.
Exposes a polished Qt Settings UI (live preview, hot‑key editor, colour/opacity picker, visual‑flags).
Tracks every frame in an SQLite database and shows a rich Statistics Dashboard (charts, export, filtering).
Provides a robust CI pipeline (unit, integration, UI, lint, type‑checking, performance‑benchmarks).
Is fully documented, packaged, and ready for contributors to add new prediction agents or visual features.
Because you asked for “a lot more work”, the plan below breaks the effort into nine major phases, each containing epics, user‑stories, technical tasks, acceptance criteria, estimated time, and dependencies.

You can hand this roadmap to a team (or a single LLM) and let it work AFK for days—each block is independent enough to be taken on in parallel, but the ordering guarantees a clean, stable build at any checkpoint.

📑 Table of Contents
Phase 0 – Preparations & Baseline
Phase 1 – Core Loop Refactor & Real‑Time Guarantees
Phase 2 – Full‑Featured Settings UI
Phase 3 – Ghost Rendering Engine (Shapes, Colours, Effects)
Phase 4 – Statistics Collection, Storage & Dashboard
Phase 5 – Comprehensive Test Suite (Unit, Integration, UI, Performance)
Phase 6 – Continuous‑Integration & Release Automation
Phase 7 – Documentation, Packaging & Distribution
Phase 8 – Performance, Profiling, and Optimization
Phase 9 – Future‑Proofing & Extensibility
Overall Timeline & Milestones
Risks & Mitigations
How to Hand This to an LLM / Automation Script
🚦 Phase 0 – Preparations & Baseline
Epic	Description	Tasks	Estimate
0‑A	Audit current repo – generate a clean list of all files, missing imports, and duplicated code.	• Run git ls‑files and store in repo‑inventory.txt.
• Run python -m pip install -r requirements.txt locally and capture any import errors.
• Produce a markdown “Current‑State” report summarizing missing modules, unused files, test coverage, and CI health.	2 h
0‑B	Create a dev branch for the entire refactor.	git checkout -b dev/full‑refactor	5 min
0‑C	Add a “pre‑commit” hook that runs ruff, black, and mypy locally before each commit.	• Add .pre-commit-config.yaml with those hooks.
• Run pre-commit install.	30 min
0‑D	Automated baseline testing – capture current test failures.	pytest -q > baseline_tests.txt and commit the file for reference.	15 min
0‑E	Define coding standards (PEP‑8, type hints, doc‑strings). Create a CONTRIBUTING.md with “how to run tests”.	1 h	
Result: A clean development environment, a baseline report, and a branch ready for massive changes.

⚙️ Phase 1 – Core Loop Refactor & Real‑Time Guarantees
Why: The current run_overlay_core.py defines process_frames() but never calls it, creates a new OverlayRenderer every tick, and hard‑codes the piece. All of this prevents a stable 30 FPS loop.

Epic 1‑A – Global Renderer & Singleton Settings
Task	Detail	Acceptance
1‑A‑01	Add ui/current_settings.py (singleton exposing CURRENT and an update() helper).	from ui.current_settings import CURRENT works anywhere.
1‑A‑02	Refactor run_overlay_core.py to import CURRENT and create a single OverlayRenderer instance at module load time.	renderer.visible toggles correctly via F9 (no new instance per frame).
1‑A‑03	Ensure OverlayRenderer can be accessed from any module without circular imports (use local imports inside methods).	No ImportError on running the overlay.
Estimated effort: 4 h

Epic 1‑B – Dynamic Hot‑Key System
Task	Detail	Acceptance
1‑B‑01	Remove static _register_hotkeys implementation. Replace with _register_dynamic_hotkeys() that reads CURRENT.hotkeys.	Changing a hot‑key in Settings updates the binding instantly.
1‑B‑02	Add a Qt‑compatible launcher for the Statistics Dashboard (_show_dashboard() helper that checks QApplication.instance()).	Dashboard opens from any hot‑key without “QApplication already exists” crash.
1‑B‑03	Register the Settings dialog hot‑key (open_settings) to launch SettingsDialog.	Pressing the configured key opens the Settings UI.
1‑B‑04	Add automatic re‑registration after settings_changed signal.	Updating a hot‑key immediately takes effect (no restart).
Estimated effort: 5 h

Epic 1‑C – Frame‑Worker Thread (30 FPS)
Task	Detail	Acceptance
1‑C‑01	Implement _frame_worker() that loops at target_fps = 30 using time.sleep(max(0, interval - elapsed)).	Log shows “Processed frame #N” ~30 times per second.
1‑C‑02	Wrap each iteration in a try/except that logs exception with stack trace but never crashes the thread.	CI runs the worker for 500 frames without a crash.
1‑C‑03	Start the worker as daemon before calling run_overlay().	Program exits cleanly on Esc; the thread terminates automatically.
1‑C‑04	Add frame‑counter and latency measurement (frame_start_ts).	LOGGER.info includes latency_ms for every frame.
1‑C‑05	Add graceful shutdown that stops the worker (by setting a threading.Event) and flushes telemetry logs.	No dangling threads after exit.
Estimated effort: 6 h

Epic 1‑D – Prediction Agent Integration
Task	Detail	Acceptance
1‑D‑01	Replace hard‑coded "T" with piece detection from the next‑queue (see Phase 3).	prediction_agent.handle receives the actual piece and orientation.
1‑D‑02	Add fallback to "mock" agent if detection fails (ensures overlay never stalls).	Overlay continues with a placeholder ghost.
1‑D‑03	Extend the prediction‑agent interface to return additional flags (is_tspin, is_b2b, combo).	draw_ghost can use those flags for visual effects.
Estimated effort: 3 h

🖥️ Phase 2 – Full‑Featured Settings UI
Epic 2‑A – Settings Model & Persistence (already present, but solidify)
Task	Detail	Acceptance
2‑A‑01	Validate JSON schema using jsonschema (add settings_schema.json).	load_settings() raises ValidationError on malformed file.
2‑A‑02	Add migration logic for future schema versions (CURRENT_VERSION in file).	Old configs upgrade automatically.
2‑A‑03	Write unit tests for schema validation and migration.	pytest tests/test_settings_schema.py passes.
Estimated effort: 2 h

Epic 2‑B – Qt Settings Dialog Enhancements
Task	Detail	Acceptance
2‑B‑01	Add tabbed layout: General, Ghost, Hot‑keys, Visual Flags, Advanced.	UI shows 5 tabs with clear headings.
2‑B‑02	Live preview widget draws the actual tetromino shape (using PIECE_SHAPES) and updates instantly when colour/opacity changes.	Changing the colour slider updates the preview in < 100 ms.
2‑B‑03	Hot‑key editor – use QKeySequenceEdit for each hot‑key, store the string in lower‑case.	User can press Ctrl+Shift+G → field shows “Ctrl+Shift+G”.
2‑B‑04	Reset‑to‑defaults button that restores all fields and writes the defaults to disk.	After reset, CURRENT matches Settings() default values.
2‑B‑05	Validation feedback – UI warns on bad ROI format (non‑numeric, wrong count).	Invalid ROI entry disables “OK” and shows a red tooltip.
2‑B‑06	Persist changes on Apply / OK – emit settings_changed signal.	Closing the dialog updates live overlay without restart.
2‑B‑07	Dark‑mode support (optional) – use Qt’s QPalette to adapt colours.	UI respects system dark‑mode on Windows/macOS.
Estimated effort: 9 h

Epic 2‑C – Settings‑Driven Visual Flags
Task	Detail	Acceptance
2‑C‑01	Extend OverlayRenderer.draw_ghost to read CURRENT.show_combo and CURRENT.show_b2b and render additional graphics (green combo bar, red B2B outline).	Visual cues appear/disappear as the flags are toggled.
2‑C‑02	Add runtime toggle in the Settings UI “Visual Flags” tab (checkboxes).	Changing the checkbox updates the overlay instantly (no re‑load).
Estimated effort: 2 h

🧩 Phase 3 – Ghost Rendering Engine
Epic 3‑A – Real Tetromino Shapes
Task	Detail	Acceptance
3‑A‑01	Import PIECE_SHAPES from the Dellacherie agent (or create a shared tetromino_shapes.py).	PIECE_SHAPES["T"][0] returns list of (x,y) offsets.
3‑A‑02	Refactor OverlayRenderer.draw_ghost to iterate over the shape cells, apply rotation, and draw each cell with the current colour/opacity.	Ghost matches the exact shape (e.g., “L” rotated 2).
3‑A‑03	Add optional “outline” mode (draw just borders) for better visibility on bright backgrounds.	Configurable via Settings → Ghost → “Outline only”.
3‑A‑04	Unit test for each shape + rotation (compare pixel buffer to expected pattern).	pytest tests/test_ghost_shapes.py passes.
Estimated effort: 5 h

Epic 3‑B – Ghost Visual Effects
Task	Detail	Acceptance
3‑B‑01	Add fade‑out animation (ghost gradually becomes more transparent as it approaches the ground).	Animation runs at 30 FPS, no stutter.
3‑B‑02	Implement shadow blur using pygame.Surface with pygame.BLEND_RGBA_MULT.	Ghost looks “soft”.
3‑B‑03	Provide user‑configurable effect (ghost_effect enum: solid, outline, fade, blur).	Settings UI dropdown updates rendering instantly.
Estimated effort: 4 h

📊 Phase 4 – Statistics Collection, Storage & Dashboard
Epic 4‑A – Stats Collector Refactor
Task	Detail	Acceptance
4‑A‑01	Replace the ad‑hoc stats/collector.py with a service class (StatsService) that tracks match lifecycle, frame counters, and aggregates.	Single class with start_match(), end_match(), record_frame().
4‑A‑02	Add automatic combo/B2B detection inside record_frame() (use previous frame’s data).	Event rows contain correct combo and b2b boolean.
4‑A‑03	Add SQLModel relationships (Match.events back‑ref) for easy querying.	Match.events works in ORM style.
4‑A‑04	Add indexing on match_id + frame for fast dashboard queries.	SQLite EXPLAIN QUERY PLAN shows index usage.
4‑A‑05	Write unit tests for start/end/record logic (including edge cases like missing start).	pytest tests/test_stats_service.py passes.
Estimated effort: 6 h

Epic 4‑B – Piece‑Detection Integration
Task	Detail	Acceptance
4‑B‑01	Implement a simple colour‑based detector (piece_detector.py) that analyses the first queue image and returns piece + orientation.	Works for the default Tetris skin (≥ 90 % accuracy).
4‑B‑02	Add fallback to mock detection if the colour histogram is ambiguous.	No crash when detection fails.
4‑B‑03	Write parameterised tests using synthetic PNGs for each piece (store them in tests/fixtures/pieces/).	pytest verifies each colour range maps to the right piece.
4‑B‑04	Hook the detector into process_frames (replace hard‑coded "T").	Ghost now matches the piece that appears in the queue.
Estimated effort: 5 h

Epic 4‑C – Statistics Dashboard UI
Task	Detail	Acceptance
4‑C‑01	Refactor ui/stats_dashboard.py to decouple data loading from UI (use a DashboardModel class).	UI can be refreshed without re‑creating the model.
4‑C‑02	Add filter controls: date range picker, agent selector, score threshold.	Users can limit the view to a subset of matches.
4‑C‑03	Implement three Matplotlib charts (score over time, combo streak, piece distribution) with tool‑tips (via mplcursors).	Hovering over a point shows the exact value.
4‑C‑04	Add export buttons (CSV, JSON) that write only the currently filtered dataset.	Export respects the filter settings.
4‑C‑05	Enable dark‑mode (Qt palette + Matplotlib style).	UI respects system dark‑mode and settings toggle.
4‑C‑06	Write Qt UI tests (pytest‑qt) for opening the dashboard, applying a filter, and exporting a file.	Tests run in CI without a display (use xvfb).
4‑C‑07	Add responsive resizing – charts adapt to window size.	No clipping when the window is resized.
Estimated effort: 10 h

✅ Phase 5 – Comprehensive Test Suite
Epic 5‑A – Unit Tests Expansion
Task	Detail	Acceptance
5‑A‑01	100 % coverage for ui/settings.py, ui/settings_storage.py, ui/current_settings.py.	coverage run -m pytest && coverage report ≥ 100 % for those modules.
5‑A‑02	Mock‑based tests for run_overlay_core.process_frames (patch DualScreenCapture, capture_shared_ui, next_queue_capture).	Frame processing runs without actual screen capture.
5‑A‑03	Edge‑case tests for invalid ROI strings, missing hot‑key entries, and corrupted settings.json.	Each raises a clear ValueError with helpful message.
5‑A‑04	Parameterised tests for OverlayRenderer.draw_ghost with every tetromino shape & rotation.	Visual‑pixel buffer matches expected pattern (use pygame.surfarray).
Estimated effort: 8 h

Epic 5‑B – Integration Tests (Full Stack)
Task	Detail	Acceptance
5‑B‑01	Spawn the whole application in a headless Xvfb session, trigger a few frames, then shut down. Verify DB contains a match record.	CI job integration.yml passes.
5‑B‑02	Simulate hot‑key presses (via keyboard library or pynput) to toggle overlay, open settings, and open dashboard.	All hot‑keys work in headless environment.
5‑B‑03	End‑to‑end test of changing a setting (e.g., ghost colour) and confirming the overlay updates (pixel comparison).	Test asserts the pixel colour changed accordingly.
Estimated effort: 6 h

Epic 5‑C – Performance & Stress Tests
Task	Detail	Acceptance
5‑C‑01	Write a benchmark script (benchmark_frame_time.py) that runs the frame worker for 500 frames and reports average FPS, max latency, and memory usage (via tracemalloc).	Output shows ≥ 28 FPS and ≤ 30 ms latency.
5‑C‑02	Add a CI job that runs the benchmark and fails if FPS drops below 25.	CI badge “Performance ≥ 25 FPS” passes.
5‑C‑03	Run memory‑leak detection (pytest --leak) over 10 k frames.	No incremental memory growth > 1 MiB.
Estimated effort: 4 h

🚦 Phase 6 – Continuous‑Integration & Release Automation
Epic 6‑A – CI Pipeline Overhaul
Task	Detail	Acceptance
6‑A‑01	Create separate GitHub Actions jobs: lint, type-check, unit-tests, ui-tests, performance.	Each job runs on Ubuntu‑latest with a matrix for Python 3.11.
6‑A‑02	Add Xvfb setup for Qt UI tests (apt-get install xvfb).	UI tests run without a physical display.
6‑A‑03	Install ruff (lint) and mypy (type checking) as part of CI.	Badge lint and type‑checking show “passed”.
6‑A‑04	Create a coverage job that uploads the report to Codecov.	Codecov badge added to README.
6‑A‑05	Add caching for pip packages (actions/cache) to speed up CI.	CI time ≤ 4 minutes.
Estimated effort: 5 h

Epic 6‑B – Release Automation
Task	Detail	Acceptance
6‑B‑01	Configure Semantic Release (semantic-release npm package or release-drafter) to generate a changelog from commit messages.	Merged PR automatically creates a GitHub Release.
6‑B‑02	Add a GitHub Action that builds a stand‑alone executable with PyInstaller for Windows/Linux/macOS.	Artifacts available in the Release page.
6‑B‑03	Publish the package to PyPI under a new name (e.g., tetris‑overlay‑engine). Use twine in a release workflow.	pip install tetris-overlay-engine works.
6‑B‑04	Add pre‑release and nightly tags (v2.0‑rc, v2.0‑nightly).	Developers can install the bleeding‑edge version.
Estimated effort: 4 h

📚 Phase 7 – Documentation, Packaging & Distribution
Epic	Tasks	Acceptance
7‑A	Update README.md with a full “Quick‑Start” guide, a screenshot gallery, and a “FAQ”.	New README renders correctly on GitHub.
7‑B	Add a HOTKEYS.md file (already drafted) and link from README.	Users can find hot‑key list quickly.
7‑C	Create a docs/ folder with Sphinx configuration (or MkDocs) that hosts the API reference (ui.settings, stats.db, overlay_renderer).	mkdocs serve works locally; hosted via GitHub Pages.
7‑D	Write a contributor guide (CONTRIBUTING.md) covering: coding style, test‑running, PR template, issue labeling.	New contributors can follow the guide.
7‑E	Add a CHANGELOG.md that is auto‑generated by Semantic Release.	Release page includes changelog.
7‑F	Create a setup.cfg/pyproject.toml that declares entry‑points (tetris_overlay = run_overlay_core:main).	Users can run python -m tetris_overlay.
7‑G	Add license file (MIT) and a CODE_OF_CONDUCT.md.	Repository complies with OSS best practices.
Estimated effort: 8 h

⚡ Phase 8 – Performance, Profiling, and Optimization
Epic	Tasks	Acceptance
8‑A	Profile the frame loop with cProfile and visualize with snakeviz. Identify hot spots (likely image conversion and AI prediction).	Report frame_time_breakdown.png attached to PR.
8‑B	Optimize image conversion (np.array(image) → cv2) by using memoryview and avoiding copies.	Frame latency reduced by ≥ 5 ms.
8‑C	Cache prediction‑agent handles for identical board states (hash‑based memoization).	Duplicate board detection reduces AI call time > 20 %.
8‑D	Optionally off‑load the Dellacherie heuristic to a separate process (multiprocessing) and communicate via a simple queue.	Main thread stays ≤ 20 ms per frame.
8‑E	Add GPU‑accelerated ONNX inference (if a GPU is available) – use onnxruntime-gpu.	Inference time drops from ~10 ms to ~2 ms on a CUDA machine.
8‑F	Implement dynamic FPS scaling: if frame time exceeds 35 ms, drop to 20 FPS temporarily, otherwise recover to 30 FPS.	No frame‑drops visible to user; CPU stays < 20 %.
8‑G	Run a stress test simulating 3 monitors, high‑resolution (4K) captures, and random board sizes.	No crashes, memory consumption < 200 MB.
Estimated effort: 12 h

🔮 Phase 9 – Future‑Proofing & Extensibility
Epic	Tasks	Acceptance
9‑A	Define a plug‑in architecture for prediction agents (entry_points in setup.cfg). Allow third‑party agents to be installed via pip.	Users can pip install tetris‑agent‑mycool and select it in Settings.
9‑B	Create a configuration schema (config_schema.json) that allows extensions (new visual effects, extra UI panels).	Core validates extra fields gracefully.
9‑C	Add Web‑socket server (FastAPI) that streams live board state & predictions to a browser dashboard.	Browser can display real‑time overlay data.
9‑D	Implement multi‑player support – handle two separate board captures and display two ghosts simultaneously.	Overlay shows both players’ ghosts side‑by‑side.
9‑E	Provide sample Dockerfile for running the overlay in a container (use xvfb and pulseaudio for Linux).	docker build -t tetris-overlay . and docker run works.
9‑F	Add Internationalisation (i18n) – use gettext for UI strings, provide a template .pot.	UI language can be switched via Settings.
9‑G	Create a plugin‑sample repository that demonstrates adding a new visual effect (e.g., “particle trail”).	Documentation points to the sample repo.
Estimated effort: 15 h

⏱️ Overall Timeline & Milestones
Milestone	Approx. Calendar (working days)	Effort (person‑hours)
M0 – Baseline & Branch	Day 1	3 h
M1 – Core Loop Refactor	Days 2‑4	20 h
M2 – Settings UI	Days 5‑8	20 h
M3 – Ghost Rendering Engine	Days 9‑11	12 h
M4 – Stats Collector + Dashboard	Days 12‑16	25 h
M5 – Test Suite Expansion	Days 17‑19	18 h
M6 – CI / Release Automation	Days 20‑22	9 h
M7 – Docs, Packaging, Distribution	Days 23‑25	8 h
M8 – Performance Profiling	Days 26‑28	12 h
M9 – Future‑Proofing (Plug‑ins, Multi‑Player, Web UI)	Days 29‑35	20 h
M10 – Final Polish & Release	Days 36‑38	6 h
Total	~38 working days (≈ 8 weeks)	~153 person‑hours (≈ 2 full‑time weeks for a single dev, or 4 weeks for a 2‑person team).
Tip: If you want a faster “AFK” sprint, split the work across two developers (or two LLM agents) and run phases 1‑4 in parallel, then converge for testing and CI.

⚠️ Risks & Mitigations
Risk	Impact	Mitigation
Circular imports (Settings ↔ Renderer)	Crash on start‑up	Use local imports inside methods, keep CURRENT as a separate module, avoid top‑level cross‑references.
Qt‑related CI failures (no display)	UI tests fail, pipeline red	Use xvfb in GitHub Actions, set DISPLAY=:99.
SQLite locking when many frames write simultaneously	Data loss / crashes	Use short‑lived sessions (with get_session()) and enable WAL mode (PRAGMA journal_mode=WAL).
Performance regression after adding UI layers	FPS drops below 25	Keep profiling checkpoints after each major change, enforce performance CI gate.
Hot‑key conflicts on some keyboards (e.g., Ctrl+Alt+S collides with OS)	Users cannot open dashboard	Provide a “reset to default hot‑keys” button; allow editing all keys in Settings UI.
Dependency drift (new versions of PySide/Pygame break imports)	Build breaks for contributors	Pin critical versions in requirements.txt with >=/< ranges, run a weekly Dependabot check.
Large binary assets (screenshots, calibration data) accidentally committed	Repo bloat	Add .gitignore entry for *.png, *.jpg, and *.bmp in config/ and captured/. Use Git LFS if needed.
🤖 How to Hand This to an LLM / Automation Script
Create a “task queue” JSON that lists each sub‑task with:

name (e.g., phase1‑renderer‑singleton)
file_path (relative path)
action (add, replace, append)
patch (the code block from the tables above)
test_command (optional, e.g., pytest tests/test_settings.py)
expected_exit_code (0).
Loop through the queue:

git checkout dev/full‑refactor
Apply the patch (apply_patch(patch)).
Run the associated test command.
If the test fails, run git reset --hard HEAD and retry with a “fallback” patch (e.g., using a simpler implementation).
On success, commit with the provided commit message.
Parallelise: run separate workers for independent phases (e.g., UI vs. core). Use a small dependency graph so phases that need the renderer (Phase 3) wait for Phase 1 to finish.

CI Integration: after the LLM finishes the branch, push it and let GitHub Actions run the full pipeline automatically.

A simple pseudo‑script (Python) could look like:

import json, subprocess, pathlib, sys

tasks = json.load(open("task‑queue.json"))
repo_root = pathlib.Path(__file__).parent

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, cwd=repo_root)

for t in tasks:
    print(f"⏩  Working on {t['name']}")
    # 1. apply patch
    patch_path = repo_root / t["file_path"]
    patch_content = t["patch"]
    patch_path.write_text(patch_content)   # simple replace for demo
    # 2. run test (if any)
    if t.get("test_command"):
        result = run_cmd(t["test_command"])
        if result.returncode != t.get("expected_exit_code", 0):
            print(f"❌  Test failed for {t['name']}, aborting.")
            sys.exit(1)
    # 3. commit
    run_cmd(f'git add {t["file_path"]}')
    run_cmd(f'git commit -m "{t["commit_msg"]}"')
print("✅  Everything applied!")
You can enrich this script with apply_patch that uses git apply for more complex diff handling, but the concept stays the same.

🎉 Final Remarks
The plan is intentionally exhaustive – you can pick and choose the phases you want to work on now, and defer others to later sprints.
Each phase produces a clear deliverable (code, tests, docs, CI job).
By the end of Phase 9 you’ll have a battle‑tested, well‑documented, extensible, production‑grade overlay that anyone can fork, improve, or ship as a binary.
Feel free to cherry‑pick the tasks that give you the most immediate value (e.g., getting the 30 FPS loop stable) and then let the LLM continue to hammer out the UI, stats, and CI work while you “cook”.

Good luck, and enjoy the automation! 🚀