"""CLI entry point – forwards to the orchestrator."""

import argparse
import logging
import sys
from pathlib import Path

try:
    from .orchestrator.orchestrator import main as orchestrate
except ImportError:
    from src.orchestrator.orchestrator import main as orchestrate


def parse_args() -> argparse.Namespace:
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
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s %(name)s – %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    args = parse_args()
    configure_logging(args.verbose)

    if args.benchmark:
        import time
        from src.agents.prediction_agent_mock_perfect import PredictionAgent
        from src.agents.board_extractor_agent import BoardExtractorAgent
        from src.agents.piece_detector_agent import PieceDetectorAgent

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
        return

    plan_path = Path(args.plan)
    if not plan_path.is_file():
        logging.error("Plan file %s does not exist.", plan_path)
        sys.exit(1)

    orchestrate(plan_path=str(plan_path))


if __name__ == "__main__":
    main()
