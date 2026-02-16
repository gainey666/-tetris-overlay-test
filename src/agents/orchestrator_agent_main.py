"""Thin wrapper that forwards a plan file to the main orchestrator."""

from __future__ import annotations

import logging
from typing import Optional

from .base_agent import BaseAgent

log = logging.getLogger(__name__)


class OrchestratorAgentMain(BaseAgent):
    """Allows the orchestrator to be addressed as an agent."""

    def handle(self, params: Optional[dict] = None) -> None:
        from ..orchestrator.orchestrator import main as orchestrate

        plan_path = params.get("plan") if params else "orchestration_plan.yaml"
        log.info("OrchestratorAgentMain – executing nested plan %s", plan_path)
        orchestrate(plan_path=plan_path)
