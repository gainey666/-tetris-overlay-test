import datetime
import json
import logging
import sys
import threading
import time
from pathlib import Path
from typing import Dict, Any

import keyboard  # type: ignore
import pygame

from tetris_overlay_core import run_overlay, toggle_overlay, reset_calibration
from overlay_renderer import OverlayRenderer
from tools.calibration.calibration_ui import start_calibration
from dual_capture import DualScreenCapture
from roi_calibrator import start_calibrator
from shared_ui_capture import capture_shared_ui
from next_queue_capture import capture_next_queue
from piece_detector import get_current_piece
from logger_config import setup_telemetry_logger

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

LOGGER = setup_telemetry_logger()
FRAME_COUNTER = 0

# Create global overlay renderer instance
overlay_renderer = OverlayRenderer()

# Add hotkey for new calibrator
keyboard.add_hotkey("ctrl+alt+c", lambda: start_calibrator())


def load_prediction_agent(agent_name: str) -> Any:
    """Dynamically import and instantiate a prediction agent."""
    if agent_name == "dellacherie":
        from src.agents.prediction_agent_dellacherie import PredictionAgent
        return PredictionAgent()
    elif agent_name == "onnx":
        from src.agents.prediction_agent_onnx import PredictionAgent
        return PredictionAgent()
    elif agent_name == "simple":
        from src.agents.prediction_agent_simple import PredictionAgent
        return PredictionAgent()
    elif agent_name == "mock":
        from src.agents.prediction_agent_mock_perfect import PredictionAgent
        return PredictionAgent()
    else:
        raise ValueError(f"Unknown prediction_agent: {agent_name}")


# Load prediction agent from config
CONFIG_PATH = Path("config/config.json")
if CONFIG_PATH.is_file():
    cfg = json.loads(CONFIG_PATH.read_text())
    prediction_agent_name = cfg.get("prediction_agent", "dellacherie")
else:
    prediction_agent_name = "dellacherie"

prediction_agent = load_prediction_agent(prediction_agent_name)


def roi_to_binary_matrix(roi_image):
    """Convert an ROI image to a 20×10 binary matrix (naive stub)."""
    import cv2
    import numpy as np

    gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (10, 20), interpolation=cv2.INTER_NEAREST)
    _, binary = cv2.threshold(small, 127, 255, cv2.THRESH_BINARY)
    return binary


def extract_board(image):
    """Extract board state from PIL Image using existing board processing logic."""
    import numpy as np
    import cv2

    # Convert PIL to numpy array
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Use existing board processing logic
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    mask_resized = cv2.resize(thresh, (10, 20), interpolation=cv2.INTER_NEAREST)
    mask_binary = np.where(mask_resized > 0, 255, 0).astype(np.uint8)

    return mask_binary


def process_frames():
    global FRAME_COUNTER
    left_img, right_img = DualScreenCapture().grab()
    left_board = extract_board(left_img)
    right_board = extract_board(right_img)
    shared = capture_shared_ui()
    queue_images = capture_next_queue()

    # Get current piece from queue (fallback to "T" if detection fails)
    current_piece = get_current_piece() or "T"

    # Predict for left board with actual current piece
    pred = prediction_agent.handle({"board": left_board, "piece": current_piece, "orientation": 0})

    # Draw ghost on overlay (reuse global renderer instance)
    if overlay_renderer.visible:
        # Extract piece type from prediction if available, otherwise use detected piece
        piece_type = pred.get("piece", current_piece)
        overlay_renderer.draw_ghost(overlay_renderer.screen, pred["target_col"], pred["target_rot"], piece_type)
        pygame.display.flip()

    LOGGER.info(
        {
            "ts": datetime.datetime.utcnow().isoformat(),
            "frame_id": FRAME_COUNTER,
            "score_w": shared["score"].size[0],
            "score_h": shared["score"].size[1],
            "wins_w": shared["wins"].size[0],
            "wins_h": shared["wins"].size[1],
            "timer_w": shared["timer"].size[0],
            "timer_h": shared["timer"].size[1],
            "queue_len": len(queue_images),
        }
    )
    FRAME_COUNTER += 1

    # Simple processing without complex agents for now
    print(
        "Processed boards - Left: %s, Right: %s, Shared: %s, Queue len: %d"
        % (left_board.shape, right_board.shape, list(shared.keys()), len(queue_images))
    )
    logging.info("Dual board processing successful")


def _toggle_logging():
    root = logging.getLogger()
    if root.level == logging.DEBUG:
        root.setLevel(logging.INFO)
        logging.info("Debug logging OFF")
    else:
        root.setLevel(logging.DEBUG)
        logging.debug("Debug logging ON")


def _frame_loop():
    """Main frame processing loop - runs in separate thread."""
    while True:
        try:
            process_frames()
            time.sleep(1/30)  # Target 30 FPS
        except Exception as e:
            LOGGER.error(f"Error in frame loop: {e}")
            time.sleep(0.1)  # Prevent tight error loop


def _graceful_exit():
    logging.info("Esc pressed – shutting down")
    from tetris_overlay_core import graceful_exit
    graceful_exit()


if __name__ == "__main__":
    # Start frame processing thread
    threading.Thread(target=_frame_loop, daemon=True).start()
    
    # Run the main overlay loop
    run_overlay()
