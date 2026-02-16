"""UI integration tests for the Tetris overlay."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest
from sqlmodel import select

from ui.settings_dialog import SettingsDialog
from ui.stats_dashboard import StatsDashboard
from ui.settings_storage import save as save_settings, load as load_settings
from ui.settings import Settings, GhostStyle


@pytest.fixture
def app():
    """Create QApplication for tests."""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app
    app.quit()


@pytest.fixture
def temp_settings_file():
    """Create temporary settings file for tests."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
    
    # Mock the settings storage path
    import ui.settings_storage
    original_path = ui.settings_storage.DB_PATH
    ui.settings_storage.DB_PATH = temp_path
    
    yield temp_path
    
    # Restore original path
    ui.settings_storage.DB_PATH = original_path
    if temp_path.exists():
        temp_path.unlink()


class TestSettingsDialog:
    """Test the settings dialog functionality."""
    
    def test_dialog_creation(self, app):
        """Test that settings dialog can be created."""
        dialog = SettingsDialog()
        assert dialog is not None
        assert dialog.windowTitle() == "Tetris Overlay – Settings"
        dialog.close()
    
    def test_dialog_tabs_exist(self, app):
        """Test that all expected tabs are present."""
        dialog = SettingsDialog()
        tabs = dialog.tabs
        
        expected_tabs = ["General", "Ghost", "Hotkeys", "Visual Flags"]
        actual_tabs = [tabs.tabText(i) for i in range(tabs.count())]
        
        for tab in expected_tabs:
            assert tab in actual_tabs
        
        dialog.close()
    
    def test_settings_load_and_display(self, app, temp_settings_file):
        """Test that settings are loaded and displayed correctly."""
        # Create custom settings
        custom_settings = Settings()
        custom_settings.roi_left = (100, 200, 640, 360)
        custom_settings.ghost.colour = (10, 20, 30)
        custom_settings.ghost.opacity = 0.7
        custom_settings.show_combo = False
        
        # Save settings
        save_settings(custom_settings)
        
        # Create dialog and check values
        dialog = SettingsDialog()
        
        # Check ROI values
        assert dialog.left_roi_edit.text() == "100,200,640,360"
        
        # Check ghost style
        assert dialog.opacity_slider.value() == 70  # 0.7 * 100
        
        # Check visual flags
        assert not dialog.combo_chk.isChecked()
        
        dialog.close()
    
    def test_settings_save_and_emit_signal(self, app, temp_settings_file):
        """Test that settings are saved and signal is emitted."""
        dialog = SettingsDialog()
        
        # Mock the signal receiver
        signal_received = []
        def on_settings_changed(settings):
            signal_received.append(settings)
        
        dialog.settings_changed.connect(on_settings_changed)
        
        # Change some settings
        dialog.left_roi_edit.setText("50,60,640,360")
        dialog.opacity_slider.setValue(80)
        
        # Apply changes
        dialog._apply()
        
        # Check signal was emitted
        assert len(signal_received) == 1
        new_settings = signal_received[0]
        
        # Check values were saved
        assert new_settings.roi_left == (50, 60, 640, 360)
        assert new_settings.ghost.opacity == 0.8
        
        # Verify file was saved
        loaded_settings = load_settings()
        assert loaded_settings.roi_left == (50, 60, 640, 360)
        
        dialog.close()
    
    def test_reset_to_defaults(self, app, temp_settings_file):
        """Test reset to defaults functionality."""
        # Create non-default settings
        custom_settings = Settings()
        custom_settings.roi_left = (999, 999, 999, 999)
        custom_settings.ghost.colour = (1, 2, 3)
        save_settings(custom_settings)
        
        # Create dialog
        dialog = SettingsDialog()
        
        # Verify custom settings are loaded
        assert dialog.left_roi_edit.text() == "999,999,999,999"
        
        # Mock the confirmation dialog to always say "Yes"
        with patch('PySide6.QtWidgets.QMessageBox.question', return_value=QMessageBox.Yes):
            # Reset to defaults
            dialog._reset_to_defaults()
        
        # Check values were reset
        assert dialog.left_roi_edit.text() == "0,0,640,360"
        
        dialog.close()
    
    def test_invalid_roi_input(self, app):
        """Test handling of invalid ROI input."""
        dialog = SettingsDialog()
        
        # Enter invalid ROI
        dialog.left_roi_edit.setText("invalid,input")
        
        # Try to apply - should show warning and not crash
        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog._apply()
            mock_warning.assert_called_once()
        
        dialog.close()


class TestStatsDashboard:
    """Test the statistics dashboard functionality."""
    
    def test_dashboard_creation(self, app):
        """Test that stats dashboard can be created."""
        dashboard = StatsDashboard()
        assert dashboard is not None
        assert dashboard.windowTitle() == "Tetris Overlay - Statistics"
        dashboard.close()
    
    def test_dashboard_components_exist(self, app):
        """Test that all expected components are present."""
        dashboard = StatsDashboard()
        
        # Check for match table
        assert hasattr(dashboard, 'match_table')
        
        # Check for charts (they should exist even if empty)
        assert hasattr(dashboard, 'score_chart')
        assert hasattr(dashboard, 'combo_chart')
        assert hasattr(dashboard, 'piece_chart')
        
        dashboard.close()
    
    @patch('stats.db.get_session')
    def test_data_loading(self, app, mock_session):
        """Test that dashboard loads data correctly."""
        # Mock database session
        mock_session.return_value.__enter__.return_value.query.return_value.all.return_value = []
        
        dashboard = StatsDashboard()
        
        # The dashboard should load without crashing even with empty data
        dashboard.load_data()
        
        dashboard.close()


class TestErrorHandling:
    """Test error handling in UI components."""
    
    def test_settings_dialog_error_recovery(self, app):
        """Test that settings dialog recovers from errors."""
        dialog = SettingsDialog()
        
        # Simulate an error during settings save
        with patch('ui.settings_storage.save', side_effect=Exception("Save failed")):
            # Should not crash
            with patch('PySide6.QtWidgets.QMessageBox.warning'):
                dialog._apply()
        
        dialog.close()
    
    def test_dashboard_error_recovery(self, app):
        """Test that stats dashboard recovers from errors."""
        dashboard = StatsDashboard()
        
        # Simulate database error
        with patch('stats.db.get_session', side_effect=Exception("DB failed")):
            # Should not crash
            dashboard.load_data()
        
        dashboard.close()


class TestUIIntegration:
    """Test integration between UI components."""
    
    def test_settings_change_updates_overlay(self, app, temp_settings_file):
        """Test that settings changes properly update overlay components."""
        dialog = SettingsDialog()
        
        # Mock the overlay renderer
        with patch('overlay_renderer.OverlayRenderer') as mock_renderer:
            mock_instance = mock_renderer.return_value
            mock_instance.update_ghost_style = Mock()
            
            # Change ghost settings
            dialog.opacity_slider.setValue(90)
            dialog._apply()
            
            # Check overlay was updated
            mock_instance.update_ghost_style.assert_called_once()
        
        dialog.close()
    
    def test_hotkey_changes_are_applied(self, app, temp_settings_file):
        """Test that hotkey changes are properly registered."""
        dialog = SettingsDialog()
        
        # Mock keyboard module
        with patch('keyboard.add_hotkey') as mock_add_hotkey:
            # Change hotkey
            dialog.toggle_edit.setKeySequence('f8')
            dialog._apply()
            
            # Check hotkey was re-registered
            assert mock_add_hotkey.called
        
        dialog.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
