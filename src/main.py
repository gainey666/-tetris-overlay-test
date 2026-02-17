"""CLI entry point – forwards to the orchestrator."""

import argparse
import logging
import sys
from pathlib import Path

# Import our logger bridge
try:
    import logger_bridge as log
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False

try:
    from .orchestrator.orchestrator import main as orchestrate
except ImportError:
    from src.orchestrator.orchestrator import main as orchestrate


def parse_args() -> argparse.Namespace:
@trace_calls('parse_args', 'main.py', 21)
    parser = argparse.ArgumentParser(
        description="WindSurf AI – run the multi-step orchestrated pipeline."
    )
    parser.add_argument(
        "-p",
        "--plan",
        default="orchestration_plan.yaml",
        help="Path to an orchestration plan YAML file (default: orchestration_plan.yaml)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable DEBUG logging",
    )
    parser.add_argument(
        "--benchmark",
        type=int,
        help="Run benchmark for specified milliseconds",
    )
    return parser.parse_args()


def configure_logging(verbose: bool) -> None:
@trace_calls('configure_logging', 'main.py', 45)
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s %(name)s – %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
@trace_calls('main', 'main.py', 54)
    args = parse_args()
    configure_logging(args.verbose)

    if args.benchmark:
        if LOGGER_AVAILABLE:
            log.log_info("main", f"Running benchmark for {args.benchmark}ms")
        
        import time
        from src.agents.prediction_agent_mock_perfect import PredictionAgent
        from src.agents.board_extractor_agent import BoardExtractorAgent
        from src.agents.piece_detector_agent import PieceDetectorAgent

# Import global function tracer
try:
    from tracer.client import safe_trace_calls as trace_calls
    TRACER_AVAILABLE = True
except ImportError:
    TRACER_AVAILABLE = False


        print(f"Running benchmark for {args.benchmark}ms...")
        start_time = time.time()

        # Simple benchmark - run predictions
        predictor = PredictionAgent()
        extractor = BoardExtractorAgent()
        detector = PieceDetectorAgent()

        # Simulate work for specified duration
        elapsed = 0
        while elapsed < args.benchmark / 1000.0:
            # Run a quick prediction cycle
            result = predictor.handle(
                {"board": "dummy", "piece": "T", "orientation": 0}
            )
            elapsed = time.time() - start_time

        print(f"Benchmark completed in {elapsed*1000:.2f}ms")
        print(f"Predictions per second: {len(result) / elapsed:.0f}")
        if LOGGER_AVAILABLE:
            log.log_success("main", f"Benchmark completed: {len(result) / elapsed:.0f} predictions/sec")
        return

    plan_path = Path(args.plan)
    if not plan_path.is_file():
        logging.error("Plan file %s does not exist.", plan_path)
        if LOGGER_AVAILABLE:
            log.log_fail("main", f"Plan file not found: {plan_path}")
        sys.exit(1)

    if LOGGER_AVAILABLE:
        log.log_info("main", f"Loading plan from: {plan_path}")
    
    orchestrate(plan_path=str(plan_path))


if __name__ == "__main__":
    main()
