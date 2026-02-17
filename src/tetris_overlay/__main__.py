"""
Main entry point for Tetris Overlay.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox
from .ui.wizard import run_wizard
from .core.overlay import GhostOverlay

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



def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    
    # Try to load existing config first
    config_path = Path.home() / ".tetris_overlay" / "config.json"
    if config_path.exists():
        try:
            config = OverlayConfig.load(config_path)
            print(f"Using saved config for window {config.target_hwnd}")
        except Exception as e:
            print(f"Failed to load config: {e}")
            config = None
    else:
        config = None
    
    # If no valid config, run the wizard
    if not config:
        print("No valid config found, running window selection wizard...")
        config = run_wizard()
        if not config:
            print("No window selected. Exiting.")
            return 1
    
    # Create and show the overlay
    try:
        overlay = GhostOverlay(config)
        overlay.show()
        
        # Save config for next time
        config.save(config_path)
        
        print(f"Overlay started for window {config.target_hwnd}")
        print("Press Ctrl+C to exit")
        
        return app.exec()
        
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to start overlay: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
