"""Action dataclass and plan-loading utilities."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Action:
    """One step of the orchestration plan."""

    name: str
    params: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Action":
        if "name" not in data:
            raise ValueError("Each step must contain a 'name' field.")
        return Action(name=data["name"], params=data.get("params", {}))


def load_plan(file_path: Path | str) -> List[Action]:
    """Parse a YAML plan and return a list of Action objects."""
    import yaml

    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Plan file not found: {path}")

    raw = yaml.safe_load(path.read_text())
    steps = raw.get("steps", [])
    actions = [Action.from_dict(step) for step in steps]
    log.debug("Loaded plan %s with %d actions.", path, len(actions))
    return actions
