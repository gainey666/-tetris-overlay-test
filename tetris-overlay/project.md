# Project: Screen‑Based Tetris Prediction Overlay

## Vision
Create a *local* assistant that watches a Tetris‑style game on the screen, builds an internal board model, computes the highest‑scoring placement for the falling piece, and draws a semi‑transparent "ghost" suggestion on a second monitor (or over the game window).  
No memory hacking – everything is derived from visual data.

## Success Criteria
| # | Metric | Target |
|---|--------|--------|
| 1 | **Latency** (capture → ghost) | ≤ 30 ms (≈ 33 fps) |
| 2 | **Prediction Accuracy** vs. perfect AI | ≥ 95 % same move on a test set of 10 000 random boards |
| 3 | **Robustness** (different themes, window sizes) | Works after a single ROI calibration |
| 4 | **Usability** – one‑click start/stop and a clear overlay | ✅ |

## Deliverables
1. **Calibration utility** (`src/calibrate.py`) – user clicks TL/BR of the board once.  
2. **Screen‑capture agent** (Python + `mss`).  
3. **Board‑extraction agent** (OpenCV threshold → 20×10 binary matrix).  
4. **Piece‑detector agent** (template‑matching *or* tiny CNN).  
5. **Prediction service** – either:  
   * Hand‑crafted weighted‑sum heuristic (`tetris_bot.best_move`) **or**  
   * Pre‑trained ONNX CNN (pixel → action).  
6. **Overlay renderer** (Pygame transparent window, click‑through).  
7. **Orchestration script** (`src/main.py`) that wires the agents together.  

## Milestones
| Milestone | Tasks | Due |
|-----------|-------|-----|
| M0 – Repo scaffolding | Create folder structure, `requirements.txt`, sample README | Day 1 |
| M1 – Calibration & capture | `calibrate.py`, `capture_and_process.py` (capture + board extraction) | Day 2 |
| M2 – Piece detection | Template matcher + unit tests | Day 3 |
| M3 – Prediction engine | Integrate `tetris_bot` + socket server (or ONNX CNN) | Day 4 |
| M4 – Overlay | Transparent Pygame window, ghost drawing | Day 5 |
| M5 – Integration & testing | Full pipeline, latency profiling, accuracy benchmark | Day 6 |
| M6 – Documentation | `project.md`, `system.md`, agent specs, user guide | Day 7 |

## Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| Capture too slow on high‑DPI monitors | > 30 ms | Switch to DXGI Desktop Duplication (C++) if needed |
| Piece detection fails on anti‑aliased graphics | Wrong predictions | Use a tiny CNN trained on synthetic data (optional) |
| Full‑screen exclusive mode blocks overlay | No overlay visible | Require the game to be windowed or border‑less |
| False positives in board mask (lighting) | Extra holes → bad score | Morphological closing (`cv2.morphologyEx`) and adaptive HSV thresholds |
