"""Common fixtures for the test suite."""
import pytest
import numpy as np


@pytest.fixture(scope="session")
def dummy_frame():
    """Create a synthetic 640×480 BGR frame (gray with a white square)."""
    frame = np.full((480, 640, 3), 50, dtype=np.uint8)
    try:
        import cv2  # noqa: F401
    except ModuleNotFoundError:
        pytest.skip("cv2 not installed")
    return frame
