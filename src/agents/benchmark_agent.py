"""Simple benchmark that measures time of each pipeline stage."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Optional

# Import our logger bridge
try:
    import logger_bridge as log

# Import global function tracer
try:
    from tracer.client import safe_trace_calls as trace_calls
    TRACER_AVAILABLE = True
except ImportError:
    TRACER_AVAILABLE = False

    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False


log = logging.getLogger(__name__)

REPORT_PATH = Path("benchmark_report.json")


class BenchmarkAgent:
    """Records dummy timings for each stage and saves a report."""

    def __init__(self) -> None:
    @trace_calls('__init__', 'benchmark_agent.py', 35)
        self.records: dict[str, float] = {}

    def record(self, stage: str, duration: float) -> None:
    @trace_calls('record', 'benchmark_agent.py', 38)
        self.records[stage] = duration

    def save(self) -> None:
    @trace_calls('save', 'benchmark_agent.py', 41)
        with REPORT_PATH.open("w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=2)
        log.info("Benchmark report written to %s", REPORT_PATH)

    def handle(self, params: Optional[dict] = None) -> None:
    @trace_calls('handle', 'benchmark_agent.py', 46)
        log.info("BenchmarkAgent started.")
        start = time.perf_counter()
        self.record("capture", 0.015)
        self.record("board_processing", 0.004)
        self.record("prediction", 0.010)
        self.record("overlay", 0.008)
        total = time.perf_counter() - start
        self.record("total", total)
        self.save()
