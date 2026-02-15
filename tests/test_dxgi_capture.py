import pytest


def test_dxgi_capture_basic():
    try:
        import dxgi_capture  # noqa: F401
    except ImportError:
        pytest.skip("DXGI not available")


def test_dxgi_initialize():
    try:
        import dxgi_capture
    except ImportError:
        pytest.skip("DXGI not available")

    grabber = dxgi_capture.FrameGrabber()
    result = grabber.initialize()
    assert isinstance(result, bool)
