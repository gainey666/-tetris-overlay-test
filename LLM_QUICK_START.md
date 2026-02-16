# LLM Quick Start – Resume Overlay Development

This guide lets any local AI agent (or human) reboot the Day 6 workflow in minutes.

## 1. Prep the environment
- `py -3.11 -m venv .venv` (first time) then `.cvenv\Scripts\activate`.
- `pip install -r requirements.txt`
- Optional: `pip install -r requirements_qa.txt` if you need QA helpers (`pytest`, etc.).

## 2. Calibrate the 17 ROIs + queue slots
1. Run `python run_overlay_core.py` (spawns overlay and hotkeys).
2. Press **Ctrl+Alt+C** → `roi_calibrator.start_calibrator()`.
3. Follow console prompts to draw, in order:
   - 14 competitive play ROIs (boards, hold, previews, garbage, zone, scores, names).
   - 3 shared UI ROIs: score, wins, timer (single source for both players).
   - Up to 4 **next_queue** slots (number prompted; draw top→bottom).
4. When finished the tool writes both `config.json` (dual boards) and `roi_config.json` (full list).

## 3. Capture pipeline check
```powershell
python - <<'PY'
from roi_capture import capture_all
print(sorted(capture_all().keys()))
PY
```
- Should list every scalar ROI (queue handled separately).
- Next queue helper: `python - <<'PY'
from next_queue_capture import capture_next_queue
print(len(capture_next_queue()))
PY`

## 4. Overlay processing loop
- `run_overlay_core.py` already:
  - Hooks Ctrl+Alt+C, starts `OverlayRenderer`, and drives `DualScreenCapture`.
  - Calls `capture_shared_ui()` + `capture_next_queue()` each frame for downstream models/OCR.
- Extend `process_frames()` or downstream agents to feed:
  - `shared["score"|"wins"|"timer"]` into `ocr_utils.extract_number`.
  - `queue_images` into the piece classifier (length 1‑4).

## 5. Testing checklist
1. `pytest tests/test_shared_ui.py` *(create if missing)* to assert ROI helpers return valid images.
2. Manual sanity: `python - <<'PY'` snippet above and inspect `.save("/tmp/roi.png")` outputs if needed.
3. Run end‑to‑end overlay for 2+ minutes; watch logs for `Dual board processing successful`.

## 6. Deployment notes
- Config + ROI files live at repo root; bundle them with releases.
- When shipping, add instructions for pressing Ctrl+Alt+C post‑install so users recalibrate quickly.
- Log captured numbers via the new logging persona (`personia/agent_logger.md`) if you script an automation agent.

Happy Day‑6 hacking! Keep `DAY6_CHANGES.md` updated with what/why/how for each commit. 🚀
