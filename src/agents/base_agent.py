"""Base class for all agents."""

from __future__ import annotations

import abc
import logging
from typing import Any, Mapping, Optional

log = logging.getLogger(__name__)


class BaseAgent(abc.ABC):
    """All agents must implement a `handle(params)` method."""

    @abc.abstractmethod
    def handle(self, params: Optional[Mapping[str, Any]] = None) -> None:
        """Execute the agent’s work."""
        raise NotImplementedError
