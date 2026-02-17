"""
Logging utilities for Tetris Overlay.
"""

import sys
from pathlib import Path
from typing import Optional

# Import our logger bridge
try:
    import logger_bridge as log

# Import global function tracer
try:
    from tracer.client import safe_trace_calls as trace_calls
    TRACER_AVAILABLE = True
except ImportError:
    TRACER_AVAILABLE = False

    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False


# Simple logger implementation (loguru can be added later)
class SimpleLogger:
    """Simple logger for the overlay."""
    
    def __init__(self, name: str = "tetris_overlay"):
        self.name = name
        self.log_file = Path.home() / ".tetris_overlay" / "overlay.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def info(self, message: str):
        """Log info message."""
        print(f"[INFO] {message}")
        self._write_to_file(f"INFO: {message}")
    
    def error(self, message: str):
        """Log error message."""
        print(f"[ERROR] {message}", file=sys.stderr)
        self._write_to_file(f"ERROR: {message}")
    
    def warning(self, message: str):
        """Log warning message."""
        print(f"[WARNING] {message}")
        self._write_to_file(f"WARNING: {message}")
    
    def debug(self, message: str):
        """Log debug message."""
        print(f"[DEBUG] {message}")
        self._write_to_file(f"DEBUG: {message}")
    
    def _write_to_file(self, message: str):
        """Write message to log file."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"{message}\n")
        except Exception:
            pass  # Fail silently if we can't write to file

# Global logger instance
logger = SimpleLogger()
