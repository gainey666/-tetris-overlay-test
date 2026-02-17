"""Test that main module can be imported."""

def test_import_main():
    """Test that the main overlay module can be imported."""
    try:
        import run_overlay_core
        assert run_overlay_core is not None
    except ImportError as e:
        assert False, f"Failed to import main module: {e}"

def test_import_wizard():
    """Test that the wizard module can be imported."""
    try:
        import wizard
        assert wizard is not None
    except ImportError as e:
        assert False, f"Failed to import wizard module: {e}"
