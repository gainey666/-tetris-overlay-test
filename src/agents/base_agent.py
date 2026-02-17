"""Base class for all agents."""

from __future__ import annotations

import abc
import logging
from typing import Any, Mapping, Optional

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


class BaseAgent(abc.ABC):
    """All agents must implement a `handle(params)` method."""

    @abc.abstractmethod
    def handle(self, params: Optional[Mapping[str, Any]] = None) -> None:
    @trace_calls('handle', 'base_agent.py', 32)
        """Execute the agent’s work."""
        raise NotImplementedError
