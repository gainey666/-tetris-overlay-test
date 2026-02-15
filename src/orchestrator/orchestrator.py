"""Main orchestrator – loads a plan and dispatches actions to registered agents."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Dict, List

from .model import Action, load_plan

log = logging.getLogger(__name__)


def _build_registry() -> Dict[str, Callable[[dict], None]]:
    from src.agents import (
        BenchmarkAgent,
        BoardProcessorAgent,
        CalibrateAgent,
        ConfigAgent,
        OverlayRendererAgent,
        PredictionAgent,
        RunAgent,
        ShutdownAgent,
    )
    from src.agents.synthetic_capture_agent import SyntheticCaptureAgent
    from src.agents.prediction_agent_mock_perfect import PredictionAgent
    from src.agents.overlay_renderer_agent_simple import OverlayRendererAgentSimple as SimpleOverlayAgent

    capture = SyntheticCaptureAgent(fps=60)
    board = BoardProcessorAgent(capture)
    prediction = PredictionAgent()
    overlay = SimpleOverlayAgent()

    return {
        "calibrate": CalibrateAgent(),
        "load_config": ConfigAgent(),
        "run": RunAgent(),
        "overlay": overlay,
        "benchmark": BenchmarkAgent(),
        "shutdown": ShutdownAgent(),
    }


AGENT_REGISTRY: Dict[str, Callable[[dict], None]] = _build_registry()


def execute_plan(actions: List[Action]) -> None:
    for act in actions:
        log.info("▶️ Executing step: %s (params=%s)", act.name, act.params)
        agent = AGENT_REGISTRY.get(act.name)
        if agent is None:
            raise RuntimeError(f"No registered agent for step '{act.name}'")
        try:
            agent.handle(act.params)
            log.info("✅ Step '%s' completed.", act.name)
        except Exception as exc:
            log.exception("❌ Step '%s' raised an exception: %s", act.name, exc)
            raise


def main(plan_path: str | Path = "orchestration_plan.yaml") -> None:
    actions = load_plan(plan_path)
    execute_plan(actions)
