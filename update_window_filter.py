#!/usr/bin/env python3
"""
Update window_filter.py with robust title matching
"""
import re
import pathlib

# Read the current window_filter.py
current_file = pathlib.Path("src/window_filter.py")
if current_file.exists():
    current_file.rename("src/window_filter_old.py")
    print("✅ Backed up current window_filter.py to window_filter_old.py")

# New robust window_filter.py content
new_content = '''"""
Utility to locate the Tetris game window on the desktop and return its
screen offset (left, top, width, height).  The function uses the
``pygetwindow`` package, which works on Windows, macOS and Linux.

It also copes with titles that contain a random "(nnn)" suffix – the
suffix is stripped before the substring match.
"""
from __future__ import annotations

import time
import re
from typing import Tuple, Optional

# ----------------------------------------------------------------------
# pygetwindow – a tiny cross‑platform wrapper around the native Win32 API.
# ----------------------------------------------------------------------
try:
    import pygetwindow as gw
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "pygetwindow is required for window‑title filtering. "
        "Install it with: pip install pygetwindow"
    ) from exc


def _clean_title(title: str) -> str:
    """Remove a trailing ``(number)`` from a window title."""
    # ``\\\\s*\\\\(\\\\d+\\\\)$`` matches an optional space and a parenthesised number at the end.
    return re.sub(r"\\s*\\(\\d+\\)$", "", title).strip()


def find_window(title_substring: str) -> Optional[Tuple[int, int, int, int]]:
    """
    Return ``(left, top, width, height)`` of the *first* visible window whose
    title (after stripping a trailing ``(nnn)``) contains ``title_substring``
    (case‑insensitive).  If the window is minimized we restore it and bring it
    to the foreground.

    Parameters
    ----------
    title_substring:
        Sub‑string to search for – e.g. ``"tetris"``.

    Returns
    -------
    Optional[Tuple[int, int, int, int]]
        ``None`` if no matching window is found.
    """
    for raw_title in gw.getAllTitles():
        clean = _clean_title(raw_title)

        if title_substring.lower() in clean.lower():
            wins = gw.getWindowsWithTitle(raw_title)
            for win in wins:
                if win.isMinimized:
                    continue
                if win.width < 200 or win.height < 200:
                    continue
                # Prioritize game windows (exclude editor windows)
                if any(skip_word in raw_title.lower() for skip_word in ['windsurf', 'visual studio', 'code']):
                    continue
                if win.isMinimized:
                    win.restore()
                win.activate()
                time.sleep(0.05)
                return win.left, win.top, win.width, win.height

    return None


def re_detect_window() -> Optional[Tuple[int, int, int, int]]:
    """
    Convenience wrapper that re‑detects the Tetris window.
    Useful when the window title changes (random number suffix) or the window
    is moved.
    """
    return find_window("tetris")


if __name__ == "__main__":   # pragma: no cover
    info = find_window("tetris")
    if info:
        print(f"Tetris window found at (left, top, w, h) = {info}")
    else:
        print("No window whose title contains 'tetris' was found.")
'''

# Write the new file
new_file = pathlib.Path("src/window_filter.py")
new_file.write_text(new_content, encoding="utf-8")
print("✅ Updated window_filter.py with robust title matching")
