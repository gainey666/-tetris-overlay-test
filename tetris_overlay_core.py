import logging
import os
import sys
import re
import atexit
import threading

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

try:
    import win32gui  # type: ignore
except ImportError:  # pragma: no cover
    win32gui = None

try:
    import msvcrt  # type: ignore
except ImportError:  # pragma: no cover
    msvcrt = None

import keyboard  # type: ignore
import mss  # type: ignore
from PIL import Image  # type: ignore
from roi_calibrator import start_calibrator

BLACKLIST = set()
_LOCK_HANDLE = None
_LOCK_PATH = None
_HOTKEYS_REGISTERED = False
_OVERLAY_RENDERER = None
_CALIBRATION_FUNC = None


def window_filter():
    """Return {hwnd: score} for windows whose title matches the Tetris regex."""
    results = {}
    if win32gui is None:
        logging.warning("win32gui unavailable; skipping window filter.")
        return results

    pattern = re.compile(r"Tetris\s*\d+", re.IGNORECASE)

    def enum_cb(hwnd, _):
        if hwnd in BLACKLIST:
            return
        if win32gui:
            title = win32gui.GetWindowText(hwnd) or ""
        else:
            title = ""
        score = 1 if pattern.search(title) else 0
        if score:
            results[hwnd] = score

    win32gui.EnumWindows(enum_cb, None)
    return results


class ScreenCapture:
    """Capture a rectangle of the primary monitor using mss only."""

    def __init__(self, rect):
        if len(rect) != 4:
            raise ValueError("rect must be a (left, top, width, height) tuple")
        left, top, width, height = rect
        self.region = {"left": left, "top": top, "width": width, "height": height}
        self.sct = mss.mss()
        monitor = self.sct.monitors[1]
        right = left + width
        bottom = top + height
        mon_left = monitor["left"]
        mon_top = monitor["top"]
        mon_right = mon_left + monitor["width"]
        mon_bottom = mon_top + monitor["height"]
        if right <= mon_left or bottom <= mon_top or left >= mon_right or top >= mon_bottom:
            raise ValueError("Capture region lies completely off-screen")

    def grab(self):
        shot = self.sct.grab(self.region)
        return Image.frombytes("RGB", shot.size, shot.rgb)


def _release_lock():
    global _LOCK_HANDLE
    if not _LOCK_HANDLE:
        return
    try:
        if os.name == "nt" and msvcrt:
            msvcrt.locking(_LOCK_HANDLE.fileno(), msvcrt.LK_UNLCK, 1)
        elif os.name != "nt":
            import fcntl

            fcntl.flock(_LOCK_HANDLE, fcntl.LOCK_UN)
        _LOCK_HANDLE.close()
        logging.info("Overlay lock released.")
    except Exception as exc:  # pragma: no cover
        logging.error(f"Error releasing lock: {exc}")
    finally:
        _LOCK_HANDLE = None


def _acquire_lock():
    global _LOCK_HANDLE, _LOCK_PATH
    if _LOCK_HANDLE:
        return
    if os.name == "nt" and msvcrt:
        _LOCK_PATH = os.path.join(os.getenv("TMP", "."), "tetris_overlay.lock")
        _LOCK_HANDLE = open(_LOCK_PATH, "w")
        try:
            msvcrt.locking(_LOCK_HANDLE.fileno(), msvcrt.LK_NBLCK, 1)
            logging.info("Overlay lock acquired.")
        except OSError:
            sys.exit("Another overlay instance is already running.")
    else:
        import fcntl

        _LOCK_PATH = "/tmp/tetris_overlay.lock"
        _LOCK_HANDLE = open(_LOCK_PATH, "w")
        try:
            fcntl.flock(_LOCK_HANDLE, fcntl.LOCK_EX | fcntl.LOCK_NB)
            logging.info("Overlay lock acquired.")
        except OSError:
            sys.exit("Another overlay instance is already running.")
    atexit.register(_release_lock)


def toggle_overlay():
    logging.info("F9 pressed – toggle overlay.")
    global _OVERLAY_RENDERER
    if _OVERLAY_RENDERER:
        _OVERLAY_RENDERER.toggle()


def reset_calibration():
    logging.info("F1 pressed – reset calibration.")
    global _CALIBRATION_FUNC
    if _CALIBRATION_FUNC:
        _CALIBRATION_FUNC()


def _toggle_debug_logging():
    root = logging.getLogger()
    if root.level == logging.DEBUG:
        root.setLevel(logging.INFO)
        logging.info("F2 pressed – debug logging OFF.")
    else:
        root.setLevel(logging.DEBUG)
        logging.debug("F2 pressed – debug logging ON.")


def graceful_exit():
    logging.info("Esc pressed – exiting.")
    _release_lock()
    sys.exit(0)


def _register_hotkeys():
    global _HOTKEYS_REGISTERED
    if _HOTKEYS_REGISTERED:
        return
    keyboard.add_hotkey("F9", toggle_overlay)
    keyboard.add_hotkey("F1", reset_calibration)
    keyboard.add_hotkey("F2", _toggle_debug_logging)
    keyboard.add_hotkey("esc", graceful_exit)
    keyboard.add_hotkey("ctrl+alt+c", start_calibrator)
    _HOTKEYS_REGISTERED = True
    logging.info("Hotkeys registered.")


def run_overlay(renderer=None, calibration_func=None):
    """Initialize and run the overlay system with optional renderer and calibration."""
    global _OVERLAY_RENDERER, _CALIBRATION_FUNC
    # Store references for hotkey callbacks
    _OVERLAY_RENDERER = renderer
    _CALIBRATION_FUNC = calibration_func
    
    _acquire_lock()
    _register_hotkeys()
    
    # Start renderer thread if provided
    if renderer:
        import threading
        threading.Thread(target=renderer.run_loop, daemon=True).start()
        logging.info("Renderer thread started")
    
    logging.info("Hotkey listener active – press Esc to quit.")
    keyboard.wait()


if __name__ == "__main__":
    run_overlay()
