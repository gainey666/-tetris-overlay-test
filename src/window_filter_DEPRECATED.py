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

"""
DEPRECATED: This module has been superseded by the consolidated window filtering in tetris_overlay_core.py

The new implementation:
- Uses win32gui directly with better error handling
- Is consolidated with singleton lock and hotkey management
- Follows the project's architectural consolidation goals

This file is kept for reference only. Use tetris_overlay_core.window_filter() instead.
"""

# For reference, here's what the new window filter looks like:
# from tetris_overlay_core import window_filter
# windows = window_filter()  # Returns {hwnd: score} dict
