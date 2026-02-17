#!/usr/bin/env python3
"""
Real Tetris Overlay - Shows ghost pieces on your actual Tetris game.
"""

import sys
from pathlib import Path

# -----------------------------------------------------------------
# Tracer import – safe fallback when package is unavailable.
# -----------------------------------------------------------------
try:
    from tracer.client import safe_trace_calls as trace_calls
except Exception:  # pragma: no cover
    def trace_calls(*_, **__):  # type: ignore[misc]
        def _decorator(func):
            return func

        return _decorator

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication, QMessageBox
from tetris_overlay.ui.wizard import run_wizard
from tetris_overlay.core.overlay import GhostOverlay
from tetris_overlay.core.config import OverlayConfig
from tetris_overlay.utils.logger import logger


@trace_calls("S")
def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    
    # Try to load existing config first
    config_path = Path.home() / ".tetris_overlay" / "config.json"
    if config_path.exists():
        try:
            config = OverlayConfig.load(config_path)
            logger.info(f"Using saved config for window {config.target_hwnd}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            config = None
    else:
        config = None
    
    # If no valid config, run the wizard
    if not config:
        logger.info("No valid config found, running window selection wizard...")
        config = run_wizard()
        if not config:
            logger.error("No window selected. Exiting.")
            return 1
    
    # Create and show the overlay
    try:
        overlay = GhostOverlay(config)
        overlay.show()
        
        # Save config for next time
        config.save(config_path)
        
        logger.info(f"Overlay started for window {config.target_hwnd}")
        logger.info("Press Ctrl+C to exit")
        
        return app.exec()
        
    except Exception as e:
        logger.error(f"Failed to start overlay: {e}")
        QMessageBox.critical(None, "Error", f"Failed to start overlay: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
