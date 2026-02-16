"""
DEPRECATED: This module has been superseded by the mss-based ScreenCapture in tetris_overlay_core.py

The new implementation:
- Uses mss only (no OpenCV/webcam)
- Handles negative monitor coordinates properly  
- Is consolidated in tetris_overlay_core.py
- Follows the project's no-webcam constraint

This file is kept for reference only. Use tetris_overlay_core.ScreenCapture instead.
"""

# For reference, here's what the new capture looks like:
# from tetris_overlay_core import ScreenCapture
# capture = ScreenCapture((left, top, width, height))
# image = capture.grab()
