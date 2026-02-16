import unittest
import sys, pathlib

sys.path.append(str(pathlib.Path(__file__).parents[1] / "src"))


class SmokeTest(unittest.TestCase):
    def test_imports(self):
        from src.agents.synthetic_capture_agent import SyntheticCaptureAgent
        from src.agents.board_extractor_agent import BoardExtractorAgent
        from src.agents.prediction_agent_mock_perfect import PredictionAgent


if __name__ == "__main__":
    unittest.main()
