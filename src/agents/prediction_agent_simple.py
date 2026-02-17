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
    def handle(self, param):
    @trace_calls('handle', 'prediction_agent_simple.py', 21)
        # naive: place at leftmost column
        return {"target_col": 0, "target_rot": param["orientation"]}
