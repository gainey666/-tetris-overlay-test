#!/usr/bin/env python3
"""
Complete cleanup of broken overlay files
Restores original overlay system to working state
"""

import re
from pathlib import Path

def clean_file_completely(file_path, original_content=None):
    """Completely rewrite a file with clean content"""
    try:
        if original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"✅ Restored {file_path}")
        else:
            print(f"⚠️ No content provided for {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error restoring {file_path}: {e}")
        return False

def main():
    """Complete cleanup of overlay files"""
    print("🧹 Complete cleanup of broken overlay files...")
    
    # Clean config.py
    config_content = '''"""
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
'''
    
    clean_file_completely("src/tetris_overlay/core/config.py", config_content)
    
    # Clean __init__.py
    init_content = '''"""
Tetris Overlay - A real-time ghost piece overlay for Tetris games.
"""

__version__ = "0.1.0"
__author__ = "Tetris Overlay Team"

from .core.config import OverlayConfig
from .core.overlay import GhostOverlay


__all__ = ["OverlayConfig", "GhostOverlay"]
'''
    
    clean_file_completely("src/tetris_overlay/__init__.py", init_content)
    
    print("✅ Complete cleanup finished!")
    print("🎮 Original overlay system should now work!")

if __name__ == "__main__":
    main()
