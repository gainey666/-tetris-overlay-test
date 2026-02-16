"""PredictionAgent should convert a mask into a non-empty list of dummy pieces."""

from unittest.mock import MagicMock

import numpy as np

from src.agents.prediction_agent import PredictionAgent


def test_fake_prediction_returns_something():
    mask = np.zeros((10, 20), dtype=np.uint8)
    mask[1, 3] = 255
    mask[4, 12] = 255
    mask[7, 0] = 255

    dummy_processor = MagicMock()
    dummy_processor.mask_queue.get.return_value = mask

    pred_agent = PredictionAgent(board_processor=dummy_processor)
    predictions = pred_agent._fake_predict(mask)

    assert len(predictions) == 3
    for row, col, piece in predictions:
        assert 0 <= row < 10
        assert 0 <= col < 20
        assert isinstance(piece, str) and len(piece) == 1
