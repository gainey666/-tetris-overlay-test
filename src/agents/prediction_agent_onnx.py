# ---------------------------------------------------------
# prediction_agent_onnx.py
# ---------------------------------------------------------
import numpy as np, onnxruntime as ort
from .base_agent import BaseAgent
from pathlib import Path

class PredictionAgent(BaseAgent):
    """
    Loads a pre‑trained ONNX Tetris model (perfect play).
    Input: dict with:
        - board: 20×10 uint8 (0 / 255)
        - piece: "I","O","T","S","Z","J","L"
        - orientation: 0‑3 (ignored by the model – it handles rotations internally)
    Output: dict with:
        - target_col, target_rot, is_tspin, is_b2b, combo
    """
    def __init__(self):
        model_path = Path(__file__).parent.parent / "models" / "tetris_perfect.onnx"
        if not model_path.is_file():
            raise FileNotFoundError(f"ONNX model not found: {model_path}")
        self.session = ort.InferenceSession(str(model_path), providers=["CPUExecutionProvider"])

        # Input name expected by the model (verify with Netron)
        self.input_name = self.session.get_inputs()[0].name
        # Output name (single tensor with placement data)
        self.output_name = self.session.get_outputs()[0].name

    def _prepare_input(self, board, piece, orientation):
        # Convert board 0/255 → 0/1 floats
        board_bin = (board > 0).astype(np.float32).reshape(1, 20, 10)

        # Piece encoding: one‑hot 7‑dim vector
        piece_ids = {"I":0,"O":1,"T":2,"S":3,"Z":4,"J":5,"L":6}
        piece_vec = np.zeros((1,7), dtype=np.float32)
        piece_vec[0, piece_ids[piece]] = 1.0

        # Orientation (0‑3) as integer scalar
        orient_scalar = np.array([orientation], dtype=np.int64)

        # Model expects a dict of inputs – adapt if your ONNX has a single concatenated tensor
        return {
            "board": board_bin,
            "piece": piece_vec,
            "orientation": orient_scalar
        }

    def handle(self, params):
        board = params["board"]
        piece = params["piece"]
        orient = params["orientation"]
        ort_input = self._prepare_input(board, piece, orient)

        # Run inference
        ort_out = self.session.run([self.output_name], ort_input)[0]

        # Model output layout (example):
        # [col, rot, is_tspin, is_b2b, combo]  all as scalars
        col, rot, is_ts, is_b2b, combo = ort_out[0]
        return {
            "target_col": int(col),
            "target_rot": int(rot),
            "is_tspin": bool(is_ts),
            "is_b2b":   bool(is_b2b),
            "combo":    int(combo)
        }

    def start(self):
        """No-op for compatibility with existing orchestrator."""
        pass

    def stop(self):
        """No-op for compatibility with existing orchestrator."""
        pass
