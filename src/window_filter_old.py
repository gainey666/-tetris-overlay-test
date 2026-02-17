"""
Utility to locate the Tetris game window on the desktop and return its
screen offset (left, top, width, height).  The function uses the
``pygetwindow`` package, which works on Windows, macOS and Linux.

It is deliberately tiny – just enough for the overlay to turn the absolute
ROI values (saved by the calibration UI) into *window‑relative* ROI
coordinates.
"""

from __future__ import annotations

import time
from typing import Tuple, Optional

# ``pygetwindow`` is a small pure‑Python wrapper around the native Win32
# API on Windows.  It ships with a pure‑Python fallback for macOS /
# X11, so it does not add any heavy binary dependencies.
try:
    import pygetwindow as gw

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

except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "pygetwindow is required for window‑title filtering. "
        "Add it to requirements.txt (pip install pygetwindow)."
    ) from exc


def find_window(title_substring: str) -> Optional[Tuple[int, int, int, int]]:
    """
    Return ``(left, top, width, height)`` of the *first* visible window whose
    title contains ``title_substring`` (case‑insensitive).  If the window is
    minimized we restore it and bring it to the foreground.

    Handles window names with random numbers like "Tetris® Effect: Connected (3)".

    Parameters
    ----------
    title_substring:
        Sub‑string to search for – e.g. ``"tetris"``.

    Returns
    -------
    Optional[Tuple[int, int, int, int]]
        ``None`` if no matching window is found.
    """
    # ``gw.getAllTitles()`` returns a list of all known window titles.
    matching_windows = []

    for title in gw.getAllTitles():
        # Handle titles with random numbers like "Tetris® Effect: Connected (3)"
        # Strip the random number part for matching
        clean_title = title
        if "(" in title and ")" in title:
            # Remove the "(number)" part for matching
            clean_title = title[: title.rfind("(")].strip()

        if title_substring.lower() in clean_title.lower():
            # There may be several windows with the same title; we take the
            # first one.
            wins = gw.getWindowsWithTitle(title)
            for win in wins:
                # Skip minimized windows
                if win.isMinimized:
                    continue
                # Skip very small windows (likely overlays)
                if win.width < 200 or win.height < 200:
                    continue
                # Prioritize game windows (exclude editor windows)
                if any(
                    skip_word in title.lower()
                    for skip_word in ["windsurf", "visual studio", "code"]
                ):
                    continue
                matching_windows.append((title, win))

    # Sort by priority: prefer windows with "effect" or actual game names
    game_keywords = ["effect", "connected", "game", "play"]
    for keyword in game_keywords:
        for title, win in matching_windows:
            if keyword in title.lower():
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(0.05)
                return win.left, win.top, win.width, win.height

    # If no game windows found, return the first suitable window
    if matching_windows:
        title, win = matching_windows[0]
        if win.isMinimized:
            win.restore()
        win.activate()
        time.sleep(0.05)
        return win.left, win.top, win.width, win.height

    return None


if __name__ == "__main__":  # pragma: no cover
    # Simple sanity test you can run from a console:
    info = find_window("tetris")
    if info:
        print(f"Tetris window found at (left, top, w, h) = {info}")
    else:
        print("No window whose title contains 'tetris' was found.")
