"""End-to-end tests with mocked screen capture."""

import numpy as np
import pytest
from unittest.mock import Mock, patch
import pygame


def test_full_overlay_pipeline():
    """Test the complete pipeline with mocked screen capture."""
    # Mock pygame to avoid display issues in CI
    with patch('pygame.display.set_mode'), \
         patch('pygame.display.flip'), \
         patch('pygame.Surface'):
        
        # Mock screen capture
        with patch('run_overlay_core.DualScreenCapture') as mock_capture:
            # Create fake screen captures
            fake_left = Mock()
            fake_right = Mock()
            mock_capture.return_value.grab.return_value = (fake_left, fake_right)
            
            # Mock the image processing
            with patch('run_overlay_core.extract_board') as mock_extract:
                # Return a 20x10 board matrix with some blocks
                mock_board = np.zeros((20, 10), dtype=np.uint8)
                mock_board[0:5, 3:7] = 255  # Some filled blocks
                mock_extract.return_value = mock_board
                
                # Mock other captures
                with patch('run_overlay_core.capture_shared_ui') as mock_shared, \
                     patch('run_overlay_core.capture_next_queue') as mock_queue:
                    
                    mock_shared.return_value = {
                        "score": Mock(size=[100, 30]),
                        "wins": Mock(size=[80, 20]),
                        "timer": Mock(size=[60, 25])
                    }
                    mock_queue.return_value = []
                    
                    # Import and test the frame processing
                    from run_overlay_core import process_frames, prediction_agent
                    
                    # This should not raise any exceptions
                    try:
                        process_frames()
                        # Verify prediction agent was called with correct data
                        assert mock_extract.call_count == 2  # Left and right boards
                    except Exception as e:
                        pytest.fail(f"process_frames() raised {e}")


def test_prediction_agent_integration():
    """Test that prediction agents work with the expected data format."""
    from run_overlay_core import load_prediction_agent
    
    # Test each agent type
    for agent_name in ["mock", "simple", "dellacherie"]:
        agent = load_prediction_agent(agent_name)
        assert agent is not None
        
        # Test with the expected board format (0/255 values)
        board = np.zeros((20, 10), dtype=np.uint8)
        board[0:5, 3:7] = 255
        
        try:
            result = agent.handle({
                "board": board,
                "piece": "T",
                "orientation": 0
            })
            
            # Verify result structure
            assert "target_col" in result
            assert "target_rot" in result
            assert isinstance(result["target_col"], int)
            assert isinstance(result["target_rot"], int)
            assert 0 <= result["target_col"] <= 9
            assert 0 <= result["target_rot"] <= 3
            
        except Exception as e:
            pytest.fail(f"Agent {agent_name} failed: {e}")


def test_roi_config_loading():
    """Test that ROI configuration loads correctly."""
    from dual_roi_manager import load_config
    
    config = load_config()
    assert isinstance(config, dict)
    assert "roi" in config
    assert isinstance(config["roi"], list)
    
    # Should have left and right board ROIs if calibrated
    if len(config["roi"]) >= 2:
        left_board, right_board = config["roi"][:2]
        assert isinstance(left_board, list) and len(left_board) == 4
        assert isinstance(right_board, list) and len(right_board) == 4


if __name__ == "__main__":
    # Run tests directly
    test_full_overlay_pipeline()
    test_prediction_agent_integration()
    test_roi_config_loading()
    print("All end-to-end tests passed!")
