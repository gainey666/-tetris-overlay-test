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

# Legacy alias file retained for compatibility with older import paths.
__all__ = [
    "orchestrator_main_alias",
    "orchestrator_agent_main",
    "orchestrator_agent_main_alias",
]
