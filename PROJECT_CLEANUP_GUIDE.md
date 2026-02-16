# Project Cleanup Guide – Human‑readable file map

## Core overlay runtime (keep in git)
- `run_overlay_core.py` – Main entry point; starts capture, hotkeys, overlay loop.
- `roi_calibrator.py` – Interactive ROI calibration with Y/N/E/K flow and labeled overlays.
- `capture.py` – Low‑level screen capture wrapper.
- `dual_capture.py` – Captures two monitors (left/right boards).
- `dual_roi_manager.py` – Manages dual‑board ROI pairing.
- `shared_ui_capture.py` – Captures shared UI (score/wins/timer) once per frame.
- `next_queue_capture.py` – Captures the 4‑slot next‑piece queue.
- `roi_capture.py` – Generic ROI loader/capture utilities.
- `overlay_renderer.py` – Pygame overlay drawing.
- `ocr_utils.py` – OCR helpers for extracting numbers from UI images.
- `logger_config.py` – Sets up JSON telemetry logger.
- `run_all_tests.py` – Thin wrapper that runs pytest quietly.
- `conftest.py` – Ensures test artifacts exist in UTF‑8.

## Configuration (keep in git)
- `roi_config.json` – Saved ROI rectangles for calibration.
- `config.json` – General overlay configuration.
- `requirements.txt` – Python dependencies for the overlay.
- `requirements_qa.txt` – Extra test/CI dependencies.
- `pyproject.toml` – Minimal pytest config.
- `.gitignore` – Keeps .venv, artifacts, logs, screenshots, personia out of git.

## Tests (keep in git)
- `tests/test_shared_ui.py` – Validates ROI helpers and queue slots.
- `tests/test_telemetry_logging.py` – Validates telemetry JSON output.
- `tests/test_orchestrator.py` – Skipped test for legacy orchestrator (can be removed).

## Documentation (keep in git)
- `README.md` – Project overview and quick start.
- `LLM_QUICK_START.md` – Resume‑day‑6 workflow for agents/humans.
- `DAY6_CHANGES.md` – Day‑6 change log.
- `PRODUCTION.md` – Production deployment notes.

## Legacy/unused (can be removed from git)
- `src/orchestrator/` – Plan‑driven scheduler; not used by live overlay.
- `orchestration_plan.yaml` – Plan file for the above orchestrator.
- `personia/` – Multi‑agent persona demo; unrelated to overlay.
- `server.md` – Persona orchestrator rules; unused.
- `src/agents/` (except capture_agent shim) – Many agents only used by orchestrator.
- `agents.md` – Agent list for orchestrator.
- `calibration_ui.py` – Old UI; replaced by roi_calibrator.py.
- `advanced_calibration.py` – Experimental; not used.
- `integrate_agents.py` – Orchestrator integration script.
- `tetris_overlay_core.py` – Alternate core; not the active entry point.
- `run_qa_cli.py` – QA helper script; optional.
- `llm_qa_agent/` – QA agent scaffolding; optional.
- `llm promtp.md` – Prompt drafts; optional.
- `CI_*.md`, `CURSOR_AI_PLANNING.md`, `FUTURE_ROADMAP.md`, `PROJECT_*.md`, `VALIDATION_SUMMARY.md`, `VERIFICATION.md` – Planning/status docs; optional.
- `*.ps1` build/install scripts – Keep only if you still use them.
- `*.bat`, `cleanup.bat` – Optional cleanup scripts.
- `*.png` screenshots – Test captures; optional.
- `test_*.py` standalone scripts – Optional manual test helpers.
- `benchmark*.py/json`, `cnn_latency.json` – Benchmark artifacts; optional.
- `models/`, `tetris_cnn.onnx` – Model files; keep only if you use the CNN.
- `cpp_binding/` – C++ bindings; optional.
- `False/`, `base image/`, `tetris_overlay/`, `tetris_artifacts.zip` – Experimental bundles; optional.
- `index.html`, `script.js`, `style.css` – Web demo; optional.
- `window_manager.py`, `create_window_filter.py`, `debug_*.py` – Debug utilities; optional.
- `singleton_lock.py` – Process lock; optional.
- `safe_create.py` – Helper; optional.
- `make_progress_log.py`, `progress_log.json` – Progress tracking; optional.
- `infofile.md`, `project*.md`, `system*.md` – Additional docs; optional.
- `RESPONSE_FOOTER.txt` – Template snippet; optional.

## Generated/temporary (already ignored)
- `.venv/`, `__pycache__/`, `.pytest_cache/`, `artifacts/`, `telemetry.log`, `*.log`, `Capture*.PNG`, `game_screenshots/`, `*.swp`.

## Proposed shrink actions
1. **Delete or move to a legacy folder:** `src/orchestrator/`, `orchestration_plan.yaml`, `personia/`, `server.md`, `agents.md`, most of `src/agents/` except the capture shim.
2. **Archive optional docs:** Move planning/status markdowns to a `docs/legacy/` folder or delete them.
3. **Archive optional scripts:** Keep only the scripts you actively use; move others to `tools/optional/`.
4. **Archive test utilities:** Keep `tests/` for pytest; move standalone `test_*.py` scripts to `tools/manual/`.
5. **Archive model/benchmark files:** If you don’t use the CNN or benchmarks, move them to `assets/optional/`.
6. **Commit the cleanup** after confirming the overlay still runs with `python run_overlay_core.py` and calibration works.

Result: a lean repo containing only the runtime, configuration, tests, and essential docs—easier to navigate and safer to share.
