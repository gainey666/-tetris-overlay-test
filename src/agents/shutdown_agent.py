"""Graceful shutdown – stops all running agents."""

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


class ShutdownAgent(BaseAgent):
    """Stops any registered agents."""

    def __init__(self) -> None:
    @trace_calls('__init__', 'shutdown_agent.py', 32)
        self._agents: list[BaseAgent] = []

    def register(self, agent: BaseAgent) -> None:
    @trace_calls('register', 'shutdown_agent.py', 35)
        self._agents.append(agent)

    def handle(self, params: Optional[dict] = None) -> None:
    @trace_calls('handle', 'shutdown_agent.py', 38)
        log.info("ShutdownAgent – stopping %d agents.", len(self._agents))
        for ag in self._agents:
            try:
                stop = getattr(ag, "stop", None)
                if callable(stop):
                    stop()
            except Exception as exc:
                log.exception("Error stopping %s: %s", ag.__class__.__name__, exc)
