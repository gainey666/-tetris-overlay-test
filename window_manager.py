import ctypes
import json
import logging
import os
import re
from pathlib import Path

try:
    import win32gui  # type: ignore
except ImportError:  # pragma: no cover
    win32gui = None

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"
MIN_ROI_SIZE = 50
BLACKLIST = set()
_PATTERN = re.compile(r"Tetris\s*\d+", re.IGNORECASE)


def load_cache() -> dict:
    if not CONFIG_PATH.exists():
        data = {"hwnd": 0, "roi": [0, 0, 640, 360]}
        CONFIG_PATH.write_text(json.dumps(data, indent=2))
        return data
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if "roi" in data:
        data["roi"] = clamp_roi(data["roi"])
    return data


def save_cache(hwnd: int, roi: list) -> None:
    data = {"hwnd": int(hwnd), "roi": clamp_roi(roi)}
    CONFIG_PATH.write_text(json.dumps(data, indent=2))
    logging.info("Cache saved for hwnd=%s", hwnd)


def _virtual_screen_bounds() -> dict:
    """Return the virtual screen bounding box (left, top, width, height)."""
    if os.name != "nt":
        # Fallback: assume single monitor using pygame/mss later.
        return {"left": 0, "top": 0, "width": 8_192, "height": 8_192}
    user32 = ctypes.windll.user32
    try:
        user32.SetProcessDPIAware()
    except AttributeError:
        pass
    left = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
    top = user32.GetSystemMetrics(77)   # SM_YVIRTUALSCREEN
    width = user32.GetSystemMetrics(78) # SM_CXVIRTUALSCREEN
    height = user32.GetSystemMetrics(79)# SM_CYVIRTUALSCREEN
    return {"left": left, "top": top, "width": width, "height": height}


def clamp_roi(roi: list | tuple) -> list:
    """Clamp ROI to virtual screen bounds and enforce minimum size."""
    bounds = _virtual_screen_bounds()
    left, top, width, height = [int(x) for x in roi]
    right = left + width
    bottom = top + height
    bounds_left = bounds["left"]
    bounds_top = bounds["top"]
    bounds_right = bounds_left + bounds["width"]
    bounds_bottom = bounds_top + bounds["height"]

    left = max(bounds_left, min(left, bounds_right - 1))
    top = max(bounds_top, min(top, bounds_bottom - 1))
    right = max(left + MIN_ROI_SIZE, min(right, bounds_right))
    bottom = max(top + MIN_ROI_SIZE, min(bottom, bounds_bottom))

    return [left, top, right - left, bottom - top]


def score_window(hwnd: int) -> int:
    if not win32gui:
        return 0
    title = win32gui.GetWindowText(hwnd)
    return 1 if _PATTERN.search(title or "") else 0


def _enum_windows():
    windows = []

    def _cb(hwnd, _):
        if hwnd in BLACKLIST:
            return
        windows.append(hwnd)

    if win32gui:
        win32gui.EnumWindows(_cb, None)
    else:
        logging.warning("win32gui unavailable; cannot enumerate windows")
    return windows


def get_active_tetris_hwnd():
    best_hwnd = None
    best_score = 0
    for hwnd in _enum_windows():
        score = score_window(hwnd)
        if score > best_score:
            best_hwnd = hwnd
            best_score = score
    if best_hwnd:
        logging.info("Selected Tetris hwnd=%s score=%s", best_hwnd, best_score)
    return best_hwnd


__all__ = [
    "BLACKLIST",
    "load_cache",
    "save_cache",
    "score_window",
    "get_active_tetris_hwnd",
]
