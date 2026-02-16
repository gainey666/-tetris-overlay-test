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

from tetris_overlay_core import run_overlay, toggle_overlay, reset_calibration, graceful_exit
from overlay_renderer import OverlayRenderer
from tools.calibration.calibration_ui import start_calibration
from dual_capture import DualScreenCapture
from roi_calibrator import start_calibrator
from shared_ui_capture import capture_shared_ui
from next_queue_capture import capture_next_queue
from piece_detector import get_current_piece
from performance_monitor import performance_monitor
from logger_config import setup_telemetry_logger
from error_handler import error_handler
from feature_toggles import is_feature_enabled

# New imports for settings and stats
from ui.settings_storage import load as load_settings, save as save_settings
from ui.settings_dialog import SettingsDialog
from ui.stats_dashboard import StatsDashboard
from stats.db import init_db
from stats.collector import start_new_match, end_current_match, record_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

LOGGER = setup_telemetry_logger()
FRAME_COUNTER = 0

# Load settings
CURRENT_SETTINGS = load_settings()

# Perform startup checks
if not error_handler.check_dependencies():
    logging.error("Dependency check failed. Exiting.")
    sys.exit(1)

# Skip game window check for now - overlay will work without it
# if not error_handler.check_game_window():
#     logging.warning("No game window found. Will try fallback mode.")

if not error_handler.check_roi_config():
    logging.warning("ROI configuration incomplete. Please run calibrator.")

# Create global overlay renderer instance
overlay_renderer = OverlayRenderer()

# Initialize database
init_db()

# Start a new match
start_new_match(CURRENT_SETTINGS.prediction_agent)

def _toggle_logging():
    root = logging.getLogger()
    if root.level == logging.DEBUG:
        root.setLevel(logging.INFO)
        logging.info("Debug logging OFF")
    else:
        root.setLevel(logging.DEBUG)
        logging.debug("Debug logging ON")

def _graceful_exit():
    """Handle graceful exit with stats cleanup."""
    end_current_match()
    logging.info("Esc pressed – shutting down")
    from tetris_overlay_core import graceful_exit
    graceful_exit()

def _register_dynamic_hotkeys():
    """Register hotkeys based on current settings."""
    # Clear existing hotkeys
    try:
        keyboard.unhook_all()
    except:
        pass  # keyboard library might not have unhook_all
    
    hk = CURRENT_SETTINGS.hotkeys
    keyboard.add_hotkey(hk.toggle_overlay, toggle_overlay)
    keyboard.add_hotkey(hk.open_settings, _open_settings)
    keyboard.add_hotkey(hk.open_stats, _open_stats)
    keyboard.add_hotkey(hk.debug_logging, _toggle_logging)
    keyboard.add_hotkey(hk.quit, _graceful_exit)
    keyboard.add_hotkey(hk.calibrate, start_calibrator)

def _open_settings():
    """Open the settings dialog."""
    dialog = SettingsDialog()
    dialog.settings_changed.connect(_on_settings_changed)
    dialog.exec()

def _open_stats():
    """Open the statistics dashboard."""
    dashboard = StatsDashboard()
    dashboard.show()

def _on_settings_changed(new_settings):
    """Handle settings changes."""
    global CURRENT_SETTINGS
    CURRENT_SETTINGS = new_settings
    
    # Save settings to disk
    save_settings(new_settings)
    
    _register_dynamic_hotkeys()
    
    # Update overlay renderer with new ghost style
    overlay_renderer.update_ghost_style(
        colour=new_settings.ghost.colour,
        opacity=new_settings.ghost.opacity,
    )

# Register initial hotkeys
_register_dynamic_hotkeys()


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


# Load prediction agent based on settings
prediction_agent = load_prediction_agent(CURRENT_SETTINGS.prediction_agent)


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
    
    # Start performance monitoring
    performance_monitor.start_frame()
    capture_start_ts = time.time()
    
    try:
        left_img, right_img = DualScreenCapture().grab()
        left_board = extract_board(left_img)
        right_board = extract_board(right_img)
        shared = capture_shared_ui()
        queue_images = capture_next_queue()

    except Exception as e:
        # Handle screen capture errors gracefully
        if not error_handler.handle_critical_error(e, "Screen Capture"):
            raise  # Re-raise if user chose to exit
        
        # Fallback: use dummy data
        left_board = [[0] * 10 for _ in range(20)]
        right_board = [[0] * 10 for _ in range(20)]
        shared = {}
        queue_images = []
        error_handler.handle_warning("Using fallback data due to capture error", "Frame Processing")

        # Get current piece from queue (fallback to "T" if detection fails)
        current_piece = get_current_piece() or "T"

        try:
            pred = prediction_agent.handle({"board": left_board, "piece": current_piece, "orientation": 0})
        except Exception as e:
            # Handle prediction errors gracefully
            error_handler.handle_warning(f"Prediction error: {e}", "AI Prediction")
            # Fallback prediction
            pred = {"piece": current_piece, "target_col": 3, "target_rot": 0, "combo": 0, "is_b2b": False, "is_tspin": False}

        # Draw ghost on overlay (reuse global renderer instance)
        if overlay_renderer.visible and is_feature_enabled("ghost_pieces_enabled") and CURRENT_SETTINGS.show_combo:
            # Extract piece type from prediction if available, otherwise use detected piece
            piece_type = pred.get("piece", current_piece)
            
            # Get special move indicators from prediction
            is_tspin = pred.get("is_tspin", False)
            is_b2b = pred.get("is_b2b", False)
            combo = pred.get("combo", 0)
            
            # Update overlay counters
            overlay_renderer.update_counters(combo, is_b2b)
            
            # Draw ghost piece
            overlay_renderer.draw_ghost(
                overlay_renderer.screen, 
                pred["target_col"], 
                pred["target_rot"], 
                piece_type,
                is_tspin,
                is_b2b,
                combo
            )
            
            # Draw stats (combo, B2B)
            if is_feature_enabled("combo_indicators_enabled") or is_feature_enabled("b2b_indicators_enabled"):
                overlay_renderer.draw_stats(overlay_renderer.screen)
            
            # Draw performance info (FPS)
            if is_feature_enabled("performance_monitor_enabled"):
                overlay_renderer.draw_performance(overlay_renderer.screen)
            
            pygame.display.flip()

        # Record statistics
        if is_feature_enabled("statistics_enabled"):
            latency_ms = (time.time() - capture_start_ts) * 1000
            record_event(
                frame=FRAME_COUNTER,
                piece=pred.get("piece", current_piece),
                orientation=pred.get("target_rot", 0),
                lines_cleared=shared.get("lines_cleared", 0),
                combo=pred.get("combo", 0),
                b2b=pred.get("is_b2b", False),
                tspin=pred.get("is_tspin", False),
                latency_ms=latency_ms
            )

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
                "piece": current_piece,
                "prediction": pred
            }
        )
        
        FRAME_COUNTER += 1
        
    except Exception as e:
        LOGGER.error(f"Error in frame {FRAME_COUNTER}: {e}")
    
    finally:
        # End performance monitoring
        frame_time = performance_monitor.end_frame()
        
        # Log performance warnings if needed
        if frame_time > 0.050:  # 50ms threshold
            LOGGER.warning(f"Slow frame: {frame_time*1000:.1f}ms")
        
        # Log performance stats every 100 frames
        if FRAME_COUNTER % 100 == 0:
            stats = performance_monitor.get_stats()
            LOGGER.info(f"Performance: {stats['fps']:.1f} FPS, avg {stats['avg_frame_time']*1000:.1f}ms")


def _frame_loop():
    """Main frame processing loop - runs in separate thread."""
    while True:
        try:
            process_frames()
            time.sleep(1/30)  # Target 30 FPS
        except Exception as e:
            LOGGER.error(f"Error in frame loop: {e}")
            time.sleep(0.1)  # Prevent tight error loop


if __name__ == "__main__":
    # Start frame processing thread
    threading.Thread(target=_frame_loop, daemon=True).start()
    
    # Run the main overlay loop
    run_overlay()
