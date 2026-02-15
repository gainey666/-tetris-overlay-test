"""Global error-handling wrapper – logs uncaught exceptions."""
from __future__ import annotations

import logging
from typing import Optional

from .base_agent import BaseAgent

log = logging.getLogger(__name__)


class ErrorHandlerAgent(BaseAgent):
    """Provided for custom plans; no-op in the default pipeline."""

    def handle(self, params: Optional[dict] = None) -> None:
        log.debug("ErrorHandlerAgent invoked – no-op.")
