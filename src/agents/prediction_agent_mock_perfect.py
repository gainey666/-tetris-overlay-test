# ---------------------------------------------------------
# prediction_agent_mock_perfect.py
# ---------------------------------------------------------
import numpy as np
from .base_agent import BaseAgent

# Import our logger bridge
try:
    import logger_bridge as log

# Import global function tracer
try:
    from tracer.client import safe_trace_calls as trace_calls
    TRACER_AVAILABLE = True
except ImportError:
    TRACER_AVAILABLE = False

    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False



class PredictionAgent(BaseAgent):
    """
    Mock perfect AI that always chooses the optimal column (0) and rotation (0).
    This simulates 100% accuracy for testing when the ONNX model is unavailable.
    """

    def __init__(self):
    @trace_calls('__init__', 'prediction_agent_mock_perfect.py', 30)
        pass

    def handle(self, params):
    @trace_calls('handle', 'prediction_agent_mock_perfect.py', 33)
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
    @trace_calls('start', 'prediction_agent_mock_perfect.py', 46)
        """No-op for compatibility with existing orchestrator."""
        pass

    def stop(self):
    @trace_calls('stop', 'prediction_agent_mock_perfect.py', 50)
        """No-op for compatibility with existing orchestrator."""
        pass
