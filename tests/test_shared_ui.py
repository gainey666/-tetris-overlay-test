import json
import pathlib

import pytest


CONFIG = json.load(open("config/roi_config.json", encoding="utf-8"))
REQUIRED = {
    "player_left_board",
    "player_right_board",
    "left_hold_piece",
    "right_hold_piece",
    "left_next_preview",
    "right_next_preview",
    "left_garbage_indicator",
    "right_garbage_indicator",
    "left_zone_meter",
    "right_zone_meter",
    "left_score",
    "right_score",
    "left_player_name",
    "right_player_name",
    "wins",
    "timer",
}


def test_required_keys():
    keys = {entry["name"] for entry in CONFIG["rois"]}
    missing = REQUIRED - keys
    assert not missing, f"Missing ROI keys: {missing}"


def test_nonzero_rectangles():
    for entry in CONFIG["rois"]:
        if entry["name"] in REQUIRED:
            left, top, width, height = entry["rect"]
            assert width > 0 and height > 0, f"{entry['name']} has zero size"


def test_next_queue_bounds():
    queue = next(e for e in CONFIG["rois"] if e["name"] == "next_queue")
    slots = queue["rect"]
    assert 1 <= len(slots) <= 4, f"next_queue length {len(slots)} out of bounds"
    for idx, rect in enumerate(slots, start=1):
        _, _, width, height = rect
        assert width > 0 and height > 0, f"slot {idx} in next_queue has zero size"
