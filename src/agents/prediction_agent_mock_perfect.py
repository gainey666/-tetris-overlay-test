# ---------------------------------------------------------
# prediction_agent_mock_perfect.py
# ---------------------------------------------------------
import numpy as np
from .base_agent import BaseAgent


class PredictionAgent(BaseAgent):
    """
    Mock perfect AI that always chooses the optimal column (0) and rotation (0).
    This simulates 100% accuracy for testing when the ONNX model is unavailable.
    """

    def __init__(self):
        pass

    def handle(self, params):
        board = params["board"]
        piece = params["piece"]
        orient = params["orientation"]
        # Mock perfect play: always column 0, rotation 0
        return {
            "target_col": 0,
            "target_rot": 0,
            "is_tspin": False,
            "is_b2b": False,
            "combo": 0,
        }

    def start(self):
        """No-op for compatibility with existing orchestrator."""
        pass

    def stop(self):
        """No-op for compatibility with existing orchestrator."""
        pass
