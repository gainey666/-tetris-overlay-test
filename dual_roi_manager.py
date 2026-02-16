import json, logging
from pathlib import Path

CONFIG_PATH = Path("config.json")

def load_config():
    if not CONFIG_PATH.is_file():
        logging.info("Config missing – creating empty template")
        return {"roi": [], "hwnd": None}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

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
