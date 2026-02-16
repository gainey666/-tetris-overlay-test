"""
Current Settings Singleton Module
Provides global access to application settings with update capabilities.
"""

from .settings_storage import load as load_settings, save as save_settings
from .settings import Settings
from typing import Optional
import logging

# Load once at import time – JSON/TinyDB will be created if missing
CURRENT: Settings = load_settings()

def update(new_settings: Settings) -> None:
    """Update the global settings singleton and persist to disk."""
    global CURRENT
    CURRENT = new_settings
    save_settings(new_settings)
    logging.info("Settings updated and persisted")

def get() -> Settings:
    """Get the current settings singleton."""
    return CURRENT
