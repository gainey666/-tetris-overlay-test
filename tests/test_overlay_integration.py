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
    # Verify the matrix uses 0/255 values (not 0/1)
    assert set(np.unique(mat)).issubset({0, 255})

def test_ghost_shape_rendering():
    import pygame
    from overlay_renderer import OverlayRenderer, PIECE_SHAPES
    pygame.init()
    
    # Test that all piece shapes are defined
    expected_pieces = ["I", "O", "T", "S", "Z", "J", "L"]
    for piece in expected_pieces:
        assert piece in PIECE_SHAPES
        assert len(PIECE_SHAPES[piece]) > 0
        # Each shape should have 4 blocks
        for shape in PIECE_SHAPES[piece]:
            assert len(shape) == 4
            # Each block should be a (x, y) coordinate
            for block in shape:
                assert isinstance(block, tuple) and len(block) == 2
    
    # Test ghost rendering doesn't crash
    renderer = OverlayRenderer()
    surface = pygame.Surface((300, 600), pygame.SRCALPHA)
    
    # Test normal ghost
    renderer.draw_ghost(surface, column=5, rotation=0, piece_type="T")
    
    # Test special move indicators
    renderer.draw_ghost(surface, column=3, rotation=1, piece_type="I", is_tspin=True)
    renderer.draw_ghost(surface, column=2, rotation=0, piece_type="O", is_b2b=True)
    renderer.draw_ghost(surface, column=4, rotation=2, piece_type="S", combo=3)
    
    pygame.quit()
