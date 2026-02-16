"""Feature toggle system for the Tetris overlay."""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from logging import getLogger

log = getLogger(__name__)

@dataclass
class FeatureToggles:
    """Feature toggle configuration."""
    ghost_pieces_enabled: bool = True
    performance_monitor_enabled: bool = True
    statistics_enabled: bool = True
    b2b_indicators_enabled: bool = True
    combo_indicators_enabled: bool = True
    debug_mode_enabled: bool = False
    experimental_ai_enabled: bool = False

class FeatureToggleManager:
    """Manages feature toggles with persistence."""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path("feature_toggles.json")
        self._toggles = FeatureToggles()
        self.load()
    
    def load(self):
        """Load feature toggles from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                # Update toggles with loaded data, using defaults for missing keys
                for key, value in data.items():
                    if hasattr(self._toggles, key):
                        setattr(self._toggles, key, value)
                log.info(f"Loaded feature toggles from {self.config_file}")
            except Exception as e:
                log.error(f"Failed to load feature toggles: {e}")
                # Use defaults
                self._toggles = FeatureToggles()
        else:
            log.info("Feature toggle file not found, using defaults")
            self.save()  # Create default config file
    
    def save(self):
        """Save feature toggles to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self._toggles), f, indent=2)
            log.info(f"Saved feature toggles to {self.config_file}")
        except Exception as e:
            log.error(f"Failed to save feature toggles: {e}")
    
    def is_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled."""
        if not hasattr(self._toggles, feature):
            log.warning(f"Unknown feature toggle: {feature}")
            return False
        return getattr(self._toggles, feature)
    
    def set_enabled(self, feature: str, enabled: bool):
        """Enable or disable a feature."""
        if not hasattr(self._toggles, feature):
            log.warning(f"Unknown feature toggle: {feature}")
            return
        
        setattr(self._toggles, feature, enabled)
        self.save()
        log.info(f"Feature '{feature}' {'enabled' if enabled else 'disabled'}")
    
    def get_all_toggles(self) -> Dict[str, bool]:
        """Get all feature toggles as a dictionary."""
        return asdict(self._toggles)
    
    def reset_to_defaults(self):
        """Reset all toggles to default values."""
        self._toggles = FeatureToggles()
        self.save()
        log.info("Reset all feature toggles to defaults")

# Global feature toggle manager
feature_manager = FeatureToggleManager()

# Convenience functions
def is_feature_enabled(feature: str) -> bool:
    """Check if a feature is enabled globally."""
    return feature_manager.is_enabled(feature)

def enable_feature(feature: str, enabled: bool = True):
    """Enable or disable a feature globally."""
    feature_manager.set_enabled(feature, enabled)

def get_feature_toggles() -> Dict[str, bool]:
    """Get all feature toggles."""
    return feature_manager.get_all_toggles()
