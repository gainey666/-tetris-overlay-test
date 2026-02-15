<!--- STATUS-BADGES-START --->
# 📊 Project Status

| Task | Status | Note |
|------|--------|------|
| 1 | done | Log & tracker files initialized |
| 2 | done | Python CI succeeded - artifacts in tetris_artifacts.zip |
| 3 | done | -note "Linux archive created (Windows skipped)" |
| 4 | done | -note "All unit tests passed." |
| 5 | done | -note "CNN latency recorded." |
| 6 | done | -note "ImGui UI launched." |
| 7 | in_progress | -note "Updating documentation" |
| 8 | done | -note "Verification passed; backup tetris_again_backup_20260215.zip generated." |
<!--- STATUS-BADGES-END   --->

# WindSurf AI – Python Prototype (Agents + Orchestrator)

This repository contains a minimal, fully functional prototype of the WindSurf AI pipeline:

- Agent-based architecture (see `src/agents/`).
- Declarative orchestration plan (`orchestration_plan.yaml`).
- Python pipeline (capture → board processing → prediction → overlay).
- Starter C++ bridge (`cpp_binding/board_processor_cpp/`).

## Quick Start

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m src.main -p orchestration_plan.yaml
```

## Project Layout

- `src/` – CLI, config, orchestrator, agents.
- `tests/` – pytest suite.
- `cpp_binding/board_processor_cpp/` – placeholder C++ bridge (pybind11 + OpenCV).
- Documentation: `project.md`, `PROJECT_COMPLETE_STATE.md`, `agents.md`, `system.md`.

See `project.md` for milestones and success criteria. 


<!--- TASKS-OVERVIEW-START --->
## 📋 Tasks Overview

| ID | Description | Current Status |
|----|-------------|----------------|
| 1 | Log & tracker cleanup | done |
| 2 | CI pipeline verification | done |
| 3 | Cross-platform packaging | done |
| 4 | Unit-test suite | done |
| 5 | CNN verification | done |
| 6 | ImGui UI configuration | done |
| 7 | Documentation refresh | in_progress |
| 8 | Verification & backup | done |
<!--- TASKS-OVERVIEW-END   --->

---

# -tetris-overlay-test
A copy of my screen overlay + predictions tool for backup.
