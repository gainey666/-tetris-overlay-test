import json, logging
from pathlib import Path

CONFIG_PATH = Path("config/roi_config.json")


def load_config():
    if not CONFIG_PATH.is_file():
        logging.info("Config missing – creating empty template")
        return {"rois": [], "hwnd": None}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Convert new format to old dual ROI format
    rois = data.get("rois", [])
    left_board = None
    right_board = None
    
    for roi in rois:
        if roi.get("name") == "player_left_board":
            left_board = roi.get("rect")
        elif roi.get("name") == "player_right_board":
            right_board = roi.get("rect")
    
    return {"roi": [left_board, right_board] if left_board and right_board else [], "hwnd": None}


def save_config(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    logging.info("Config saved")


def set_roi_pair(pair):
    cfg = load_config()
    cfg["roi"] = pair
    save_config(cfg)


def get_roi_pair():
    return load_config().get("roi", [])
