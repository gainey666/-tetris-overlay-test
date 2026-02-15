# Architecture

- **CaptureAgent** (DXGI or OpenCV) → `frame_queue` 
- **BoardExtractorAgent** → binary 20×10 matrix
- **PieceDetectorAgent** → piece type + orientation
- **PredictionAgent** (Dellacherie) → best column & rotation
- **OverlayRendererAgent** → Pygame window or console output
- **Orchestrator** wires the agents via `orchestration_plan.yaml`.

# Dependencies
- Python 3.12
- OpenCV, NumPy, pybind11, pygame, mss
- Visual Studio 2026 Build Tools (C++), vcpkg (OpenCV, DirectX libs)

# Build Flow
`build_dxgi_full_fixed.ps1` → generates `dxgi_capture.cp312-win_amd64.pyd` → copied to `src/agents/`.
