# System Architecture – Screen‑Based Tetris Overlay

```
+------------------------+ UDP (JSON) +------------------------+
| Capture Agent          | ───────────────────► | Prediction Agent |
| (mss → raw frame)      |                    | (hand‑crafted or CNN) |
+------------------------+                    +------------------------+
        |                                         |
        | 1. ROI crop + colour‑threshold          |
        ▼                                         |
+------------------------+ Queue +------------------------+
| Board‑Processor Agent  | ◄────────────────►| Piece‑Detector Agent |
| (binary 20×10 matrix)  |                    | (template or CNN)      |
+------------------------+                    +------------------------+
        |                                         |
        | 2. Board matrix + piece info           |
        ▼ ▼                                       |
+---------------------------------------------------------------+
| Overlay Renderer Agent (Pygame)                               |
| Receives {rotation, column, piece_type} → draws ghost         |
+---------------------------------------------------------------+
```

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
   ```
   It returns
   ```json
   {"rotation":1,"column":5,"piece_type":"T","score":13.2}
   ```
   – either by calling tetris_bot.best_move (hand‑crafted) or by running an ONNX CNN (onnxruntime).  
6. Overlay Renderer reads the prediction via a thread‑safe queue, draws a semi‑transparent outline of the piece at the suggested column/rotation, and keeps the window always‑on‑top & click‑through.

## Technologies
| Layer | Library / Tool | Language |
|-------|----------------|----------|
| Capture | mss (cross‑platform screen grab) | Python |
| Image processing | OpenCV (cv2) – colour threshold, morphology | Python |
| Piece detection | Template matching or ONNX CNN (onnxruntime) | Python |
| Prediction | Karpathy's tetris_bot (NumPy) or custom CNN | Python |
| Overlay | Pygame transparent window (NOFRAME, WS_EX_LAYERED) | Python |
| IPC | UDP sockets (local 127.0.0.1) + queue.Queue for intra‑process | Python |
