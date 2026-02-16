import datetime
import json
import logging
from io import StringIO
from pathlib import Path

import pytest

import run_overlay_core


def test_telemetry_logging(monkeypatch):
    log_path = Path("telemetry.log")
    buffer = StringIO()
    handler = logging.StreamHandler(buffer)
    handler.setFormatter(logging.Formatter("%(message)s"))
    temp_logger = logging.getLogger(log_path.stem + ".test")
    temp_logger.handlers = []
    temp_logger.addHandler(handler)
    temp_logger.setLevel(logging.INFO)
    temp_logger.propagate = False
    monkeypatch.setattr(run_overlay_core, "LOGGER", temp_logger)

    def fake_process_frames():
        payload = {
            "ts": datetime.datetime.utcnow().isoformat(),
            "frame_id": 0,
            "score_w": 10,
            "score_h": 20,
            "wins_w": 30,
            "wins_h": 40,
            "timer_w": 50,
            "timer_h": 60,
            "queue_len": 2,
        }
        temp_logger.info(json.dumps(payload))

    monkeypatch.setattr(run_overlay_core, "process_frames", fake_process_frames)
    run_overlay_core.process_frames()
    log_line = buffer.getvalue().strip().splitlines()[-1]
    data = json.loads(log_line)

    expected_keys = {
        "ts",
        "frame_id",
        "score_w",
        "score_h",
        "wins_w",
        "wins_h",
        "timer_w",
        "timer_h",
        "queue_len",
    }
    assert expected_keys.issubset(data.keys())
    size_fields = [
        "score_w",
        "score_h",
        "wins_w",
        "wins_h",
        "timer_w",
        "timer_h",
    ]
    for field in size_fields:
        assert isinstance(data[field], int) and data[field] > 0
    assert isinstance(data["queue_len"], int) and data["queue_len"] > 0

    temp_logger.removeHandler(handler)
    handler.close()
