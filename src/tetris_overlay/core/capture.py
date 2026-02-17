"""
Screen capture functionality for Tetris Overlay.
"""

import cv2
import numpy as np
import win32gui
import win32ui
import win32con
import win32api
from typing import Tuple

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



def bbox_from_hwnd(hwnd: int) -> Tuple[int, int, int, int]:
@trace_calls('bbox_from_hwnd', 'capture.py', 30)
    """Get the bounding box of a window (left, top, right, bottom)."""
    rect = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = rect
    return left, top, right, bottom


def grab_window(hwnd: int) -> np.ndarray:
@trace_calls('grab_window', 'capture.py', 37)
    """Capture a window and return as numpy array (BGR format)."""
    left, top, right, bottom = bbox_from_hwnd(hwnd)
    width, height = right - left, bottom - top
    
    # Get window device context
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    
    # Create bitmap
    save_bitmap = win32ui.CreateBitmap()
    save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(save_bitmap)
    
    # BitBlt the window
    result = save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)
    
    # Get bitmap bits
    bmpinfo = save_bitmap.GetInfo()
    bmpstr = save_bitmap.GetBitmapBits(True)
    
    # Convert to numpy array
    img = np.frombuffer(bmpstr, dtype=np.uint8)
    img.shape = (height, width, 4)  # BGRA format
    
    # Convert BGRA to BGR
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    # Cleanup
    win32gui.DeleteObject(save_bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)
    
    return img


def capture_window_area(hwnd: int, x: int, y: int, width: int, height: int) -> np.ndarray:
@trace_calls('capture_window_area', 'capture.py', 75)
    """Capture a specific area of a window."""
    full_image = grab_window(hwnd)
    return full_image[y:y+height, x:x+width]
