"""Global error-handling wrapper – logs uncaught exceptions."""

from __future__ import annotations

import logging
from typing import Optional

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


log = logging.getLogger(__name__)


class ErrorHandlerAgent(BaseAgent):
    """Provided for custom plans; no-op in the default pipeline."""

    def handle(self, params: Optional[dict] = None) -> None:
    @trace_calls('handle', 'error_handler_agent.py', 32)
        log.debug("ErrorHandlerAgent invoked – no-op.")
