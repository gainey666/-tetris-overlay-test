import json
import pathlib

import pytest


CONFIG = json.load(open("roi_config.json"))
REQUIRED = {
    "score",
    "wins",
    "timer",
    "level",
    "lines_cleared",
    "garbage_meter",
    "combo_counter",
    "b2b_indicator",
    "opponent_score",
    "opponent_level",
    "opponent_lines",
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
    for rect in slots:
        _, _, width, height = rect
        assert width > 0 and height > 0, "empty slot in next_queue"
