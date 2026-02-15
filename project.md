# Project Vision & Success Metrics

**Vision** – Build a modular, high‑performance board‑game‑state detector that can run in real‑time on consumer hardware, ultimately implemented in C++/DXGI for maximum frame‑rate, while preserving a clean, testable Python orchestration layer.

**Milestones**

| # | Milestone                                   | Target date | Success metric                                    |
|---|---------------------------------------------|------------|---------------------------------------------------|
| 1 | Basic Python prototype (agents + CLI)       | 2024‑01‑15 | All unit tests pass, end‑to‑end run < 2 s per frame |
| 2 | Add C++ board‑processor via pybind11        | 2024‑02‑28 | 30 % speed‑up vs Python version                  |
| 3 | Integrate DXGI surface capture (Windows)    | 2024‑04‑10 | 60 fps sustained on a 1080p webcam               |
| 4 | Full C++ pipeline (capture → inference)    | 2024‑06‑01 | End‑to‑end latency ≤ 5 ms                         |
| 5 | Production‑ready packaging (pip / wheels) | 2024‑07‑15 | `pip install windsurf-ai` works on Win/macOS/Linux |

**Success Metrics** –  

* **Latency**: < 10 ms end‑to‑end (capture → board mask).  
* **Throughput**: ≥ 60 fps sustained on a 1080p source.  
* **Accuracy**: ≥ 98 % board‑mask IoU on the validation set.  
* **Stability**: < 0.1 % crash rate across 100 h of continuous run.

---

### How to use this doc

- Links of the form `@project.md#1-44` refer to this file (line 1‑44).  
- Keep the milestones up‑to‑date as you ship new agents or replace them with C++ continuations.
