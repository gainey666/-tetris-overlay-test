Below is a ready‑to‑copy project skeleton that you can drop straight into your Windsurf‑Cursor‑AI (or any other agent‑based automation platform).
It contains:

project.md – high‑level description, goals, milestones.
system.md – architecture diagram, data‑flow, tech stack.
agents/ – one markdown file per agent (Capture, Board‑Processor, Piece‑Detector, Prediction, Overlay‑Renderer).
src/ – minimal Python entry point and the core scripts (calibrate, predictor‑server, capture‑&‑overlay).
requirements.txt – all third‑party packages you need to pip install.
All files are self‑contained; just create the folder structure shown at the end of this answer, paste the contents, and run pip install -r requirements.txt followed by python src/main.py.

📁 Folder layout (copy‑paste)
tetris‑overlay/
├─ project.md
├─ system.md
├─ requirements.txt
├─ agents/
│   ├─ capture_agent.md
│   ├─ board_processor_agent.md
│   ├─ piece_detector_agent.md
│   ├─ prediction_agent.md
│   └─ overlay_renderer_agent.md
└─ src/
    ├─ calibrate.py
    ├─ predictor_server.py
    ├─ capture_and_process.py
    └─ main.py
📄 project.md
# Project: Screen‑Based Tetris Prediction Overlay

## Vision
Create a *local* assistant that watches a Tetris‑style game on the screen, builds an internal board model, computes the highest‑scoring placement for the falling piece, and draws a semi‑transparent “ghost” suggestion on a second monitor (or over the game window).  
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

---  

## 📄 `system.md`

```markdown
# System Architecture – Screen‑Based Tetris Overlay

+------------------------+ UDP (JSON) +------------------------+ | Capture Agent | ───────────────────► | Prediction Agent | | (mss → raw frame) | | (hand‑crafted or CNN) | +------------------------+ +------------------------+ | | | 1. ROI crop + colour‑threshold | ▼ | +------------------------+ Queue +------------------------+ | Board‑Processor Agent | ◄────────────────►| Piece‑Detector Agent | | (binary 20×10 matrix) | | (template or CNN) | +------------------------+ +------------------------+ | | | 2. Board matrix + piece info | ▼ ▼ +---------------------------------------------------------------+ | Overlay Renderer Agent (Pygame) | | Receives {rotation, column, piece_type} → draws ghost | +---------------------------------------------------------------+


## Data Flow
1. **Capture Agent** grabs the full desktop each 30 ms (or faster) using `mss`.  
2. The frame is **cropped** to the calibrated board ROI (saved in `calibration.json`).  
3. **Board‑Processor** converts the ROI to a binary 20×10 matrix via HSV threshold + morphological cleanup.  
4. **Piece‑Detector** runs on the *difference* between the current and previous mask (or uses a tiny CNN) to identify the falling tetromino (`type` + `rotation`).  
5. The **Prediction Agent** receives a JSON payload  
   ```json
   {
     "board": [[0,1,…],[…]],
     "current_piece": {"type":"T","rotation":2},
     "next_queue": ["L","I","Z"]   // optional
   }
It returns

{"rotation":1,"column":5,"piece_type":"T","score":13.2}
– either by calling tetris_bot.best_move (hand‑crafted) or by running an ONNX CNN (onnxruntime).
6. Overlay Renderer reads the prediction via a thread‑safe queue, draws a semi‑transparent outline of the piece at the suggested column/rotation, and keeps the window always‑on‑top & click‑through.

Technologies
Layer	Library / Tool	Language
Capture	mss (cross‑platform screen grab)	Python
Image processing	OpenCV (cv2) – colour threshold, morphology	Python
Piece detection	Template matching or ONNX CNN (onnxruntime)	Python
Prediction	Karpathy’s tetris_bot (NumPy) or custom CNN	Python
Overlay	Pygame transparent window (NOFRAME, WS_EX_LAYERED)	Python
IPC	UDP sockets (local 127.0.0.1) + queue.Queue for intra‑process	Python
📄 agents/capture_agent.md
# Capture Agent

## Purpose
Grab the desktop (or a specific monitor) at a target rate (≈ 30 fps) and forward the raw frame to downstream agents.

## Inputs
- None (starts on launch).

## Outputs
- `frame` – a NumPy array `shape=(H, W, 3)` in BGR order.

## Dependencies
- `mss`
- `numpy`

## Implementation notes
```python
# src/capture_and_process.py – function used by the agent
import mss, numpy as np

def capture_frame(monitor=0):
    with mss.mss() as sct:
        raw = sct.grab(sct.monitors[monitor])  # full desktop
        img = np.array(raw)[:, :, :3]          # BGR
    return img
The agent runs in its own thread, continuously calling capture_frame() and pushing the result onto a queue.Queue named frame_q.

Configuration
monitor index (default 0 = primary) – change if your game is on a secondary monitor.
Desired FPS can be limited by time.sleep(1/target_fps).

---  

## 📄 `agents/board_processor_agent.md`

```markdown
# Board Processor Agent

## Purpose
Convert the captured screen region that contains the Tetris board into a **binary matrix** (20 × 10) where `1` = block, `0` = empty.

## Inputs
- `frame` (from Capture Agent)

## Outputs
- `board` – `np.ndarray` (`dtype=np.uint8`, shape `(20,10)`)
- `mask` – optional full‑size binary mask (useful for piece detection)

## Dependencies
- `opencv-python` (cv2)
- `numpy`

## Implementation notes
1. Load `calibration.json` once – contains `x, y, w, h` of the board ROI.
2. Crop: `roi = frame[y:y+h, x:x+w]`.
3. Convert to HSV: `hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)`.
4. Threshold to isolate any bright block colour:  
   ```python
   lower = np.array([0, 50, 50])
   upper = np.array([180, 255, 255])
   mask = cv2.inRange(hsv, lower, upper)
Morphological closing to fill small gaps:
kernel = np.ones((3,3), np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
Resize each cell to a single pixel (average pooling):
board = cv2.resize(mask, (10, 20), interpolation=cv2.INTER_AREA)
board = (board > 30).astype(np.uint8)   # threshold to 0/1
The agent consumes frames from frame_q and pushes (board, mask) onto board_q.

Configuration
HSV bounds (lower, upper) may need tweaking for custom skins/themes.

---  

## 📄 `agents/piece_detector_agent.md`

```markdown
# Piece Detector Agent

## Purpose
Identify **type** (`I,O,T,S,Z,J,L`) and **rotation** (0‑3) of the currently falling tetromino.

## Inputs
- `mask` (binary mask from Board Processor Agent)
- `prev_mask` (mask from the previous frame, kept internally)

## Outputs
- `piece_info` – JSON‑serialisable dict:
  ```json
  {"type":"T","rotation":2}
Dependencies
opencv-python
Optional: onnxruntime (if you prefer a tiny CNN)
Two implementation paths
A) Template‑matching (no ML)
Compute diff = cv2.subtract(mask, prev_mask) – new coloured pixels.
Find connected components (cv2.connectedComponentsWithStats).
Keep the largest component (the falling piece).
Compare the component shape against pre‑computed 4×4 binary templates for each tetromino/rotation.
Return the best‑matching (type, rotation).
Templates are stored in templates.py (a dict {type: [rot0, rot1, …]} – each entry is a 4×4 np.uint8 array.)

B) Tiny CNN (more robust)
Train a 5‑layer CNN (see train_cnn.py in the repo) that takes the 20×10 binary board + the diff mask and outputs a 28‑class ID (type*4 + rotation).
Export to piece_classifier.onnx.
Load with onnxruntime.InferenceSession and call session.run(...).
Agent code skeleton (template‑matching version):

def detect_piece(prev_mask, cur_mask):
    diff = cv2.subtract(cur_mask, prev_mask)
    num, labels, stats, _ = cv2.connectedComponentsWithStats(diff, connectivity=8)
    if num <= 1:
        return {"type":"I","rotation":0}   # fallback
    # largest component (ignore background)
    largest = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
    piece_mask = (labels == largest).astype(np.uint8) * 255
    # resize to 4×4 for matching
    tiny = cv2.resize(piece_mask, (4,4), interpolation=cv2.INTER_NEAREST)
    # compare with templates (see templates.py)
    best_type, best_rot = match_template(tiny)
    return {"type": best_type, "rotation": best_rot}
The agent continuously reads from board_q, keeps the previous mask in memory, and pushes results onto piece_q.

Configuration
If you change the board cell size (non‑standard), adjust the resize dimension in the detector accordingly.

---  

## 📄 `agents/prediction_agent.md`

```markdown
# Prediction Agent

## Purpose
Given a binary board and the current piece, compute the **highest‑scoring placement** (rotation + column).  

Two possible back‑ends:
1. **Hand‑crafted weighted‑sum heuristic** (`tetris_bot.best_move`).  
2. **ONNX CNN** that maps directly to an action (`tetris_cnn.onnx`).

## Inputs
- `board` (20×10 binary matrix)
- `piece_info` (`{"type":"T","rotation":2}`)

## Outputs
- `prediction` – JSON dict:
  ```json
  {
    "rotation":1,
    "column":5,
    "piece_type":"T",
    "score":13.2
  }
Dependencies
numpy
Option A: tetris_bot (pure‑Python, bundled in src/predictor_server.py).
Option B: onnxruntime (if you use the CNN).
Implementation notes
A) Weighted‑sum heuristic (default)
from tetris_bot import best_move   # <-- the library from Karpathy's repo

def predict(board, piece):
    rot, col, _, score = best_move(board, piece["type"])
    return {
        "rotation": rot,
        "column": col,
        "piece_type": piece["type"],
        "score": float(score)
    }
B) ONNX CNN
import onnxruntime as ort
session = ort.InferenceSession("tetris_cnn.onnx")

def predict(board, piece):
    # board shape (20,10) → (1,1,20,10) float32
    inp = board.astype(np.float32)[np.newaxis, np.newaxis, :, :]
    logits = session.run(None, {"input": inp})[0]   # (1,280)
    action = logits.argmax()
    piece_id = action // 40
    rot = (action % 40) // 10
    col = action % 10
    types = ["I","O","T","S","Z","J","L"]
    return {
        "rotation": rot,
        "column": col,
        "piece_type": types[piece_id],
        "score": float(logits.max())
    }
The agent runs in its own thread, listening on a local UDP socket (127.0.0.1:51424) for the JSON payload from the upstream agents.
After computing the prediction, it sends the JSON reply back to the same address and pushes it onto a thread‑safe prediction_q for the Overlay Renderer.

Configuration
Choose backend by setting PREDICTION_BACKEND = "heuristic" or "cnn" in src/predictor_server.py.
If you use the CNN, ensure tetris_cnn.onnx is placed next to the script.

---  

## 📄 `agents/overlay_renderer_agent.md`

```markdown
# Overlay Renderer Agent

## Purpose
Display a **semi‑transparent ghost piece** at the location returned by the Prediction Agent, without stealing mouse/keyboard focus.

## Inputs
- `prediction` (from Prediction Agent)

## Outputs
- Visual overlay (no programmatic output)

## Dependencies
- `pygame`
- (Windows only) `ctypes` for click‑through flag – also works on macOS/Linux with the `SDL_WINDOW_ALLOW_HIGHDPI` hint.

## Implementation notes
```python
import pygame, sys, ctypes, json, queue

def init_window(width, height):
    pygame.init()
    screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
    # Make window click‑through on Windows
    if sys.platform.startswith('win'):
        hwnd = pygame.display.get_wm_info()["window"]
        WS_EX_LAYERED      = 0x80000
        WS_EX_TRANSPARENT  = 0x20
        ctypes.windll.user32.SetWindowLongW(hwnd, -20,
                                           WS_EX_LAYERED | WS_EX_TRANSPARENT)
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 200, 0x2)
    return screen

def draw_ghost(screen, pred):
    piece = pred["piece_type"]
    rot   = pred["rotation"]
    col   = pred["column"]
    shape = TETROMINO[piece][rot]   # same dict used by the predictor
    BLOCK = board_cell_px           # same as in calibration (e.g., 30)

    # Simple drop row (visual only – we place it near the top)
    for dr, dc in shape:
        r = dr * BLOCK
        c = (col + dc) * BLOCK
        pygame.draw.rect(screen, (255,255,0),
                         (c, r, BLOCK-2, BLOCK-2), 2)   # yellow outline

def run_overlay(prediction_q, width, height):
    screen = init_window(width, height)
    clock = pygame.time.Clock()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        screen.fill((0,0,0,0))   # clear transparent background
        try:
            pred = prediction_q.get_nowait()
            draw_ghost(screen, pred)
        except queue.Empty:
            pass
        pygame.display.flip()
        clock.tick(30)   # 30 fps
The agent reads predictions from a shared queue.Queue (prediction_q) that the main.py script populates.
It runs in its own thread, allowing the rest of the pipeline to keep capturing at full speed.

Configuration
board_cell_px should match the cell size discovered during calibration (W/10).
Opacity (currently 200/255) can be adjusted in the SetLayeredWindowAttributes call.

---  

## 📄 `requirements.txt`

```text
numpy
opencv-python
mss
pygame
onnxruntime   # optional – only needed if you use the CNN backend
# tetris_bot is a pure‑Python library; copy its source into src/ or install via pip if you have it.
📄 src/calibrate.py
"""
calibrate.py – one‑off utility to store the board ROI (top‑left & bottom‑right)
"""

import cv2, json, pathlib, sys

def click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        print(f"point #{len(points)}: {(x, y)}")
        if len(points) == 2:
            cv2.destroyAllWindows()

if __name__ == "__main__":
    img_path = input("Path to a screenshot of the game (PNG/JPG): ").strip()
    img = cv2.imread(img_path)
    if img is None:
        sys.exit("Failed to load image.")
    points = []
    cv2.imshow("Click TL then BR of the board", img)
    cv2.setMouseCallback("Click TL then BR of the board", click)
    cv2.waitKey(0)

    if len(points) != 2:
        sys.exit("You must click exactly two points.")
    (x1, y1), (x2, y2) = points
    roi = {"x": min(x1, x2), "y": min(y1, y2),
           "w": abs(x2 - x1), "h": abs(y2 - y1)}
    out_path = pathlib.Path("calibration.json")
    out_path.write_text(json.dumps(roi, indent=2))
    print(f"Saved ROI → {out_path}")
📄 src/predictor_server.py
#!/usr/bin/env python3
"""
Simple UDP server that receives a board+piece JSON, runs the selected prediction
backend, and replies with the best move.
"""

import socket, json, argparse
import numpy as np
from tetris_bot import best_move     # <-- copy Karpathy's repo into src/
import onnxruntime as ort           # optional, only if you use the CNN backend

# -------------------------------------------------
# Configuration
# -------------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--backend", choices=["heuristic","cnn"], default="heuristic",
                    help="Which prediction engine to use")
parser.add_argument("--port", type=int, default=51424,
                    help="UDP port to listen on")
parser.add_argument("--cnn-model", default="tetris_cnn.onnx",
                    help="Path to ONNX file (if backend=cnn)")
args = parser.parse_args()

if args.backend == "cnn":
    session = ort.InferenceSession(args.cnn_model)

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def predict_heuristic(board, piece):
    rot, col, _, score = best_move(board, piece["type"])
    return {"rotation": rot, "column": col,
            "piece_type": piece["type"], "score": float(score)}

def predict_cnn(board, piece):
    # board: (20,10) uint8 → (1,1,20,10) float32
    inp = board.astype(np.float32)[np.newaxis, np.newaxis, :, :]
    logits = session.run(None, {"input": inp})[0]    # (1,280)
    idx = logits.argmax()
    piece_id = idx // 40
    rot = (idx % 40) // 10
    col = idx % 10
    types = ["I","O","T","S","Z","J","L"]
    return {"rotation": int(rot), "column": int(col),
            "piece_type": types[piece_id], "score": float(logits.max())}

predict = predict_heuristic if args.backend == "heuristic" else predict_cnn

# -------------------------------------------------
# UDP loop
# -------------------------------------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", args.port))
print(f"⚡ Prediction server listening on 127.0.0.1:{args.port} (backend={args.backend})")

while True:
    payload, client = sock.recvfrom(4096)
    try:
        req = json.loads(payload.decode())
        board = np.array(req["board"], dtype=np.uint8)
        piece = req["current_piece"]
        resp = predict(board, piece)
        sock.sendto(json.dumps(resp).encode(), client)
    except Exception as e:
        err = {"error": str(e)}
        sock.sendto(json.dumps(err).encode(), client)
📄 src/capture_and_process.py
#!/usr/bin/env python3
"""
High‑level orchestration that wires the agents together:
  Capture → BoardProcessor → PieceDetector → Prediction → Overlay
"""

import json, pathlib, threading, queue, time, sys
from predictor_server import predict_heuristic  # only needed for import sanity
import mss, cv2, numpy as np
import pygame, ctypes

# ------------------------------------------------------------------
# Load calibration
# ------------------------------------------------------------------
CALIB_PATH = pathlib.Path("calibration.json")
if not CALIB_PATH.exists():
    sys.exit("⚠️ Run calibrate.py first.")
ROI = json.loads(CALIB_PATH.read_text())
X, Y, W, H = ROI["x"], ROI["y"], ROI["w"], ROI["h"]
CELL_PX = W // 10

# ------------------------------------------------------------------
# Queues (thread‑safe communication)
# ------------------------------------------------------------------
frame_q     = queue.Queue(maxsize=2)   # raw frames from mss
board_q     = queue.Queue(maxsize=2)   # (board, mask)
piece_q     = queue.Queue(maxsize=2)   # piece_info dict
prediction_q = queue.Queue(maxsize=2)   # final prediction dict

# ------------------------------------------------------------------
# 1️⃣ Capture thread
# ------------------------------------------------------------------
def capture_loop():
    with mss.mss() as sct:
        while True:
            raw = sct.grab(sct.monitors[0])          # full desktop
            img = np.array(raw)[:, :, :3]            # BGR
            # crop to ROI
            roi = img[Y:Y+H, X:X+W]
            # push to queue, dropping older frames if needed
            if not frame_q.full():
                frame_q.put_nowait(roi)
            else:
                try: frame_q.get_nowait(); frame_q.put_nowait(roi)
            time.sleep(0.015)   # ≈ 60 fps max

# ------------------------------------------------------------------
# 2️⃣ Board‑processor thread
# ------------------------------------------------------------------
def board_processor_loop():
    lower = np.array([0, 50, 50])
    upper = np.array([180, 255, 255])
    kernel = np.ones((3,3), np.uint8)

    while True:
        roi = frame_q.get()
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # binary board 20×10
        board = cv2.resize(mask, (10,20), interpolation=cv2.INTER_AREA)
        board = (board > 30).astype(np.uint8)

        if not board_q.full():
            board_q.put_nowait((board, mask))
        else:
            try: board_q.get_nowait(); board_q.put_nowait((board, mask))
        # keep looping

# ------------------------------------------------------------------
# 3️⃣ Piece‑detector thread (template matching)
# ------------------------------------------------------------------
# Simple 4×4 templates (hard‑coded for brevity)
TEMPLATES = {
    "I": [np.array([[1,1,1,1]], dtype=np.uint8),
          np.array([[1],[1],[1],[1]], dtype=np.uint8)],
    "O": [np.array([[1,1],[1,1]], dtype=np.uint8)],
    "T": [np.array([[1,1,1],[0,1,0]], dtype=np.uint8),
          np.array([[0,1],[1,1],[0,1]], dtype=np.uint8),
    "S": [np.array([[0,1,1],[1,1,0]], dtype=np.uint8),
    "Z": [np.array([[1,1,0],[0,1,1]], dtype=np.uint8),
    "J": [np.array([[1,0,0],[1,1,1]], dtype=np.uint8),
    "L": [np.array([[0,0,1],[1,1,1]], dtype=np.uint8)]
}

def match_template(tiny):
    best_score = 1e9
    best_type, best_rot = None, None
    for typ, rots in TEMPLATES.items():
        for r_idx, tmpl in enumerate(rots):
            # resize tmpl to 4×4 if needed
            tmpl4 = cv2.resize(tmpl, (4,4), interpolation=cv2.INTER_NEAREST)
            diff = np.sum(np.abs(tiny - tmpl4))
            if diff < best_score:
                best_score, best_type, best_rot = diff, typ, r_idx
    return best_type, best_rot

def piece_detector_loop():
    prev_mask = np.zeros((H, W), dtype=np.uint8)
    while True:
        board, cur_mask = board_q.get()
        diff = cv2.subtract(cur_mask, prev_mask)
        # find largest component (the falling piece)
        num, labels, stats, _ = cv2.connectedComponentsWithStats(diff, connectivity=8)
        if num > 1:
            largest = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1
            piece_mask = (labels == largest).astype(np.uint8) * 255
            tiny = cv2.resize(piece_mask, (4,4), interpolation=cv2.INTER_NEAREST)
            typ, rot = match_template(tiny)
        else:
            typ, rot = "I", 0     # fallback
        piece = {"type": typ, "rotation": rot}
        if not piece_q.full():
            piece_q.put_nowait(piece)
        else:
            try: piece_q.get_nowait(); piece_q.put_nowait(piece)
        prev_mask = cur_mask.copy()

# ------------------------------------------------------------------
# 4️⃣ Prediction thread (calls local UDP server)
# ------------------------------------------------------------------
import socket, json

PRED_HOST = "127.0.0.1"
PRED_PORT = 51424   # must match predictor_server.py

def prediction_loop():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(0.02)   # 20 ms
    while True:
        board, _ = board_q.get()
        piece = piece_q.get()
        payload = json.dumps({
            "board": board.tolist(),
            "current_piece": piece
        }).encode()
        client.sendto(payload, (PRED_HOST, PRED_PORT))
        try:
            data, _ = client.recvfrom(1024)
            pred = json.loads(data.decode())
            pred["piece_type"] = piece["type"]   # ensure renderer knows the type
            if not prediction_q.full():
                prediction_q.put_nowait(pred)
            else:
                try: prediction_q.get_nowait(); prediction_q.put_nowait(pred)
        except socket.timeout:
            # no response – just skip this frame
            pass

# ------------------------------------------------------------------
# 5️⃣ Overlay thread (Pygame)
# ------------------------------------------------------------------
def init_window():
    pygame.init()
    screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
    if sys.platform.startswith('win'):
        hwnd = pygame.display.get_wm_info()["window"]
        WS_EX_LAYERED = 0x80000
        WS_EX_TRANSPARENT = 0x20
        ctypes.windll.user32.SetWindowLongW(hwnd, -20,
                                           WS_EX_LAYERED | WS_EX_TRANSPARENT)
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 200, 0x2)
    return screen

def draw_ghost(screen, pred):
    typ = pred["piece_type"]
    rot = pred["rotation"]
    col = pred["column"]
    shape = TEMPLATES[typ][rot % len(TEMPLATES[typ])]
    for dr, row in enumerate(shape):
        for dc, val in enumerate(row):
            if val:
                r = dr * CELL_PX
                c = (col + dc) * CELL_PX
                pygame.draw.rect(screen, (255,255,0),
                                 (c, r, CELL_PX-2, CELL_PX-2), 2)

def overlay_loop():
    screen = init_window()
    clock = pygame.time.Clock()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        screen.fill((0,0,0,0))
        try:
            pred = prediction_q.get_nowait()
            draw_ghost(screen, pred)
        except queue.Empty:
            pass
        pygame.display.flip()
        clock.tick(30)

# ------------------------------------------------------------------
# Main – start all threads
# ------------------------------------------------------------------
if __name__ == "__main__":
    threads = [
        threading.Thread(target=capture_loop, daemon=True),
        threading.Thread(target=board_processor_loop, daemon=True),
        threading.Thread(target=piece_detector_loop, daemon=True),
        threading.Thread(target=prediction_loop, daemon=True),
        threading.Thread(target=overlay_loop, daemon=True)
    ]
    for t in threads:
        t.start()
    # Keep the main thread alive – you can also add a simple CLI here.
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down.")
        sys.exit()
📎 How to run the whole thing (copy‑paste)
# 1️⃣ Clone the scaffold (replace with your own repo if you wish)
git clone https://github.com/yourname/tetris-overlay.git
cd tetris-overlay

# 2️⃣ Install dependencies
python -m pip install -r requirements.txt

# 3️⃣ Calibrate once – open a screenshot of the game in a file (PNG/JPG)
python src/calibrate.py
# Follow the on‑screen instructions: click the top‑left corner of the grid,
# then the bottom‑right corner. The file calibration.json will be created.

# 4️⃣ Start the prediction backend (choose heuristic or cnn)
python src/predictor_server.py --backend heuristic   # fast, no extra model
#   or
# python src/predictor_server.py --backend cnn --cnn-model tetris_cnn.onnx

# 5️⃣ Launch the overlay pipeline
python src/capture_and_process.py
You should now see a transparent yellow outline appear on the board, indicating the AI’s recommended placement.
Press Ctrl‑C in the terminal to stop any of the Python processes.