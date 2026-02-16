"""
Regression tests for Tetris Overlay - Sprint 5 requirements
Tests for:
1. Negative monitor coordinates handling
2. Singleton lock enforcement
3. Screen capture edge cases
"""

import sys
import os
import tempfile
import threading
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from tetris_overlay_core import (
    ScreenCapture,
    _acquire_lock,
    _release_lock,
    window_filter,
)


class TestNegativeCoordinates:
    """Test handling of negative monitor coordinates."""

    def test_screen_capture_negative_coordinates(self):
        """Test ScreenCapture with negative coordinates (multi-monitor setup)."""
        # Test with negative left coordinate (monitor to the left of primary)
        try:
            capture = ScreenCapture((-1920, 0, 100, 100))
            # Should not raise an exception if monitor exists
            assert capture.region["left"] == -1920
            assert capture.region["top"] == 0
            assert capture.region["width"] == 100
            assert capture.region["height"] == 100
        except ValueError as e:
            # Expected if no monitor at that position
            assert "off-screen" in str(e)

    def test_screen_capture_negative_top(self):
        """Test ScreenCapture with negative top coordinate."""
        try:
            capture = ScreenCapture((0, -1080, 100, 100))
            assert capture.region["left"] == 0
            assert capture.region["top"] == -1080
        except ValueError as e:
            # Expected if no monitor at that position
            assert "off-screen" in str(e)

    def test_screen_capture_completely_offscreen(self):
        """Test ScreenCapture rejects completely off-screen regions."""
        with pytest.raises(ValueError, match="off-screen"):
            ScreenCapture((-5000, -5000, 100, 100))

    def test_screen_capture_partial_overlap(self):
        """Test ScreenCapture handles partial monitor overlap."""
        # This should work if there's a monitor that overlaps
        try:
            capture = ScreenCapture((-50, -50, 200, 200))
            # Should adjust to valid region or work if monitor exists
            assert capture.region["width"] > 0
            assert capture.region["height"] > 0
        except ValueError:
            # Acceptable if no monitor at that position
            pass


class TestSingletonLock:
    """Test singleton lock enforcement."""

    def test_singleton_lock_basic(self):
        """Test basic lock acquisition and release."""
        # Reset global state
        import tetris_overlay_core

        original_lock = tetris_overlay_core._LOCK_HANDLE
        tetris_overlay_core._LOCK_HANDLE = None

        try:
            _acquire_lock()
            assert tetris_overlay_core._LOCK_HANDLE is not None
            _release_lock()
            assert tetris_overlay_core._LOCK_HANDLE is None
        finally:
            # Restore original state
            if original_lock:
                tetris_overlay_core._LOCK_HANDLE = original_lock

    def test_singleton_lock_concurrent(self):
        """Test that only one instance can acquire the lock."""
        import tetris_overlay_core
        import subprocess
        import sys
        import time

        # Test using subprocess that holds the lock
        test_script = """
import sys
import time
sys.path.insert(0, r'{parent_dir}')
from tetris_overlay_core import _acquire_lock
try:
    _acquire_lock()
    print("SUCCESS")
    # Hold lock for 3 seconds
    time.sleep(3)
except SystemExit:
    print("FAILED")
""".format(parent_dir=str(Path(__file__).parent.parent))

        # Write test script to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(test_script)
            temp_script = f.name

        try:
            # Start first process that will hold the lock
            process1 = subprocess.Popen(
                [sys.executable, temp_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Give it time to acquire the lock
            time.sleep(1)

            # Try to start second process - should fail
            result2 = subprocess.run(
                [sys.executable, temp_script], capture_output=True, text=True, timeout=5
            )

            # Wait for first process to complete
            process1.wait(timeout=5)

            # First should succeed, second should fail
            assert process1.returncode == 0
            assert result2.returncode != 0 or "FAILED" in result2.stdout

        finally:
            os.unlink(temp_script)

    def test_lock_file_creation(self):
        """Test lock file is created in correct location."""
        import tetris_overlay_core

        original_lock = tetris_overlay_core._LOCK_HANDLE
        original_path = tetris_overlay_core._LOCK_PATH
        tetris_overlay_core._LOCK_HANDLE = None

        try:
            _acquire_lock()
            if os.name == "nt":
                expected_dir = os.getenv("TMP", ".")
                expected_name = "tetris_overlay.lock"
                assert tetris_overlay_core._LOCK_PATH == os.path.join(
                    expected_dir, expected_name
                )
            else:
                assert tetris_overlay_core._LOCK_PATH == "/tmp/tetris_overlay.lock"

            assert os.path.exists(tetris_overlay_core._LOCK_PATH)

        finally:
            _release_lock()
            tetris_overlay_core._LOCK_HANDLE = original_lock
            tetris_overlay_core._LOCK_PATH = original_path


class TestWindowFilter:
    """Test window filtering functionality."""

    def test_window_filter_no_win32gui(self):
        """Test window filter gracefully handles missing win32gui."""
        import tetris_overlay_core

        original_win32gui = tetris_overlay_core.win32gui
        tetris_overlay_core.win32gui = None

        try:
            results = window_filter()
            assert isinstance(results, dict)
            assert len(results) == 0
        finally:
            tetris_overlay_core.win32gui = original_win32gui

    def test_window_filter_with_win32gui(self):
        """Test window filter with win32gui available."""
        results = window_filter()
        assert isinstance(results, dict)
        # Should find windows or return empty dict
        for hwnd, score in results.items():
            assert isinstance(hwnd, int)
            assert isinstance(score, int)
            assert score in [0, 1]  # Binary scoring


class TestScreenCaptureEdgeCases:
    """Test ScreenCapture edge cases and error handling."""

    def test_invalid_rect_format(self):
        """Test ScreenCapture rejects invalid rect format."""
        with pytest.raises(ValueError, match="rect must be a"):
            ScreenCapture((0, 0, 100))  # Missing height

        with pytest.raises(ValueError, match="rect must be a"):
            ScreenCapture((0, 0, 100, 100, 50))  # Too many values

    def test_zero_size_capture(self):
        """Test ScreenCapture handles zero-sized regions."""
        with pytest.raises(ValueError, match="off-screen"):
            ScreenCapture((0, 0, 0, 100))  # Zero width

        with pytest.raises(ValueError, match="off-screen"):
            ScreenCapture((0, 0, 100, 0))  # Zero height

    def test_very_large_capture(self):
        """Test ScreenCapture handles very large regions."""
        # Should work or gracefully fail
        try:
            capture = ScreenCapture((0, 0, 10000, 10000))
            assert capture.region["width"] == 10000
            assert capture.region["height"] == 10000
        except ValueError:
            # Acceptable if region exceeds monitor bounds
            pass


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
