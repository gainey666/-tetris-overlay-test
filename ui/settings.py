"""Settings data model for the Tetris overlay."""

from dataclasses import dataclass, field
from typing import Dict, Tuple

# ROI is stored as (left, top, width, height)
Rect = Tuple[int, int, int, int]

@dataclass
class GhostStyle:
    colour: Tuple[int, int, int] = (255, 255, 255)   # white
    opacity: float = 0.5                           # 0-1

@dataclass
class Hotkeys:
    toggle_overlay: str = "f9"
    open_settings: str = "f1"
    debug_logging: str = "f2"
    quit: str = "esc"
    calibrate: str = "ctrl+alt+c"
    open_stats: str = "ctrl+alt+s"

@dataclass
class Settings:
    roi_left: Rect = (0, 0, 640, 360)
    roi_right: Rect = (0, 0, 640, 360)
    prediction_agent: str = "dellacherie"
    ghost: GhostStyle = field(default_factory=GhostStyle)
    hotkeys: Hotkeys = field(default_factory=Hotkeys)
    show_combo: bool = True
    show_b2b: bool = True
    
    def to_dict(self) -> Dict:
        """Convert settings to dictionary for JSON storage."""
        return {
            "roi_left": list(self.roi_left),
            "roi_right": list(self.roi_right),
            "prediction_agent": self.prediction_agent,
            "ghost": {
                "colour": list(self.ghost.colour), 
                "opacity": self.ghost.opacity
            },
            "hotkeys": self.hotkeys.__dict__,
            "show_combo": self.show_combo,
            "show_b2b": self.show_b2b,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Settings':
        """Create settings from dictionary."""
        settings = cls()
        
        # ROI
        if "roi_left" in data:
            settings.roi_left = tuple(data["roi_left"])
        if "roi_right" in data:
            settings.roi_right = tuple(data["roi_right"])
        
        # Prediction agent
        if "prediction_agent" in data:
            settings.prediction_agent = data["prediction_agent"]
        
        # Ghost style
        if "ghost" in data:
            ghost_data = data["ghost"]
            settings.ghost = GhostStyle(
                colour=tuple(ghost_data.get("colour", [255, 255, 255])),
                opacity=ghost_data.get("opacity", 0.5)
            )
        
        # Hotkeys
        if "hotkeys" in data:
            hk_data = data["hotkeys"]
            settings.hotkeys = Hotkeys(
                toggle_overlay=hk_data.get("toggle_overlay", "f9"),
                open_settings=hk_data.get("open_settings", "f1"),
                debug_logging=hk_data.get("debug_logging", "f2"),
                quit=hk_data.get("quit", "esc"),
                calibrate=hk_data.get("calibrate", "ctrl+alt+c"),
                open_stats=hk_data.get("open_stats", "ctrl+alt+s")
            )
        
        # Visual flags
        if "show_combo" in data:
            settings.show_combo = data["show_combo"]
        if "show_b2b" in data:
            settings.show_b2b = data["show_b2b"]
        
        return settings
