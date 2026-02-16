"""Graceful shutdown – stops all running agents."""

from __future__ import annotations

import logging
from typing import Optional

from .base_agent import BaseAgent

log = logging.getLogger(__name__)


class ShutdownAgent(BaseAgent):
    """Stops any registered agents."""

    def __init__(self) -> None:
        self._agents: list[BaseAgent] = []

    def register(self, agent: BaseAgent) -> None:
        self._agents.append(agent)

    def handle(self, params: Optional[dict] = None) -> None:
        log.info("ShutdownAgent – stopping %d agents.", len(self._agents))
        for ag in self._agents:
            try:
                stop = getattr(ag, "stop", None)
                if callable(stop):
                    stop()
            except Exception as exc:
                log.exception("Error stopping %s: %s", ag.__class__.__name__, exc)
