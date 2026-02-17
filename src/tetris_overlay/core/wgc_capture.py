"""
Windows Graphics Capture (WGC) wrapper for non-blocking frame capture.
"""

import ctypes
import numpy as np
from typing import Optional, Tuple
import sys
from pathlib import Path

# Try to load the compiled DLL
DLL_PATH = Path(__file__).parent.parent / "capture_cpp" / "capture_cpp.dll"

_capture_dll = None
try:
    _capture_dll = ctypes.CDLL(str(DLL_PATH))
    print("✅ WGC Capture DLL loaded successfully")
except OSError as e:
    print(f"⚠️  Could not load capture_cpp.dll from {DLL_PATH}: {e}")
    print("📋 Will use BitBlt fallback (may cause game interference)")

# Define C function signatures only if DLL is available
if _capture_dll:
    class FrameGrabber(ctypes.Structure):
        pass

    # Function signatures
    _create_grabber = _capture_dll.CreateFrameGrabber
    _create_grabber.argtypes = [ctypes.c_void_p]  # HWND
    _create_grabber.restype = ctypes.POINTER(FrameGrabber)

    _destroy_grabber = _capture_dll.DestroyFrameGrabber
    _destroy_grabber.argtypes = [ctypes.POINTER(FrameGrabber)]
    _destroy_grabber.restype = None

    _try_get_frame = _capture_dll.TryGetFrame
    _try_get_frame.argtypes = [ctypes.POINTER(FrameGrabber), ctypes.c_void_p]  # ID3D11Texture2D*
    _try_get_frame.restype = ctypes.c_bool

    _get_frame_size = _capture_dll.GetFrameSize
    _get_frame_size.argtypes = [ctypes.POINTER(FrameGrabber), ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]
    _get_frame_size.restype = None

    _is_capturing = _capture_dll.IsCapturing
    _is_capturing.argtypes = [ctypes.POINTER(FrameGrabber)]
    _is_capturing.restype = ctypes.c_bool


class WGCFramerGrabber:
    """Python wrapper for Windows Graphics Capture."""
    
    def __init__(self, hwnd: int):
        if not _capture_dll:
            raise ImportError("WGC DLL not available")
        
        self.hwnd = hwnd
        self._grabber = None
        self._width = 0
        self._height = 0
        
        # Initialize capture
        self._grabber = _create_grabber(hwnd)
        
        if not _is_capturing(self._grabber):
            raise RuntimeError("Failed to start capture")
        
        # Get frame dimensions
        width = ctypes.c_uint()
        height = ctypes.c_uint()
        _get_frame_size(self._grabber, ctypes.byref(width), ctypes.byref(height))
        self._width = width.value
        self._height = height.value
        
        print(f"WGC Capture initialized: {self._width}x{self._height}")
    
    def __del__(self):
        if self._grabber and _capture_dll:
            _destroy_grabber(self._grabber)
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    def is_capturing(self) -> bool:
        """Check if capture is active."""
        return self._grabber is not None and _is_capturing(self._grabber)
    
    def try_get_frame(self) -> Optional[np.ndarray]:
        """
        Try to get the latest frame.
        Returns numpy array in BGRA format, or None if no new frame.
        """
        if not self.is_capturing():
            return None
        
        # Create a staging texture (this is a simplified approach)
        # In a real implementation, we'd need to properly handle D3D11 textures
        # For now, we'll use a fallback to BitBlt if WGC fails
        
        # This is a placeholder - the actual implementation would need
        # proper D3D11 texture handling which is complex in pure Python
        return None


def create_wgc_capture(hwnd: int) -> Optional[WGCFramerGrabber]:
    """Create a WGC capture instance."""
    try:
        return WGCFramerGrabber(hwnd)
    except Exception as e:
        print(f"Failed to create WGC capture: {e}")
        return None


# Fallback to BitBlt if WGC is not available
def create_capture(hwnd: int, prefer_wgc: bool = True) -> Optional['FrameGrabber']:
    """
    Create a frame grabber, preferring WGC if available.
    Falls back to BitBlt if WGC fails.
    """
    if prefer_wgc:
        wgc = create_wgc_capture(hwnd)
        if wgc:
            return wgc
        print("WGC failed, falling back to BitBlt")
    
    # Fallback to existing capture
    from .capture import grab_window
    return LegacyFrameGrabber(hwnd)


class LegacyFrameGrabber:
    """Fallback frame grabber using BitBlt."""
    
    def __init__(self, hwnd: int):
        self.hwnd = hwnd
        from .capture import bbox_from_hwnd
        self._rect = bbox_from_hwnd(hwnd)
        self._width = self._rect[2] - self._rect[0]
        self._height = self._rect[3] - self._rect[1]
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    def is_capturing(self) -> bool:
        return True
    
    def try_get_frame(self) -> Optional[np.ndarray]:
        """Get frame using BitBlt (blocking)."""
        try:
            from .capture import grab_window

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

            return grab_window(self.hwnd)
        except Exception:
            return None
