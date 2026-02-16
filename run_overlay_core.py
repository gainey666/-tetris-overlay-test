import datetime
import logging
import sys
import threading

import keyboard  # type: ignore

from tetris_overlay_core import run_overlay, toggle_overlay, reset_calibration
from overlay_renderer import OverlayRenderer
from tools.calibration.calibration_ui import start_calibration
from dual_capture import DualScreenCapture
from roi_calibrator import start_calibrator
from shared_ui_capture import capture_shared_ui
from next_queue_capture import capture_next_queue
from logger_config import setup_telemetry_logger

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

LOGGER = setup_telemetry_logger()
FRAME_COUNTER = 0

# Add hotkey for new calibrator
keyboard.add_hotkey('ctrl+alt+c', lambda: start_calibrator())


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
    mask_binary = np.where(mask_resized > 127, 1, 0).astype(np.uint8)
    
    return mask_binary


def process_frames():
    global FRAME_COUNTER
    left_img, right_img = DualScreenCapture().grab()
    left_board = extract_board(left_img)
    right_board = extract_board(right_img)
    shared = capture_shared_ui()
    queue_images = capture_next_queue()

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


def _graceful_exit():
    logging.info("Esc pressed – shutting down")
    from tetris_overlay_core import graceful_exit
    graceful_exit()


# Initialize renderer after core setup
renderer = OverlayRenderer()

logging.info("Overlay core initializing – press Esc to exit")

# Start the core overlay system with renderer and calibration
run_overlay(renderer=renderer, calibration_func=start_calibration)
