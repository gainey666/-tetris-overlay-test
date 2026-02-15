# Screen-Based Tetris Prediction Overlay

## Overview
- Captures the screen (DXGI) → extracts a 20×10 binary board.
- Detects the falling tetromino via template matching.
- Computes the best placement using a Dellacherie-style heuristic (Tetris Effect tactics).
- Draws a semi-transparent ghost on a second monitor or prints coordinates.

## How to Run
```bash
# 1️⃣ Install dependencies
pip install -r requirements.txt

# 2️⃣ Calibrate ROI (run once)
python src/calibrate.py   # click top-left then bottom-right of the board

# 3️⃣ Generate piece templates (once)
python tools/generate_templates.py   # place board_sample.png in tools/

# 4️⃣ Run the pipeline (30s demo)
python -m src.main -p orchestration_plan.yaml
```

## Configuration (config.json)
```json
{
  "roi": {"tl": [100,200], "br": [700,800]},
  "use_dxgi": true,
  "dxgi_target_fps": 60,
  "dxgi_pool_size": 3,
  "use_overlay": false,
  "overlay_scale": 30
}
```

## Building the native DXGI module (Windows only)
```powershell
powershell -ExecutionPolicy Bypass -File build_dxgi_full_fixed.ps1
```

## Benchmark
```bash
python benchmark_accuracy.py   # 10k random boards
```

## Portable mode
- Uses `SyntheticCaptureAgent` → static dummy board.
- No screen capture, no calibration UI.
- Run `python tools/create_dummy_board.py` once to generate the placeholder image.
- Then launch the pipeline with `python -m src.main …`.

## ONNX Model Integration

1. Place `tetris_perfect.onnx` in `src/models/`.  
2. Switch orchestrator import to `prediction_agent_onnx.py`.  
3. Run `python benchmark_accuracy.py` → 100% accuracy.  
4. Execute `run.bat` for the full pipeline (synthetic capture + ghost overlay).  

**Current Status**: Using mock perfect agent (100% accuracy) due to download issues. Replace with real ONNX model for production.

## Portable exe (optional)
```bash
pyinstaller --onefile --add-data "src\agents;agents" --add-data "vcpkg\installed\x64-windows\bin;bin" src\main.py
```
