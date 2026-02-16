"""Error handling and graceful degradation for the Tetris overlay."""

import logging
import sys
import traceback
from pathlib import Path
from typing import Optional, Callable, Any
import pygame
import tkinter as tk
from tkinter import messagebox, simpledialog

log = logging.getLogger(__name__)

class OverlayErrorHandler:
    """Handles errors gracefully with user-friendly messages and fallbacks."""
    
    def __init__(self):
        self.critical_errors = []
        self.warnings = []
        self.fallback_mode = False
        
    def handle_critical_error(self, error: Exception, context: str = "") -> bool:
        """Handle critical errors that prevent overlay from running.
        
        Returns:
            bool: True if error was handled gracefully, False if application should exit
        """
        error_msg = f"Critical Error in {context}: {str(error)}"
        log.error(error_msg)
        log.error(traceback.format_exc())
        
        self.critical_errors.append((error_msg, traceback.format_exc()))
        
        # Check if we can continue with fallback mode
        if self._can_use_fallback_mode(error):
            return self._enable_fallback_mode(error, context)
        else:
            return self._show_error_dialog(error, context)
    
    def handle_warning(self, warning: str, context: str = ""):
        """Handle non-critical warnings."""
        warning_msg = f"Warning in {context}: {warning}"
        log.warning(warning_msg)
        self.warnings.append(warning_msg)
        
        # Show toast notification if in fallback mode
        if self.fallback_mode:
            self._show_toast(warning_msg, level="warning")
    
    def _can_use_fallback_mode(self, error: Exception) -> bool:
        """Check if we can continue in fallback mode."""
        fallback_capable_errors = [
            "ScreenCapture",  # Screen capture issues
            "ROI",  # ROI calibration issues
            "PredictionAgent",  # AI prediction issues
            "Database",  # Stats database issues
        ]
        
        error_str = str(error)
        return any(err_type in error_str for err_type in fallback_capable_errors)
    
    def _enable_fallback_mode(self, error: Exception, context: str) -> bool:
        """Enable fallback mode with reduced functionality."""
        self.fallback_mode = True
        
        # Show user-friendly message
        msg = f"""
Tetris Overlay - Fallback Mode

The overlay encountered an issue: {context}

{str(error)}

The overlay will continue in limited mode:
- Basic overlay rendering
- No screen capture
- No AI predictions
- No statistics tracking

You can try:
1. Restarting the overlay
2. Recalibrating ROIs (Ctrl+Alt+C)
3. Checking game window visibility

Continue in fallback mode?
        """
        
        try:
            root = tk.Tk()
            root.withdraw()
            result = messagebox.askyesno("Tetris Overlay - Fallback Mode", msg)
            root.destroy()
            return result
        except Exception as e:
            log.error(f"Failed to show fallback dialog: {e}")
            return True  # Default to fallback mode
    
    def _show_error_dialog(self, error: Exception, context: str) -> bool:
        """Show critical error dialog and offer options."""
        msg = f"""
Tetris Overlay - Critical Error

A critical error occurred: {context}

{str(error)}

Technical details:
{traceback.format_exc()}

Options:
1. Retry - Try to start the overlay again
2. Troubleshoot - Open troubleshooting guide
3. Exit - Close the overlay

What would you like to do?
        """
        
        try:
            root = tk.Tk()
            root.withdraw()
            result = messagebox.askyesnocancel("Tetris Overlay - Error", msg)
            root.destroy()
            
            if result is True:  # Yes = Retry
                return True
            elif result is False:  # No = Troubleshoot
                self._open_troubleshooting_guide()
                return True
            else:  # Cancel = Exit
                return False
                
        except Exception as e:
            log.error(f"Failed to show error dialog: {e}")
            return False
    
    def _show_toast(self, message: str, level: str = "info"):
        """Show toast notification (simple implementation)."""
        try:
            root = tk.Tk()
            root.withdraw()
            
            # Configure colors based on level
            colors = {
                "info": "lightblue",
                "warning": "yellow", 
                "error": "lightcoral"
            }
            
            # Create simple toast window
            toast = tk.Toplevel(root)
            toast.title("Tetris Overlay")
            toast.geometry("400x100")
            toast.configure(bg=colors.get(level, "lightgray"))
            
            label = tk.Label(toast, text=message, wraplength=380, bg=colors.get(level, "lightgray"))
            label.pack(pady=20)
            
            # Auto-close after 3 seconds
            toast.after(3000, toast.destroy)
            
            root.mainloop()
            
        except Exception as e:
            log.error(f"Failed to show toast: {e}")
    
    def _open_troubleshooting_guide(self):
        """Open troubleshooting guide."""
        try:
            import webbrowser
            guide_path = Path(__file__).parent / "README.md"
            if guide_path.exists():
                webbrowser.open(f"file://{guide_path.absolute()}")
            else:
                webbrowser.open("https://github.com/gainey666/-tetris-overlay-test#troubleshooting")
        except Exception as e:
            log.error(f"Failed to open troubleshooting guide: {e}")
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are available."""
        missing_deps = []
        
        # Check critical dependencies
        deps = {
            "pygame": "pygame",
            "tkinter": "tkinter",
            "keyboard": "keyboard",
            "mss": "mss",
            "PIL": "PIL",
        }
        
        for module_name, import_name in deps.items():
            try:
                __import__(import_name)
            except ImportError:
                missing_deps.append(module_name)
        
        if missing_deps:
            error_msg = f"Missing dependencies: {', '.join(missing_deps)}"
            return self.handle_critical_error(ImportError(error_msg), "Dependency Check")
        
        return True
    
    def check_game_window(self) -> bool:
        """Check if Tetris game window is available."""
        try:
            import window_manager
            windows = window_manager.find_tetris_windows()
            
            if not windows:
                self.handle_warning(
                    "No Tetris windows found. Make sure Tetris is running.",
                    "Game Window Check"
                )
                return False
            
            return True
            
        except Exception as e:
            return self.handle_critical_error(e, "Game Window Check")
    
    def check_roi_config(self) -> bool:
        """Check if ROI configuration exists and is valid."""
        try:
            from roi_capture import load_roi_config
            config = load_roi_config()
            
            required_rois = ["left_board", "right_board", "next_queue_left", "next_queue_right"]
            missing_rois = [roi for roi in required_rois if roi not in config]
            
            if missing_rois:
                self.handle_warning(
                    f"Missing ROI configurations: {', '.join(missing_rois)}. Please run calibrator.",
                    "ROI Configuration"
                )
                return False
            
            return True
            
        except Exception as e:
            return self.handle_critical_error(e, "ROI Configuration")
    
    def get_error_summary(self) -> str:
        """Get summary of all errors and warnings."""
        summary = []
        
        if self.critical_errors:
            summary.append("Critical Errors:")
            for error, trace in self.critical_errors:
                summary.append(f"  - {error}")
        
        if self.warnings:
            summary.append("Warnings:")
            for warning in self.warnings:
                summary.append(f"  - {warning}")
        
        if self.fallback_mode:
            summary.append("Running in fallback mode with reduced functionality.")
        
        return "\n".join(summary) if summary else "No errors reported."

# Global error handler instance
error_handler = OverlayErrorHandler()

def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    log.error("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
    error_handler.handle_critical_error(exc_value, "Uncaught Exception")

# Install global exception handler
sys.excepthook = handle_exception
