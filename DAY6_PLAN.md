# DAY6_PLAN.md – 10-hour work schedule (2025-02-15)

## Overview
We have a production-ready Tetris overlay (Day 5).  
Day 6 is dedicated to **reliability, packaging, testing and CI** so the project can be shipped and maintained by anyone.

---  

## Tasks & Time Estimates

| # | Task | Details | Owner | ETA | Status |
|---|------|---------|-------|-----|--------|
| 1 | Log & tracker files | Add `DAY6_PLAN.md` (this) and `progress_log.json` (template). Initialise JSON entries to `todo`. | **You** | 0.5 h | `todo` |
| 2 | CI pipeline | Write GitHub Actions workflow (`ci.yml`) that restores vcpkg, builds, runs benchmark, packages ZIP. | **You** | 2.0 h | `todo` |
| 3 | Cross‑platform packaging | Windows installer (Inno Setup) + optional Linux AppImage/tarball. | **You** | 1.5 h | `todo` |
| 4 | Unit‑test suite | Add GoogleTest (or Catch2) target covering FrameGrabber, BoardExtractor, HeuristicEngine. | **You** | 1.5 h | `todo` |
| 5 | Optional CNN backend | Verify ONNX model loads, run inference, measure < 0.2 ms. Add CMake flag. | **You** | 1.5 h | `todo` |
| 6 | User‑config UI | Tiny ImGui overlay for toggling `use_cnn`, opacity, re‑calibration. Persist to `tetris_config.json`. | **You** | 1.0 h | `todo` |
| 7 | Documentation polish | Update README, add CI badge, installer usage, benchmark instructions. | **You** | 0.5 h | `todo` |
| 8 | Verification & backup | Run fresh installer on clean VM, benchmark, create backup zip `tetris_again_backup_20250215.zip`. | **You** | 0.5 h | `todo` |

---

## How to use `progress_log.json` 

- Open `progress_log.json` in any editor.  
- After completing a task, change its `"status"` from `"todo"` → `"done"` and set `"finished_at"` to an ISO‑8601 timestamp.  
- If a task stalls, set `"status"` to `"blocked"` and add a `"note"` field explaining the reason.

### Example entry after finishing Task 2

```json
{
  "task_id": 2,
  "name": "CI pipeline",
  "status": "done",
  "started_at": "2025-02-15T09:30:00Z",
  "finished_at": "2025-02-15T11:45:00Z",
  "note": "GitHub Actions workflow passes on Windows-2022 runner."
}
```

End of Day 6 plan
Once all rows show "done" you can mark the day as complete and move on to the next roadmap items in FUTURE_ROADMAP.md. Happy coding! 🚀
