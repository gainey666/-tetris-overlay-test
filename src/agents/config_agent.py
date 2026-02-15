"""Loads the AppConfig (JSON) and makes it available to other agents."""
from __future__ import annotations

import logging
from typing import Optional

from ..config import AppConfig
from .base_agent import BaseAgent

log = logging.getLogger(__name__)


class ConfigAgent(BaseAgent):
    """Reads config.json (or creates defaults) and caches the object."""

    config: AppConfig | None = None

    def handle(self, params: Optional[dict] = None) -> AppConfig | None:
        if self.__class__.config is None:
            self.__class__.config = AppConfig.load()
            log.info("Loaded configuration: %s", self.__class__.config)
        else:
            log.debug("Config already loaded – reuse existing instance.")
        return self.__class__.config
