# Target End‑State (C++ pipeline, DXGI/OpenCV)

## High‑level goal
Replace the Python‑only agents with a native C++ implementation that uses:

* **DXGI** for low‑latency GPU surface capture on Windows.
* **OpenCV** (C++ API) for image preprocessing and mask extraction.
* **ONNX Runtime** (or a custom inference engine) for neural‑network predictions.

## Desired architecture (final)

+--------------------+ +------------------------+ +---------------------+
| DXGI Capture       | → | C++ Board Processor    | → | C++ Inference      |
+--------------------+ +------------------------+ +---------------------+
                       ↓
                     +-------------------+
                     | Python Orchestr. |
                     +-------------------+
                     | +---------------+ |
                     | | Pygame Overlay| |
                     | +---------------+ |

## Remaining blockers (as of 2024‑02‑14)

| # | Blocker                                               | Owner | ETA |
|---|-------------------------------------------------------|-------|-----|
| 1 | C++ board‑processor implementation & pybind11 wrapper | C++ dev | 2024‑03‑01 |
| 2 | DXGI surface capture (needs Win10+ SDK)               | C++ dev | 2024‑03‑15 |
| 3 | Benchmarking harness for C++ vs Python               | QA     | 2024‑04‑01 |
| 4 | Cross‑platform fallback (Linux/macOS)                | DevOps | 2024‑04‑15 |
| 5 | CI/CD pipeline for building and publishing wheels     | DevOps | 2024‑05‑01 |

## Migration plan (steps)

1. **Expose C++ board processor** via pybind11 → replace `BoardProcessorAgent` with the native version.  
2. **Add DXGI capture** (Windows only) → optional fallback to OpenCV `VideoCapture`.  
3. **Swap prediction** → ONNX Runtime C++ API wrapped with pybind11.  
4. **Retain Python orchestrator** – it stays unchanged; agents become thin wrappers around the compiled modules.  

Once the above are complete the system will meet the “Target End‑State” as described.
