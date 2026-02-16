# 🛠️  Incremental Fix‑Guide for **‑tetris‑overlay‑test** (No Clean Slate)
> *Adapt the LLM’s “one‑file fix” plan to work with our existing project structure.*  
> *We keep our current files, folders, and git history—only make targeted fixes where needed.*

---

## 📚  What We Already Have

- ✅ Project is already organized: `tools/`, `config/`, `scripts/`, `docs/`, `src/agents/`.
- ✅ Calibration UX is enhanced (Y/N/E/K, labels, reuse saved ROIs).
- ✅ Core capture, ROI, and overlay rendering exist.
- ✅ Multiple prediction agents are implemented (ONNX, Dellacherie, simple, mock).
- ✅ `.gitignore` already excludes planning docs and legacy.
- ✅ `run_overlay_core.py` is the main entry point (not `src/main.py`).

---

## 🎯  What We’ll Actually Do (Incremental)

1. **Make the overlay loop invoke a prediction agent and draw a ghost.**
2. **Ensure the prediction agents can be selected via config.**
3. **Add a tiny test suite that fits our current structure.**
4. **Keep CI simple and focused on our overlay, not the old orchestrator.**
5. **Update docs to reflect the real entry point and current state.**

---

## 📂  Step 0 – No Repo Reset, Just a Safety Branch (Optional)

```bash
# Optional: create a branch to experiment without touching main
git checkout -b overlay-integration
git push -u origin overlay-integration
```

---

## 🧹 Step 1 – Auto‑format the Python files (No Harm)

```bash
# Install formatter if you don’t have it
pip install black

# Format everything in-place
black .
```

- This only fixes whitespace/indentation. It won’t delete or reorganize files.

---

## 🗂️ Step 2 – Ensure the Overlay Can Import Prediction Agents

Open `run_overlay_core.py` and add a helper to load the selected agent from config.

Add this near the top (after imports):

```python
# run_overlay_core.py
import json
from pathlib import Path

def load_prediction_agent(agent_name: str):
    """Dynamically import and instantiate a prediction agent."""
    if agent_name == "dellacherie":
        from src.agents.prediction_agent_dellacherie import PredictionAgent
        return PredictionAgent()
    elif agent_name == "onnx":
        from src.agents.prediction_agent_onnx import PredictionAgent
        return PredictionAgent()
    elif agent_name == "simple":
        from src.agents.prediction_agent_simple import PredictionAgent
        return PredictionAgent()
    elif agent_name == "mock":
        from src.agents.prediction_agent_mock_perfect import PredictionAgent
        return PredictionAgent()
    else:
        raise ValueError(f"Unknown prediction_agent: {agent_name}")
```

---

## ⚙️ Step 3 – Make Configurable Prediction Agent

Create/edit `config/config.json` (add if missing):

```json
{
  "prediction_agent": "dellacherie",
  "debug_overlay": false
}
```

In `run_overlay_core.py`, load this at startup:

```python
CONFIG_PATH = Path("config/config.json")
if CONFIG_PATH.is_file():
    cfg = json.loads(CONFIG_PATH.read_text())
    prediction_agent_name = cfg.get("prediction_agent", "dellacherie")
else:
    prediction_agent_name = "dellacherie"

prediction_agent = load_prediction_agent(prediction_agent_name)
```

---

## 🎥 Step 4 – Stub Board Extraction (Minimal)

In `run_overlay_core.py`, add a tiny stub to convert a board ROI to a 20×10 binary matrix. This can be improved later.

```python
import cv2
import numpy as np

def roi_to_binary_matrix(roi_image):
    """Convert an ROI image to a 20×10 binary matrix (naive stub)."""
    gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (10, 20), interpolation=cv2.INTER_NEAREST)
    _, binary = cv2.threshold(small, 127, 255, cv2.THRESH_BINARY)
    return binary
```

---

## 👻 Step 5 – Draw the Ghost Piece (Overlay Renderer Update)

Open `overlay_renderer.py` and add a method to draw a ghost at a given column/rotation. Keep it simple for now.

```python
def draw_ghost(self, surface, column, rotation, piece_type="T"):
    """Draw a semi-transparent ghost piece at the given column/rotation."""
    # Simple placeholder: draw a rectangle at column*cell_width
    cell_w = 30
    cell_h = 30
    x = column * cell_w
    y = 0
    color = (255, 255, 255, 128)  # semi-transparent white
    pygame.draw.rect(surface, color, (x, y, cell_w*4, cell_h*4), 2)
```

Then in the main loop of `run_overlay_core.py`, after you get a prediction:

```python
pred = prediction_agent.handle({"board": board_matrix, "piece": "T", "orientation": 0})
overlay.draw_ghost(screen, pred["target_col"], pred["target_rot"])
```

---

## 🧩 Step 6 – Wire It All Together in the Main Loop

In `run_overlay_core.py`, inside the `process_frames()` function, add:

```python
# Grab left board ROI (replace with your actual ROI capture)
left_board_img = capture_roi("left_board")
board_matrix = roi_to_binary_matrix(left_board_img)

# Predict
pred = prediction_agent.handle({"board": board_matrix, "piece": "T", "orientation": 0})

# Draw ghost
overlay.draw_ghost(screen, pred["target_col"], pred["target_rot"])
```

---

## ✅ Step 7 – Add a Tiny Test Suite (Our Structure)

Create `tests/test_overlay_integration.py`:

```python
def test_load_prediction_agent():
    from run_overlay_core import load_prediction_agent
    agent = load_prediction_agent("mock")
    assert agent is not None

def test_roi_to_binary_matrix():
    import numpy as np
    from run_overlay_core import roi_to_binary_matrix
    dummy = np.zeros((100, 200, 3), dtype=np.uint8)
    mat = roi_to_binary_matrix(dummy)
    assert mat.shape == (20, 10)
```

Run with:

```bash
pytest tests/test_overlay_integration.py -q
```

---

## 🚦 Step 8 – Keep CI Simple (Overlay‑Focused)

Edit `.github/workflows/ci_python.yml` (or create) to:

```yaml
name: Overlay CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest
      - name: Test overlay imports
        run: python -c "import run_overlay_core; import overlay_renderer"
      - name: Run tiny tests
        run: pytest -q
```

---

## 📄 Step 9 – Update Docs to Match Reality

Open `docs/README.md` and ensure the quick start uses `run_overlay_core.py`:

```markdown
## Quick start
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python run_overlay_core.py
# Press Ctrl+Alt+C to calibrate, then play Tetris
```
```

Add a note about `config/config.json` to choose the prediction agent.

---

## 📦 Step 10 – Run a Quick Smoke Test

```bash
python run_overlay_core.py
# Press Ctrl+Alt+C to calibrate
# Play a few frames; you should see a ghost rectangle
```

If you see a ghost overlay, the integration works. You can later improve piece detection and ghost drawing.

---

## 📋 Incremental Checklist (Copy‑Paste)

```bash
# 0️⃣ Optional safety branch
git checkout -b overlay-integration

# 1️⃣ Format code
black .

# 2️⃣ Add prediction_agent loader to run_overlay_core.py
# 3️⃣ Ensure config/config.json exists with prediction_agent field
# 4️⃣ Add roi_to_binary_matrix stub
# 5️⃣ Add draw_ghost to overlay_renderer.py
# 6️⃣ Wire prediction + ghost into process_frames()
# 7️⃣ Add tests/test_overlay_integration.py
# 8️⃣ Update CI to test overlay imports
# 9️⃣ Update docs/README.md quick start
# 10️⃣ Run smoke test
python run_overlay_core.py

# Commit when satisfied
git add .
git commit -m "Integrate prediction agent into overlay loop; draw ghost piece"
git push origin overlay-integration
```

---

## ❓ Optional Choices (You Decide)

- **Keep or remove C++ bridge?** Keep it; it’s ignored by our Python overlay.
- **DXGI capture?** Keep the fallback; you already have OpenCV capture.
- **Demo duration?** Keep it manual; no need for a timed orchestrator.

---

## 🎉 What You Get Now

- No repo reset, no file moves.
- The overlay now predicts and draws a ghost piece.
- Configurable prediction agent via `config/config.json`.
- Tiny test suite and CI that matches our real entry point.
- Docs that reflect the actual workflow.

You can continue improving piece detection, ghost rendering, and UI without reorganizing everything again. Enjoy the overlay!
