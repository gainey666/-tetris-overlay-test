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
