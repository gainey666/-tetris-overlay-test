# Agents Specification & Orchestration Plan

## Overview

The prototype is built around self‑contained agents that implement `handle(params)` and are registered in `src/orchestrator/orchestrator.py`.

## Agent list

| Agent module                | Class name               | Responsibility                                   |
|-----------------------------|--------------------------|--------------------------------------------------|
| `capture_agent`             | `CaptureAgent`           | Grab frames from webcam / video capture          |
| `board_processor_agent`     | `BoardProcessorAgent`    | Convert frames to 20×10 binary board mask        |
| `prediction_agent`          | `PredictionAgent`        | Produce piece predictions from the mask          |
| `overlay_renderer_agent`    | `OverlayRendererAgent`   | Pygame overlay drawing                           |
| `run_agent`                 | `RunAgent`               | Convenience wrapper to start capture → overlay   |
| `calibrate_agent`           | `CalibrateAgent`         | Store dummy calibration data                     |
| `benchmark_agent`           | `BenchmarkAgent`         | Record stage durations                           |
| `config_agent`              | `ConfigAgent`            | Load `AppConfig` from `config.json`              |
| `error_handler_agent`       | `ErrorHandlerAgent`      | No‑op placeholder for custom plans               |
| `shutdown_agent`            | `ShutdownAgent`          | Stop running agents                              |
| `orchestrator_agent_main`   | `OrchestratorAgentMain`  | Treat orchestrator plan as an agent              |
| `orchestrator_agent_alias`  | Alias                    | Backwards compatibility alias                    |

## Plan format

The default plan (`orchestration_plan.yaml`) runs:

1. `calibrate`
2. `load_config`
3. `run` (duration 60)
4. `overlay`
5. `benchmark`
6. `shutdown`

Each name must exist in the agent registry inside the orchestrator. 
