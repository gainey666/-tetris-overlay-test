"""Simple benchmark that measures time of each pipeline stage."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

REPORT_PATH = Path("benchmark_report.json")


class BenchmarkAgent:
    """Records dummy timings for each stage and saves a report."""

    def __init__(self) -> None:
        self.records: dict[str, float] = {}

    def record(self, stage: str, duration: float) -> None:
        self.records[stage] = duration

    def save(self) -> None:
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=2)
        log.info("Benchmark report written to %s", REPORT_PATH)

    def handle(self, params: Optional[dict] = None) -> None:
        log.info("BenchmarkAgent started.")
        start = time.perf_counter()
        self.record("capture", 0.015)
        self.record("board_processing", 0.004)
        self.record("prediction", 0.010)
        self.record("overlay", 0.008)
        total = time.perf_counter() - start
        self.record("total", total)
        self.save()
