"""Main entry point for the Tetris overlay runtime."""

import datetime
import json
import logging
import sys
import threading
import time
from pathlib import Path
from typing import Any, Dict

import keyboard  # type: ignore
import pygame

# ---------------------------------------------------------------------------
# Tracer integration – safe no-op when package/server unavailable
# ---------------------------------------------------------------------------
try:
    from tracer.client import safe_trace_calls as trace_calls
except Exception:  # pragma: no cover - defensive fallback
    def trace_calls(*_, **__):  # type: ignore[misc]
        def _decorator(func):
            return func

        return _decorator

from tetris_overlay_core import graceful_exit, reset_calibration, run_overlay, toggle_overlay
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

from ui.settings_storage import load as load_settings, save as save_settings
from ui.settings_dialog import SettingsDialog
from ui.stats_dashboard import StatsDashboard
from stats.db import init_db
from stats.collector import end_current_match, record_event, start_new_match

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

LOGGER = setup_telemetry_logger()
FRAME_COUNTER = 0

# Global settings singleton
CURRENT_SETTINGS = load_settings()

# Single renderer instance reused across frames
overlay_renderer = OverlayRenderer()

# Perform startup checks
if not error_handler.check_dependencies():
    logging.error("Dependency check failed. Exiting.")
    sys.exit(1)

if not error_handler.check_roi_config():
    logging.warning("ROI configuration incomplete. Please run calibrator.")

# Initialize persistence
init_db()
start_new_match(CURRENT_SETTINGS.prediction_agent)


@trace_calls("S")
def _toggle_logging() -> None:
    """Toggle log level between INFO and DEBUG."""
    root = logging.getLogger()
    if root.level == logging.DEBUG:
        root.setLevel(logging.INFO)
        logging.info("Debug logging OFF")
    else:
        root.setLevel(logging.DEBUG)
        logging.debug("Debug logging ON")


@trace_calls("F")
def _graceful_exit() -> None:
    """Handle graceful exit with stats cleanup."""
    end_current_match()
    logging.info("Esc pressed – shutting down")
    graceful_exit()


@trace_calls("S")
def _register_dynamic_hotkeys() -> None:
    """Register all hot-keys according to CURRENT settings."""
    keyboard.unhook_all()

    hk = CURRENT_SETTINGS.hotkeys
    keyboard.add_hotkey(hk.toggle_overlay, toggle_overlay)
    keyboard.add_hotkey(hk.open_settings, _open_settings)
    keyboard.add_hotkey(hk.debug_logging, _toggle_logging)
    keyboard.add_hotkey(hk.quit, _graceful_exit)
    keyboard.add_hotkey(hk.calibrate, start_calibrator)
    keyboard.add_hotkey(hk.open_stats, _open_stats)


@trace_calls("S")
def _open_settings() -> None:
    dialog = SettingsDialog()
    dialog.settings_changed.connect(_on_settings_changed)
    dialog.exec()


@trace_calls("S")
def _open_stats() -> None:
    StatsDashboard().show()


@trace_calls("S")
def _on_settings_changed(new_settings) -> None:
    global CURRENT_SETTINGS
    CURRENT_SETTINGS = new_settings
    save_settings(new_settings)
    _register_dynamic_hotkeys()
    overlay_renderer.update_ghost_style(
        colour=new_settings.ghost.colour,
        opacity=new_settings.ghost.opacity,
    )


# Register initial hotkeys
_register_dynamic_hotkeys()


@trace_calls("S")
def load_prediction_agent(agent_name: str) -> Any:
    """Dynamically import and instantiate a prediction agent."""
    if agent_name == "dellacherie":
        from src.agents.prediction_agent_dellacherie import PredictionAgent
    elif agent_name == "onnx":
        from src.agents.prediction_agent_onnx import PredictionAgent
    elif agent_name == "simple":
        from src.agents.prediction_agent_simple import PredictionAgent
    elif agent_name == "mock":
        from src.agents.prediction_agent_mock_perfect import PredictionAgent
    else:
        raise ValueError(f"Unknown prediction_agent: {agent_name}")

    return PredictionAgent()


prediction_agent = load_prediction_agent(CURRENT_SETTINGS.prediction_agent)


BOARD_HEIGHT = 20
BOARD_WIDTH = 10


def _ensure_rgb_array(image) -> "np.ndarray":
    import numpy as np
    import cv2

    array = np.array(image)
    if array.ndim == 2:
        return cv2.cvtColor(array, cv2.COLOR_GRAY2RGB)
    if array.shape[2] == 4:
        return cv2.cvtColor(array, cv2.COLOR_RGBA2RGB)
    return array


def roi_to_binary_matrix(roi_image):
    """Convert an ROI image to a normalized 20×10 binary matrix (values 0/1)."""
    import cv2
    import numpy as np

    frame = _ensure_rgb_array(roi_image)
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2,
    )
    board = cv2.resize(thresh, (BOARD_WIDTH, BOARD_HEIGHT), interpolation=cv2.INTER_NEAREST)
    binary = (board > 0).astype("uint8")
    return binary


def extract_board(image):
    """Extract board state from a captured image and return a normalized matrix."""
    import numpy as np

    binary = roi_to_binary_matrix(image)
    if binary.shape != (BOARD_HEIGHT, BOARD_WIDTH):
        raise ValueError(f"Unexpected board shape {binary.shape}")

    fill_ratio = float(binary.mean())
    if fill_ratio < 0.01:
        LOGGER.warning("Extracted board appears empty (ratio=%.4f)", fill_ratio)
    return binary


@trace_calls("S")
def process_frames() -> None:
    """Process a single frame of the overlay."""
    global FRAME_COUNTER

    performance_monitor.start_frame()
    capture_start_ts = time.time()

    try:
        left_img, right_img = DualScreenCapture().grab()
        left_board = extract_board(left_img)
        right_board = extract_board(right_img)
        shared = capture_shared_ui() or {}
        queue_images = capture_next_queue()
    except Exception as exc:
        if not error_handler.handle_critical_error(exc, "Screen Capture"):
            raise
        left_board = [[0] * 10 for _ in range(20)]
        right_board = [[0] * 10 for _ in range(20)]
        shared = {}
        queue_images = []
        error_handler.handle_warning(
            "Using fallback data due to capture error", "Frame Processing"
        )

    current_piece = get_current_piece() or "T"

    try:
        pred = prediction_agent.handle(
            {"board": left_board, "piece": current_piece, "orientation": 0}
        )
    except Exception as exc:
        error_handler.handle_warning(f"Prediction error: {exc}", "AI Prediction")
        pred = {
            "piece": current_piece,
            "target_col": 3,
            "target_rot": 0,
            "combo": 0,
            "is_b2b": False,
            "is_tspin": False,
        }

    if (
        overlay_renderer.visible
        and is_feature_enabled("ghost_pieces_enabled")
        and CURRENT_SETTINGS.show_combo
    ):
        piece_type = pred.get("piece", current_piece)
        is_tspin = pred.get("is_tspin", False)
        is_b2b = pred.get("is_b2b", False)
        combo = pred.get("combo", 0)

        overlay_renderer.update_counters(combo, is_b2b)
        overlay_renderer.draw_ghost(
            overlay_renderer.screen,
            pred.get("target_col", 0),
            pred.get("target_rot", 0),
            piece_type,
            is_tspin,
            is_b2b,
            combo,
        )

    if is_feature_enabled("combo_indicators_enabled") or is_feature_enabled(
        "b2b_indicators_enabled"
    ):
        overlay_renderer.draw_stats(overlay_renderer.screen)

    if is_feature_enabled("performance_monitor_enabled"):
        overlay_renderer.draw_performance(overlay_renderer.screen)

    pygame.display.flip()

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
            latency_ms=latency_ms,
        )

    FRAME_COUNTER += 1

    score = shared.get("score")
    wins = shared.get("wins")
    timer = shared.get("timer")

    LOGGER.info(
        {
            "ts": datetime.datetime.utcnow().isoformat(),
            "frame_id": FRAME_COUNTER,
            "score_w": getattr(score, "size", (0, 0))[0] if score else 0,
            "score_h": getattr(score, "size", (0, 0))[1] if score else 0,
            "wins_w": getattr(wins, "size", (0, 0))[0] if wins else 0,
            "wins_h": getattr(wins, "size", (0, 0))[1] if wins else 0,
            "timer_w": getattr(timer, "size", (0, 0))[0] if timer else 0,
            "timer_h": getattr(timer, "size", (0, 0))[1] if timer else 0,
            "piece": current_piece,
            "prediction": pred,
        }
    )

    FRAME_COUNTER += 1  # historical artifact retained for compatibility

    frame_time = performance_monitor.end_frame()
    if frame_time > 0.050:
        LOGGER.warning(f"Slow frame: {frame_time * 1000:.1f}ms")


@trace_calls("S")
def _frame_worker() -> None:
    """Runs process_frames in a loop with ~30 FPS budget."""
    target_fps = 30
    frame_time = 1.0 / target_fps
    while True:
        start = time.time()
        try:
            process_frames()
        except Exception as exc:
            logging.error("Frame error: %s", exc, exc_info=True)
        elapsed = time.time() - start
        time.sleep(max(0.0, frame_time - elapsed))


if __name__ == "__main__":
    _register_dynamic_hotkeys()
    start_new_match(CURRENT_SETTINGS.prediction_agent)
    threading.Thread(target=_frame_worker, daemon=True).start()
    run_overlay()
