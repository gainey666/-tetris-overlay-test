"""Validate that BoardProcessorAgent creates a binary mask."""
import numpy as np

from src.agents.board_processor_agent import BoardProcessorAgent
from src.agents.capture_agent import CaptureAgent


def test_board_processor_creates_binary_mask(dummy_frame):
    cap = CaptureAgent()
    cap.frame_queue.put_nowait(dummy_frame)

    processor = BoardProcessorAgent(capture_agent=cap, board_width=20, board_height=10)
    mask = processor._create_mask(dummy_frame)

    assert mask.shape == (10, 20)
    assert mask.dtype == np.uint8
    unique_vals = np.unique(mask)
    assert set(unique_vals.tolist()).issubset({0, 255})
    assert 255 in unique_vals
