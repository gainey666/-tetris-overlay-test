"""
Configuration management for Tetris Overlay.
"""

from pydantic import BaseModel, Field, field_validator
from pathlib import Path
from typing import Optional



class OverlayConfig(BaseModel):
    """Configuration for the Tetris overlay."""
    
    target_hwnd: int = Field(..., description="Window handle of the Tetris client")
    opacity: float = Field(0.6, ge=0.0, le=1.0, description="Overlay opacity")
    ghost_colour: str = Field("#00FF00", pattern=r"^#(?:[0-9A-Fa-f]{6})$", description="Ghost piece color")
    refresh_rate: int = Field(30, ge=10, le=60, description="Refresh rate in FPS")
    
    @field_validator("target_hwnd")
    @classmethod
    def hwnd_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("HWND must be a positive integer")
        return v
    
    @classmethod
    def load(cls, path: Path) -> "OverlayConfig":
        """Load configuration from file."""
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        return cls.model_validate_json(path.read_text())
    
    def save(self, path: Path) -> None:
        """Save configuration to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.model_dump_json(indent=2))
    
    @classmethod
    def create_default(cls, target_hwnd: int) -> "OverlayConfig":
        """Create a default configuration."""
        return cls(target_hwnd=target_hwnd)
