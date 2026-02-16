def test_load_prediction_agent():
    from run_overlay_core import load_prediction_agent
    agent = load_prediction_agent("mock")
    assert agent is not None

def test_roi_to_binary_matrix():
    import numpy as np
    from run_overlay_core import roi_to_binary_matrix
    dummy = np.zeros((100, 200, 3), dtype=np.uint8)
    mat = roi_to_binary_matrix(dummy)
    assert mat.shape == (20, 10)
