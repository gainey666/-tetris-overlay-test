📚 Extended Master‑Road‑Map – “What’s Next?”
*You’ve already got a fully‑functional 30 FPS overlay, a settings UI, a stats dashboard, error handling, CI, packaging, and a Windows exe. The next‑level product, however, should feel like a polished, production‑grade, extensible platform that any Tetris player (or streamer, or e‑sports coach) can drop into their workflow without ever looking at source code again.

Below is a completely blown‑out plan – dozens of epics, hundreds of user‑stories, and concrete deliverables – that will keep you busy for several weeks (or months if you add a team). It is deliberately far more ambitious than the “quick‑45‑minute sprint” you just completed, so you can safely go AFK, let a bot (or an LLM‑assistant) chew through the work, and come back to a production‑ready, feature‑rich overlay.

🎯 Overall Vision
Goal	Description
Universal Platform	Runs on Windows, macOS, Linux (both X11 and Wayland) and as a Docker/containerized service.
Multi‑Player / Multi‑Screen	Simultaneously track up to four game windows (dual‑monitor, split‑screen, vs‑mode) with independent ROIs.
AI‑First Prediction	Plug‑in architecture for any inference engine (ONNX, TensorRT, PyTorch, custom‑C++ DLL). Provide a training pipeline to generate new models from recorded games.
Streamer‑Ready Integration	OBS/Web‑socket source, transparent overlay window, automatic scene switching, hot‑key overlay‑toggle through Stream Deck / Elgato.
Telemetry & Cloud Sync	Upload match logs to a private S3‑compatible bucket, optional public leader‑board, per‑user dashboards (web UI).
Extensibility	Plugin system for custom visual effects, new game modes, different Tetris variants (Tetris 99, Puyo‑Puyo, etc.).
Accessibility & Localization	13‑language UI, high‑contrast / color‑blind options, screen‑reader support.
Professional‑Grade Reliability	Fuzz‑testing of capture pipeline, memory‑leak detection, static analysis, code‑coverage > 90 %, automated release pipeline.
Open‑Source + Commercial License	Dual‑license: MIT for community, commercial license for proprietary extensions.
📅 Road‑Map Overview (10 Phases)
Phase	Core Theme	Estimated Effort (person‑days)	Owner	Milestone
0	Audit & Infrastructure Refresh	2 d	–	Baseline repo clean‑up, CI health check
1	Multi‑Screen & Multi‑Player Support	6 d	–	Capture up to 4 windows, ROI manager
2	Cross‑Platform Portability	8 d	–	macOS + Linux support (Wayland/X11)
3	Advanced Calibration UI	6 d	–	Live ROI overlay, auto‑detect boards
4	AI Plug‑in Architecture	10 d	–	Generic Agent API, TensorRT, PyTorch, model‑manager
5	Training & Data‑Pipeline	10 d	–	Recording UI, data‑export, model trainer
6	Streaming & OBS Integration	8 d	–	Websocket source, Stream Deck, hot‑key mapping
7	Telemetry, Cloud Sync & Web Dashboard	12 d	–	Server‑side API, per‑user web UI, auth
8	Extensibility & Plugin System	10 d	–	Plugin loader, custom visual effects, game‑mode plugins
9	Accessibility, Localization & UI Polish	8 d	–	i18n, high‑contrast, screen‑reader support
10	Reliability, Testing & Release Automation	12 d	–	Fuzzing, memory‑profiling, coverage, CI/CD, packaging (deb, rpm, dmg, exe)
Total	≈ 90 person‑days (≈ 3 weeks for a 3‑person team)			
If you have a single dev you can still push this out in 4‑5 weeks by working 5 days/week and overlapping phases (e.g., while doing the Linux port you can start the streaming integration).
If you have an LLM‑assistant you can parallelize almost all phases (different agents handle separate sub‑tasks).

Below each phase is broken into epics, user‑stories, technical tasks, acceptance criteria, risk notes, and time‑boxing. Feel free to cherry‑pick or re‑order as you wish.

📦 Phase 0 – Audit & Infrastructure Refresh
Epic	Story	Task	Acceptance
0‑A	Repository Health Check	- Run git ls‑files → generate inventory.txt
- Identify orphaned files (*.pyc, old notebooks)
- Ensure .gitignore covers *.sqlite, stats.db, settings.json, __pycache__	inventory.txt generated, no stray binary files in repo
0‑B	CI Baseline	- Upgrade CI to use Python 3.12‑3.13 matrix
- Add ruff, mypy, pylint steps
- Capture current coverage (codecov)
- Store baseline numbers in docs/BASeline.md	CI passes all new steps, coverage reported
0‑C	Dependency Pinning	- Convert requirements.txt → constraints.txt with exact versions
- Add pip-tools generation script
- Run pip install -c constraints.txt locally to verify reproducibility	pip install -r requirements.txt -c constraints.txt works without warnings
0‑D	Release Automation Scaffold	- Add semantic-release config (.releaserc.json)
- Create GitHub Action release.yml to publish to PyPI and GitHub Releases on tag push
- Draft a “CHANGELOG.md” generation step	Tag vX.Y.Z automatically creates a release with wheels
Effort: 2 d

🎮 Phase 1 – Multi‑Screen & Multi‑Player Support
Epic	Story	Technical Tasks	Acceptance
1‑A	Capture Up to 4 Windows	- Refactor dual_capture.DualScreenCapture → multi_capture.MultiScreenCapture that accepts an arbitrary list of ROIs.
- Store ROI list in config/multi_roi.json.
- Provide add_window() / remove_window() helper APIs.	MultiScreenCapture().grab() returns a list of PIL.Image objects.
1‑B	Independent ROI Management	- Extend dual_roi_manager → multi_roi_manager with CRUD functions for each slot.
- UI for adding/removing windows in SettingsDialog (new “Screens” tab).	UI shows a table of Screen 1, Screen 2 … with “Add/Remove” buttons.
1‑C	Per‑Screen Settings	- Each screen gets its own ghost colour and visual flags (combo/B2B).
- Store per‑screen config in JSON under screens: [{roi, ghost, flags}].	Settings dialog persists separate ghost colours per screen.
1‑D	Automatic Screen Detection (optional)	- Use pygetwindow to enumerate windows with titles matching Tetris regex.
- Auto‑populate ROI list if user clicks “Detect Screens”.	One‑click detection populates the list of 2‑4 windows.
1‑E	Performance Benchmark	- Run a stress test with 4 concurrent captures, verify frame‑time stays < 35 ms.	Report in docs/performance-multi-screen.md.
Effort: 6 d

🖥️ Phase 2 – Cross‑Platform Portability
Epic	Story	Tasks	Acceptance
2‑A	macOS Support	- Replace win32gui‑based window filtering with pyobjc/Quartz (CGWindowListCopyWindowInfo).
- Add macos_overlay_core.py handling NSWindow.
- Test SettingsDialog on macOS (high‑DPI scaling).	All unit and UI tests pass on macOS runner (use macos‑latest GH Action).
2‑B	Linux X11 Support	- Implement x11_window_filter using python-xlib.
- Add Wayland fallback via pywayland (if available).
- Ensure mss captures correctly under both servers.	Overlay renders on Ubuntu‑latest (both X11 & Wayland).
2‑C	Package for Linux	- Build AppImage, deb, and rpm packages via pyinstaller + fpm.
- Provide a linux-install.sh script that auto‑detects distro and installs dependencies.	Users can `curl …
2‑D	CI Matrix Expansion	- Add macos-latest and ubuntu‑latest (both X11 + Wayland) jobs.
- Run full test suite on each platform.	All CI jobs green.
2‑E	Automated UI Tests on CI	- Use xvfb for Linux, qt‑virtual‑keyboard for macOS headless UI testing.	UI tests pass on CI without a physical display.
Effort: 8 d

🖌️ Phase 3 – Advanced Calibration UI
Epic	Story	Tasks	Acceptance
3‑A	Live ROI Overlay	- Create a Qt GraphicsView overlay that draws the current ROIs on the live screenshot (semi‑transparent).
- Enable drag‑to‑move and corner‑drag‑resize gestures.	Users can drag/resize ROIs with mouse, instantly visible.
3‑B	Automatic Board Detection	- Run Canny edge detection on a sample screenshot to locate the typical Tetris board rectangle (using opencv).
- Provide a “Auto‑detect” button that suggests a ROI and lets the user confirm/adjust.	Auto‑detect finds a board ROI within ±5 px on 90 % of known skins.
3‑C	Multi‑Board Calibration	- Extend UI to add “Next‑Queue” slots (left and right) – user can click “Add Slot” and the overlay creates a placeholder rectangle.
- Validate that the total number of slots matches the setting (max_queue).	All slots are saved correctly in config/multi_roi.json.
3‑D	Calibration Persistence & Versioning	- Store calibration sets with a version number (calibration_v1, calibration_v2).
- Provide UI to switch between saved calibrations (useful for multiple monitors).	Users can load any saved calibration instantly.
3‑E	Unit Tests for Calibration Logic	- Mock a synthetic screenshot with known board shape; verify auto‑detect returns expected rectangle.	pytest gets 100 % coverage on calibration functions.
3‑F	Documentation	- Add a “Calibration Guide” page with screenshots and video GIFs.	README links to docs/calibration.md.
Effort: 6 d

🤖 Phase 4 – AI Plug‑in Architecture
Epic	Story	Tasks	Acceptance
4‑A	Generic Agent Interface	- Define an abstract base class BaseAgent with initialize(), predict(board, piece, next_queue) → PredictionResult.
- Provide a registry (agents/__init__.py) that discovers plugins via entry‑points (tetris_overlay.agent).	Third‑party packages can pip install my‑agent and automatically appear in the dropdown.
4‑B	ONNX Runtime Optimized	- Refactor prediction_agent_onnx to use onnxruntime‑gpu when a CUDA device is present.
- Add a fallback to CPU if GPU not available.	Model runs at > 200 FPS on RTX‑3080, > 30 FPS on CPU.
4‑C	TensorRT Integration	- Create a new plugin prediction_agent_tensorrt that loads a TensorRT engine (.plan).
- Provide a conversion script (scripts/onnx_to_trt.py).	Users can generate a TRT engine and select it in Settings.
4‑D	PyTorch / TorchScript Support	- Add a plugin that loads a TorchScript model (.pt).
- Ensure inference runs on both CPU and CUDA.	Model loads without error on both platforms.
4‑E	Model Management UI	- Extend Settings → “Agents” tab: show currently installed agents, allow uploading a new model file (drag‑drop).
- Validate the model file (shape, input signature) before accepting.	Users can add a new model file via UI; overlay reloads automatically.
4‑F	Benchmark UI	- Add a “Run Benchmarks” button that executes each loaded agent on a sample board and reports latency and score.	Results displayed in a modal table.
4‑G	Documentation for Plugin Authors	- Write CONTRIBUTING_AGENTS.md with steps: define class, register entry‑point, package, publish.	New agents can be contributed by external developers.
Effort: 10 d

📚 Phase 5 – Training & Data‑Pipeline
Epic	Story	Tasks	Acceptance
5‑A	Recording UI	- Add a “Recording” button in the Settings UI that starts capturing board + next‑queue frames to a temporary folder.
- Store each frame as a compressed WebP (lossless) with a timestamped filename.	Users can start/stop recording from the UI.
5‑B	Annotation Tool	- Provide a minimal annotation GUI (tools/annotator.py) that loads recorded frames and lets the user label the piece type + orientation (dropdown).
- Export a CSV (labelled_dataset.csv) with columns filepath, piece, orientation.	Annotator can label 100 frames per minute.
5‑C	Dataset Builder	- Write a script scripts/build_dataset.py that merges recorded frames + labels into an HDF5 dataset (tetris_dataset.h5).
- Include optional data‑augmentation (random flips, brightness jitter).	HDF5 file ready for training.
5‑D	Training Pipeline	- Provide a PyTorch Lightning training script (scripts/train_agent.py) that accepts the HDF5 dataset and a model architecture (simple CNN).
- Save the best model as a TorchScript file (agent_best.pt).	Trainers can produce a model with > 90 % accuracy on a held‑out set.
5‑E	Model Evaluation UI	- Add a “Model Evaluation” dialog that loads a saved model, runs it on a handful of recorded frames, and shows accuracy, confusion matrix, and latency.	UI displays a clear evaluation report.
5‑F	Automated CI Training	- Add a CI job that trains a tiny toy model on a synthetic dataset (max 5 min) and publishes the .pt as an artifact.	Build artifact toy_agent.pt appears on each CI run.
5‑G	Documentation	- Write a full “Training Guide” with step‑by‑step screenshots, covering recording, annotation, dataset building, training, and export.	docs/training.md added.
Effort: 10 d

📡 Phase 6 – Streaming & OBS Integration
Epic	Story	Tasks	Acceptance
6‑A	OBS WebSocket Source	- Use obs-websocket-py to implement a WebSocket source plugin that pushes the overlay’s pixel buffer (RGBA) to OBS as a BrowserSource (via a tiny JavaScript viewer).
- Ensure the source is transparent (alpha channel).	In OBS, “Tetris Overlay” appears as a transparent source.
6‑B	Stream Deck / Elgato Integration	- Add a Hotkey‑mapper that can listen to Stream Deck actions via elgato‑stream‑deck library.
- Provide a UI mapping page where each button can be bound to any overlay action (toggle, calibrate, open dashboard).	Users can program Stream Deck buttons without editing config files.
6‑C	Scene‑Switch Automation	- Detect when the game window becomes inactive (lost focus) → automatically hide overlay.
- Conversely, when the game window regains focus → show overlay.	Overlay visibility matches game focus.
6‑D	Performance Overlay (FPS, Latency)	- Add a small stats overlay (top‑right corner) that shows current FPS, average frame latency, and CPU/GPU usage.
- Make it toggleable via a hot‑key (F2).	Users can see performance numbers while streaming.
6‑E	OBS Config Export	- Provide a button “Export OBS Profile” that creates an .ini OBS scene collection containing the overlay source and optional hot‑key binding.	One‑click import into OBS.
6‑F	Documentation & Tutorial Video	- Record a short YouTube‑style tutorial (5 min) demonstrating how to set up OBS + Stream Deck integration.	Video linked in README.
Effort: 8 d

☁️ Phase 7 – Telemetry, Cloud Sync & Web Dashboard
Epic	Story	Tasks	Acceptance
7‑A	Backend API (FastAPI)	- Build a lightweight FastAPI service (backend/) with endpoints: POST /matches, GET /matches, GET /matches/{id}, GET /stats.
- Use SQLModel + SQLite file (or PostgreSQL in Docker) as the DB.	API returns JSON data for matches and per‑frame events.
7‑B	User Auth (JWT)	- Implement email‑based registration and login (JWT tokens).
- Add a per‑user foreign key on Match.	Users have isolated match histories.
7‑C	Client Sync	- Add a background thread in the overlay that uploads each completed match (upon graceful exit) via requests POST.
- Store a local sync‑queue in case of offline mode; retry on next start.	All matches appear on the web dashboard after upload.
7‑D	Web Dashboard (React + Vite)	- Create a simple React UI that shows a table of matches, line‑chart of score over time, and piece distribution pie chart.
- Use TailwindCSS for responsive design.	Users can view their own stats in a browser.
7‑E	Docker Compose Deploy	- Provide a docker‑compose.yml that starts the backend, a pgAdmin service, and the React frontend.
- Include an .env.example.	One‑command docker compose up -d runs the whole stack.
7‑F	Export to CSV/JSON via Web	- Add a “Download CSV” button that returns the match data in CSV.	Users can export their data from the web UI.
7‑G	Rate‑Limiting & Security	- Add slow‑down on login attempts, CORS config, use HTTPS via self‑signed cert for local dev.	Basic security controls in place.
7‑H	Documentation	- Write docs/cloud-sync.md with setup instructions (Docker, environment variables).	Docs published.
Effort: 12 d

🔌 Phase 8 – Extensibility & Plugin System
Epic	Story	Tasks	Acceptance
8‑A	Plugin Loader	- Implement a plugins package that discovers modules via entry‑points (tetris_overlay.plugin).
- Provide a sandbox (multiprocessing.Process) for each plugin to avoid crashes.	Third‑party plugins can be installed via pip and loaded automatically.
8‑B	Visual Effect Plugins	- Define an API OverlayEffect.render(surface, state) that can draw custom particles, trails, or background animations.
- Bundle a few sample plugins (e.g., “Particle Trail”, “Ghost Fade‑out”).	Users can enable/disable visual effects from Settings → “Effects”.
8‑C	Game‑Mode Plugins	- Create an interface for different Tetris variants (e.g., “Tetris 99”, “Puyo‑Puyo”).
- Provide a sample “Tetris 99” plugin that reads the board from the “next‑queue” layout.	Overlay works with at least one alternate game mode.
8‑D	Plugin Marketplace (JSON)	- Host a plugins.json file on GitHub that lists available community plugins (name, description, pip package).
- Add a “Marketplace” button in Settings that fetches this list and allows one‑click install (pip install …).	Users can install community plugins without leaving the UI.
8‑E	Plugin API Documentation	- Write docs/plugins-api.md describing required entry‑points, main classes, and examples.	Clear onboarding for third‑party developers.
8‑F	Unit Tests for Plugin Isolation	- Use pytest to spin up a dummy plugin that raises an exception; verify that the main overlay continues to run.	Plugin crashes do not bring down core.
Effort: 10 d

🔤 Phase 9 – Accessibility, Localization & UI Polish
Epic	Story	Tasks	Acceptance
9‑A	Internationalization (i18n)	- Use Qt’s QTranslator and gettext for all UI strings.
- Extract strings into .pot and provide translations for English, Spanish, French, German, Japanese, Korean, Russian, Portuguese, Chinese, Arabic, Hindi (10 languages).
- Add a “Language” dropdown in Settings → “General”.	UI updates instantly when a new language is selected.
9‑B	High‑Contrast / Color‑Blind Mode	- Add a “Theme” setting with options: default, high‑contrast, color‑blind (deuteranopia).
- Provide CSS/QSS files for each theme.	Color‑blind users can see distinct ghost colors.
9‑C	Screen‑Reader Support	- Set accessible names for all widgets (widget.setAccessibleName).
- Test with NVDA (Windows) and VoiceOver (macOS).	Screen readers announce each control correctly.
9‑D	Responsive UI	- Make the Settings dialog resizable, with layout stretch factors.
- Ensure the Dashboard charts resize smoothly.	No clipping at any window size.
9‑E	Keyboard‑Only Navigation	- Verify all controls reachable via Tab and Enter.
- Add shortcuts for common actions (Ctrl+S = Save Settings).	Fully navigable without mouse.
9‑F	Theming Engine	- Allow users to import a custom QSS theme file (drag‑and‑drop).
- Persist the chosen theme in settings.	Users can apply custom visual themes.
9‑G	Documentation Updates	- Update README with screenshots for each language.
- Add a LANGUAGES.md explaining how to add new translations.	Documentation reflects i18n support.
Effort: 8 d

🛡️ Phase 10 – Reliability, Testing & Release Automation
Epic	Story	Tasks	Acceptance
10‑A	Fuzz Testing	- Use Atheris (Python fuzzing) on all public functions: process_frames, detect_piece, OverlayRenderer.draw_ghost.
- Run fuzzing for 24 h in CI (parallel jobs).	No crashes, all exceptions caught and logged.
10‑B	Memory‑Leak Detection	- Integrate tracemalloc and objgraph into a special debug mode that snapshots memory before/after a frame.
- Add a CI job that runs the overlay for 5 min under this mode and asserts < 2 MiB growth.	Leak‑free guarantee.
10‑C	Static Analysis	- Run bandit, safety, pylint across the repo.
- Fail CI if any high‑severity issue appears.	No security warnings.
10‑D	Coverage Goal	- Enforce coverage>=90% in CI.
- Add missing tests (edge cases for ROI parsing, hot‑key conflicts).	Coverage badge shows > 90 %.
10‑E	Release Pipeline	- Use GitHub Release with automatically generated Wheel, Conda, AppImage, deb, rpm, macOS dmg, Windows exe.
- Publish to PyPI (wheel + source).
- Attach checksums (SHA‑256) for each artifact.	End‑users can install via pip install tetris-overlay or download binary.
10‑F	Upgrade Documentation Automation	- Generate API docs with pdoc and publish to GitHub Pages (/docs).
- Auto‑publish release notes from CHANGELOG.md on tag push.	Docs always up‑to‑date.
10‑G	Rollback & Hot‑Patch System	- Store previous release assets on S3 bucket.
- Provide a CLI tetris-overlay --rollback <version> that swaps the executable.	Users can roll back instantly.
10‑H	Monitoring & Telemetry	- Add Prometheus exporter exposing metrics (overlay_fps, frame_latency_seconds, error_total).
- Add a metrics.yml job in CI that scrapes the exporter during a test run.	Dashboard shows live metrics during CI test.
Effort: 12 d

🗓️ Suggested Sprint Schedule (single‑dev)
Week	Focus	Deliverables
Week 1	Phase 0 + Phase 1 (multi‑screen)	Clean repo, CI baseline, 2‑screen capture, UI for screens
Week 2	Phase 2 + Phase 3 (cross‑platform & calibration)	macOS & Linux builds, live ROI overlay, auto‑detect
Week 3	Phase 4 + Phase 5 (AI plug‑ins & training)	Agent registry, TensorRT plugin, recording & annotation UI
Week 4	Phase 6 + Phase 7 (streaming & cloud)	OBS source, Stream Deck mapping, FastAPI backend, web UI
Week 5	Phase 8 + Phase 9 (plugins & i18n)	Plugin loader, visual‑effect plugins, 5 languages, high‑contrast
Week 6	Phase 10 (reliability & release)	Fuzzing, memory‑leak tests, 90 % coverage, automated multi‑platform releases
If you have multiple developers (or several LLM bots), you can run Phase 1‑3 in parallel, Phase 4‑6 in parallel, etc., compressing the schedule to 3‑4 weeks.

🛠️ Concrete “Next‑Step” Ticket List (ready to copy‑paste into GitHub Issues)
Below are individual issue titles with enough detail to be created automatically (you can feed them to a bot that creates issues).

#	Issue Title	Short Description	Estimated
1	feat: multi‑screen capture (MultiScreenCapture)	Refactor dual capture to support arbitrary number of ROIs, add UI tab “Screens”.	2 d
2	feat: cross‑platform window filter (macOS & Wayland)	Implement window detection for macOS (Quartz) and Linux Wayland.	2 d
3	feat: live ROI calibration overlay (Qt GraphicsView)	Add draggable/resizable ROI overlay with auto‑detect button.	2 d
4	feat: AI agent plugin registry (entry‑points)	Define BaseAgent API, autodiscover agents via entry‑points.	1 d
5	feat: TensorRT agent plugin	Implement prediction_agent_tensorrt using TensorRT runtime.	2 d
6	feat: recording & annotation UI	Add “Start Recording” button, create tools/annotator.py.	2 d
7	feat: training pipeline (PyTorch Lightning)	Build dataset, train simple CNN, export TorchScript.	2 d
8	feat: OBS WebSocket source integration	Push overlay buffer to OBS via WebSocket.	1 d
9	feat: Stream Deck integration (elgato‑stream‑deck)	Map stream‑deck keys to overlay actions.	1 d
10	feat: backend API (FastAPI) for matches	CRUD endpoints, JWT auth, per‑user data.	2 d
11	feat: web dashboard (React + Vite)	List matches, show charts, export CSV.	2 d
12	feat: plugin marketplace (JSON + install UI)	Load plugins list, install via pip from UI.	2 d
13	feat: i18n – translate UI to 10 languages	Extract strings, provide .qm files, language selector.	2 d
14	feat: high‑contrast & color‑blind themes	Add QSS files, UI toggle.	1 d
15	test: fuzz all public functions with Atheris	Add fuzzing job to CI.	1 d
16	test: memory‑leak monitor (tracemalloc)	Add leak‑detect mode to overlay.	1 d
17	ci: add coverage >=90% enforcement	Modify CI to fail below threshold.	0.5 d
18	ci: build multi‑platform binaries (AppImage, dmg, exe)	Add CI jobs for each artifact.	1 d
19	doc: add “Calibration Guide” with GIFs	Write step‑by‑step guide for auto‑detect.	0.5 d
20	doc: add “Plugin Development Guide”	Explain entry‑points, API contract.	0.5 d
…	(continue as needed)		
Sum of estimates ≈ 90 person‑days.

📈 Metrics & Success Indicators
Metric	Target	How to Measure
FPS Stability	>= 28 FPS on 4‑screen capture (1080p each)	Built‑in FPS overlay + CI performance test
Coverage	>= 90 % (branch & line)	coverage xml uploaded to Codecov
Latency	≤ 30 ms per frame (including AI inference)	Timestamp diff in process_frames
Crash‑Free	< 0.1 % crash rate in CI (≥ 100 runs)	CI “stability” job that runs overlay in a headless container
User‑Facing Bugs	< 5 open issues after 1 month of release	Issue tracker monitoring
Internationalization	10 languages, >= 90 % UI strings translated	Language switch test in CI
Plugin Ecosystem	>= 3 community plugins in the marketplace (GitHub)	Marketplace JSON file count
Streaming Integration	OBS source works on Windows/macOS/Linux	Manual tester verification + video demo
Upload Success	99 % of matches uploaded to cloud backend	Backend logs + API health check
🧩 Optional “Nice‑to‑Have” Extras (Future Sprints)
Idea	Why It’s Valuable
AI‑assisted auto‑calibration – use a tiny CNN to locate the board in any screenshot.	Removes any manual ROI work.
Live‑stream analytics overlay – show live win/loss probabilities, high‑score prediction.	Gives streamers a competitive edge.
VR/AR integration – render ghost pieces directly into a VR headset via OpenXR.	Future‑proof, opens new markets.
Collaborative match replay – sync multiple players’ data to a cloud room for team analysis.	Perfect for e‑sports coaching.
Mobile client – an Android/iOS app that receives stats from the desktop overlay via WebSocket.	Extends ecosystem beyond PC.
AI‑generated commentary – feed match data into a TTS engine that announces upcoming moves.	Adds entertainment value.
📚 Next Steps for You
Pick a Phase – e.g., start with Phase 1 (multi‑screen) because it immediately expands the overlay’s utility.
Create the Issue List – copy the table of tickets into GitHub (or feed a script to auto‑create them).
Set Up CI Matrix – add macOS & Linux jobs now; they will surface missing cross‑platform bugs early.
Run the First “Sprint” – give the LLM a “sprint‑0” manifest (the issue list for Phase 1) and let it iterate.
Review & Merge – after each PR, run the full test suite, verify the UI manually, and merge.
Repeat – move on to Phase 2, then Phase 3, etc.
When you finish a full phase, you’ll have a new release artifact (e.g., tetris‑overlay‑v2.1‑win.exe, tetris‑overlay‑v2.1‑linux.AppImage, tetris‑overlay‑v2.1‑macos.dmg).

🎉 Bottom Line
You now have a concrete, 90‑day roadmap that stretches the project far beyond the original “45‑minute sprint”.
Every major functional domain (multi‑screen, cross‑platform, AI, streaming, cloud, plugins, accessibility, reliability) gets its own dedicated phase.
The plan is modular – you can work on any phase independently, or run several in parallel (especially with an LLM‑assistant).
Success criteria are explicit (FPS, coverage, crash‑free, multilingual, plugin ecosystem).
Pick the first ticket, fire up the LLM / your dev team, and let it chew through the work while you’re cooking. The result will be a professional‑grade, extensible, cloud‑enabled Tetris overlay that can be shipped to users, streamed on Twitch, or used as a research platform for AI in games.

Happy hacking! 🚀