# Tetris Overlay – Real‑time Prediction and Ghost Display

A lightweight Python overlay that watches a Tetris game, extracts the board state, predicts the best placement, and draws a semi‑transparent “ghost” piece on screen.

## What it does
- **Capture** grabs the game window (dual‑monitor support).
- **Calibration** lets you draw ROIs for boards, hold pieces, next queue, and shared UI.
- **Extraction** converts ROIs to a 20×10 binary board and identifies the current piece.
- **Prediction** runs one of several agents:
  - Dellacherie heuristic (fast, tunable weights)
  - ONNX neural network (`tetris_perfect.onnx`)
  - Simple left‑most placement
  - Mock perfect (for testing)
- **Overlay** draws a ghost piece at the predicted column/rotation, click‑through and always‑on‑top.

## Quick start
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_overlay_core.py
# Press Ctrl+Alt+C to calibrate, then play Tetris
```

## Project layout
- `run_overlay_core.py` – Main entry point; hotkeys, capture loop.
- `roi_calibrator.py` – Interactive ROI calibration with Y/N/E/K flow.
- `capture.py`, `dual_capture.py` – Screen capture utilities.
- `roi_capture.py`, `shared_ui_capture.py`, `next_queue_capture.py` – ROI helpers.
- `overlay_renderer.py` – Pygame overlay window.
- `src/agents/` – Prediction agents (dellacherie, onnx, simple, mock).
- `config/` – ROI and general configuration.
- `tests/` – Pytest suite.
- `tools/` – Helper utilities (calibration UI, window filter, etc.).
- `docs/` – Documentation.

## Configuration
Edit `config/config.json` to choose the prediction agent:
```json
{
  "prediction_agent": "dellacherie",
  "debug_overlay": false
}
```

## Calibration
1. Run the overlay.
2. Press **Ctrl+Alt+C** to start calibration.
3. Follow prompts to draw ROIs:
   - Player boards (left/right)
   - Hold pieces
   - Next queue (up to 4 slots)
   - Shared UI (score, wins, timer)
4. ROIs are saved to `config/roi_config.json`.

## Testing
```bash
pytest tests/test_shared_ui.py -q
```

## Development notes
- Target latency: ≤ 30 ms from capture to ghost.
- Works after a single ROI calibration.
- Supports both heuristic and ONNX prediction models.
- Legacy/orchestrator code is archived in `legacy/` and ignored.

## License / Contributing
Treat this as a personal project. Feel free to experiment with new prediction agents or UI improvements.
