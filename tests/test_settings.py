"""Tests for settings functionality."""

import pytest
import tempfile
from pathlib import Path
from ui.settings import Settings, GhostStyle, Hotkeys
from ui.settings_storage import save, load


def test_settings_roundtrip(tmp_path):
    """Test that settings can be saved and loaded correctly."""
    # Create custom settings
    s = Settings()
    s.roi_left = (100, 200, 640, 360)
    s.roi_right = (200, 300, 640, 360)
    s.prediction_agent = "onnx"
    s.ghost.colour = (10, 20, 30)
    s.ghost.opacity = 0.7
    s.show_combo = False
    s.show_b2b = True
    
    # Temporarily change the DB path
    from ui import settings_storage
    original_path = settings_storage.DB_PATH
    settings_storage.DB_PATH = tmp_path / "test_settings.json"
    
    try:
        # Save and load
        save(s)
        loaded = load()
        
        # Verify all fields
        assert loaded.roi_left == s.roi_left
        assert loaded.roi_right == s.roi_right
        assert loaded.prediction_agent == s.prediction_agent
        assert loaded.ghost.colour == s.ghost.colour
        assert loaded.ghost.opacity == s.ghost.opacity
        assert loaded.show_combo == s.show_combo
        assert loaded.show_b2b == s.show_b2b
        
    finally:
        # Restore original path
        settings_storage.DB_PATH = original_path


def test_settings_defaults():
    """Test that default settings are created correctly."""
    s = Settings()
    
    assert s.roi_left == (0, 0, 640, 360)
    assert s.roi_right == (0, 0, 640, 360)
    assert s.prediction_agent == "dellacherie"
    assert s.ghost.colour == (255, 255, 255)
    assert s.ghost.opacity == 0.5
    assert s.show_combo == True
    assert s.show_b2b == True


def test_settings_to_dict():
    """Test settings serialization to dictionary."""
    s = Settings()
    s.roi_left = (1, 2, 3, 4)
    s.ghost.colour = (10, 20, 30)
    
    d = s.to_dict()
    
    assert isinstance(d, dict)
    assert d["roi_left"] == [1, 2, 3, 4]
    assert d["prediction_agent"] == "dellacherie"
    assert d["ghost"]["colour"] == [10, 20, 30]
    assert d["ghost"]["opacity"] == 0.5


def test_settings_from_dict():
    """Test settings deserialization from dictionary."""
    data = {
        "roi_left": [10, 20, 30, 40],
        "roi_right": [50, 60, 70, 80],
        "prediction_agent": "simple",
        "ghost": {"colour": [100, 150, 200], "opacity": 0.8},
        "hotkeys": {"toggle_overlay": "f8"},
        "show_combo": False,
        "show_b2b": True
    }
    
    s = Settings.from_dict(data)
    
    assert s.roi_left == (10, 20, 30, 40)
    assert s.roi_right == (50, 60, 70, 80)
    assert s.prediction_agent == "simple"
    assert s.ghost.colour == (100, 150, 200)
    assert s.ghost.opacity == 0.8
    assert s.show_combo == False
    assert s.show_b2b == True


def test_ghost_style_defaults():
    """Test GhostStyle default values."""
    gs = GhostStyle()
    assert gs.colour == (255, 255, 255)
    assert gs.opacity == 0.5


def test_hotkeys_defaults():
    """Test Hotkeys default values."""
    hk = Hotkeys()
    assert hk.toggle_overlay == "f9"
    assert hk.open_settings == "f1"
    assert hk.open_stats == "ctrl+alt+s"
    assert hk.quit == "esc"
