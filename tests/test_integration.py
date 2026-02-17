"""Integration tests for the complete overlay system."""

import pytest
import numpy as np
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import the main modules
from run_overlay_core import (
    _frame_worker, _register_dynamic_hotkeys, 
    process_frames, overlay_renderer, CURRENT_SETTINGS
)
from ui.settings_dialog import SettingsDialog
from ui.stats_dashboard import StatsDashboard
from stats.service import stats_service
from tetromino_shapes import get_piece_shape


class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Mock all external dependencies."""
        mocks = {}
        
        # Mock screen capture
        mocks['dual_capture'] = Mock()
        mocks['dual_capture'].grab.return_value = Mock()
        
        # Mock pygame
        mocks['pygame'] = Mock()
        mocks['pygame'].display.set_mode.return_value = Mock()
        mocks['pygame'].event.get.return_value = []
        mocks['pygame'].QUIT = None
        
        # Mock keyboard
        mocks['keyboard'] = Mock()
        
        # Mock Qt application
        mocks['qapp'] = Mock()
        mocks['qapp'].instance.return_value = None
        
        return mocks
        
    def test_frame_worker_thread(self, mock_dependencies):
        """Test the frame worker thread functionality."""
        with patch('run_overlay_core.DualScreenCapture', mock_dependencies['dual_capture']):
            with patch('pygame.event.get', mock_dependencies['pygame'].event.get):
                with patch('pygame.QUIT', None):
                    with patch('time.sleep') as mock_sleep:
                        
                        # Mock the frame processing
                        with patch('run_overlay_core.process_frames') as mock_process:
                            mock_process.return_value = True
                            
                            # Create a stop event
                            stop_event = threading.Event()
                            
                            # Run frame worker for a short time
                            def worker():
                                _frame_worker(stop_event)
                                
                            thread = threading.Thread(target=worker)
                            thread.start()
                            
                            # Let it run briefly then stop
                            time.sleep(0.1)
                            stop_event.set()
                            thread.join(timeout=1.0)
                            
                            # Should have processed some frames
                            assert mock_process.called
                            
    def test_dynamic_hotkey_registration(self, mock_dependencies):
        """Test dynamic hotkey registration."""
        with patch('keyboard.add_hotkey') as mock_add:
            with patch('keyboard.clear'):
                
                _register_dynamic_hotkeys()
                
                # Should register hotkeys for all configured actions
                assert mock_add.called
                calls = mock_add.call_args_list
                
                # Check that common hotkeys are registered
                hotkey_strings = [call[0][0] for call in calls]
                assert any('f9' in hk.lower() for hk in hotkey_strings)  # Toggle overlay
                
    def test_settings_dialog_integration(self, mock_dependencies):
        """Test settings dialog integration with overlay."""
        with patch('ui.settings_dialog.QApplication.instance', mock_dependencies['qapp'].instance):
            with patch('ui.settings_dialog.QDialog.__init__', return_value=None):
                
                dialog = SettingsDialog()
                
                # Should have settings changed signal
                assert hasattr(dialog, 'settings_changed')
                
                # Should be able to get current settings
                settings = dialog.get_settings()
                assert settings is not None
                
    def test_stats_dashboard_integration(self, mock_dependencies):
        """Test statistics dashboard integration."""
        with patch('stats.service.stats_service.get_all_matches') as mock_get_matches:
            mock_get_matches.return_value = []
            
            with patch('ui.stats_dashboard.QApplication.instance', mock_dependencies['qapp'].instance):
                
                dashboard = StatsDashboard()
                
                # Should load data on initialization
                mock_get_matches.assert_called()
                
                # Should have refresh functionality
                assert hasattr(dashboard, '_load_data')
                
    def test_complete_overlay_loop(self, mock_dependencies):
        """Test the complete overlay processing loop."""
        # Mock all the components
        with patch('run_overlay_core.DualScreenCapture', mock_dependencies['dual_capture']):
            with patch('pygame.event.get', mock_dependencies['pygame'].event.get):
                with patch('pygame.QUIT', None):
                    with patch('overlay_renderer.OverlayRenderer.draw_ghost') as mock_draw:
                        with patch('stats.service.stats_service.record_frame') as mock_record:
                            
                            # Create mock board state
                            board = np.zeros((10, 20), dtype=int)
                            
                            # Mock the capture to return images
                            mock_dependencies['dual_capture'].grab.return_value = [
                                Mock(),  # Left image
                                Mock()   # Right image
                            ]
                            
                            # Run one frame
                            result = process_frames()
                            
                            # Should complete successfully
                            assert result is True
                            
    def test_settings_change_propagation(self, mock_dependencies):
        """Test that settings changes propagate to all components."""
        with patch('ui.current_settings.update') as mock_update:
            with patch('ui.settings_storage.save') as mock_save:
                with patch('run_overlay_core._register_dynamic_hotkeys') as mock_hotkeys:
                    
                    # Simulate settings change
                    from ui.settings import Settings
                    new_settings = Settings()
                    new_settings.ghost.colour = [255, 0, 0]
                    new_settings.ghost.opacity = 0.9
                    
                    # Trigger settings change handler
                    from run_overlay_core import _on_settings_changed
                    _on_settings_changed(new_settings)
                    
                    # Should update settings and re-register hotkeys
                    mock_update.assert_called_with(new_settings)
                    mock_hotkeys.assert_called()
                    
    def test_statistics_collection_integration(self, mock_dependencies):
        """Test statistics collection with frame processing."""
        with patch('stats.service.stats_service.record_frame') as mock_record:
            with patch('stats.service.stats_service.start_new_match') as mock_start:
                with patch('stats.service.stats_service.end_current_match') as mock_end:
                    
                    # Start a match
                    match_id = stats_service.start_match()
                    assert match_id is not None
                    mock_start.assert_called()
                    
                    # Record some frames
                    board = np.zeros((10, 20), dtype=int)
                    stats_service.record_frame(board, "T", 0, (4, 10), 100)
                    
                    # Should record the frame
                    mock_record.assert_called()
                    
                    # End the match
                    stats = stats_service.end_match()
                    mock_end.assert_called()
                    
    def test_ghost_rendering_with_shapes(self, mock_dependencies):
        """Test ghost rendering with real tetromino shapes."""
        with patch('pygame.display.flip'):
            with patch('ui.current_settings.get') as mock_get:
                mock_settings = Mock()
                mock_settings.show_combo = False
                mock_settings.show_b2b = False
                mock_settings.show_fps = False
                mock_get.return_value = mock_settings
                
                # Test all piece types
                board = np.zeros((10, 20), dtype=int)
                pieces = ["I", "O", "T", "S", "Z", "J", "L"]
                
                for piece in pieces:
                    for rotation in range(4):
                        # Should not raise any exceptions
                        overlay_renderer.draw_ghost(board, piece, rotation)
                        
                        # Verify shape is used correctly
                        shape = get_piece_shape(piece, rotation)
                        assert len(shape) == 4  # All tetrominos have 4 blocks
                        
    def test_error_handling_integration(self, mock_dependencies):
        """Test error handling across the integrated system."""
        with patch('run_overlay_core.error_handler.handle_exception') as mock_handle:
            with patch('run_overlay_core.DualScreenCapture') as mock_capture:
                
                # Make capture raise an exception
                mock_capture.side_effect = Exception("Capture failed")
                
                # Process frames should handle the error
                result = process_frames()
                
                # Should handle gracefully (return False or continue)
                assert isinstance(result, bool)
                
    def test_performance_monitoring_integration(self, mock_dependencies):
        """Test performance monitoring integration."""
        with patch('performance_monitor.performance_monitor.update') as mock_update:
            with patch('performance_monitor.performance_monitor.get_stats') as mock_stats:
                mock_stats.return_value = {
                    'fps': 30.0,
                    'avg_frame_time': 33.3,
                    'memory_usage': 1000000
                }
                
                # Should update performance monitor
                stats = performance_monitor.performance_monitor.get_stats()
                
                assert 'fps' in stats
                assert 'avg_frame_time' in stats
                assert 'memory_usage' in stats
                
    def test_feature_toggle_integration(self, mock_dependencies):
        """Test feature toggle integration."""
        with patch('feature_toggles.is_feature_enabled') as mock_feature:
            
            # Test feature enabled
            mock_feature.return_value = True
            assert is_feature_enabled('ghost_rendering') is True
            
            # Test feature disabled
            mock_feature.return_value = False
            assert is_feature_enabled('ghost_rendering') is False
            
    def test_database_integration(self, mock_dependencies):
        """Test database integration with statistics."""
        with patch('stats.db.get_session') as mock_session:
            mock_session.return_value.__enter__.return_value = Mock()
            
            # Should be able to get global stats
            stats = stats_service.get_global_stats()
            
            assert isinstance(stats, dict)
            assert 'total_matches' in stats
            assert 'total_frames' in stats
