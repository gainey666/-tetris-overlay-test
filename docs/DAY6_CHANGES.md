# Day 6 Change Log – ROI + Shared UI Pipeline (2026-02-15)

## Overview
Refreshed the overlay capture stack to support full Zone Battle telemetry, added helper modules for shared UI/next queue, and removed obsolete calibration experiments. This document captures **what changed**, **why**, and **how** to reproduce or extend the work.

---

## 1. ROI schema + capture utilities
- **What:** Replaced `roi_config.json` with a full manifest (17 scalar ROIs + composite `next_queue`). Added `roi_capture.py`, `shared_ui_capture.py`, `next_queue_capture.py`, and `ocr_utils.py`.
- **Why:** Needed a consistent config that downstream agents (piece classifier, OCR) can consume automatically; also enables queue-length flexibility (1‑4 upcoming pieces) and shared score/wins/timer capture to avoid redundant work per player.
- **How:**
  - `roi_calibrator.py` now walks through the full ROI sequence, prompts for shared UI rectangles, then lets the user draw up to four queue slots. Saves both dual-board rois (via `dual_roi_manager`) and the extended `roi_config.json`.
  - `shared_ui_capture`/`next_queue_capture` each grab a single full-screen frame (cached `ScreenCapture`) and crop the relevant rectangles, returning dictionaries/lists for easy consumption.
  - `ocr_utils.extract_number` provides a tiny pytesseract wrapper for numeric overlays.

## 2. Overlay processing loop updates
- **What:** `run_overlay_core.py` imports the new helpers and logs shared UI + queue data during `process_frames()`.
- **Why:** Ensures every overlay tick can feed OCR and queue classifiers without bolting on separate scripts.
- **How:** After dual board capture, the loop now calls `capture_shared_ui()` and `capture_next_queue()` once per frame and prints a concise summary (board shapes, shared ROI keys, queue length) for debugging.

## 3. Cleanup / retired artifacts
- **Removed:** `roi_calibrator_new.py` (experimental win32 window finder) and the entire `.qa_temp/` scratch folder.
- **Why:** Both were outdated prototypes superseded by the new calibration/UI capture pipeline; keeping them risked confusion for Day 6 automation.
- **How:** Deleted via PowerShell `Remove-Item`; no dependencies referenced these files. Documented here per request.

---

## Next steps / follow-up
1. Add `tests/test_shared_ui.py` to exercise the helpers (ensure queue length ≤4, shared dict has 3 keys).
2. Feed `ocr_utils.extract_number(shared["score"])` into telemetry logs and persist results for match analytics.
3. Bundle `roi_config.json` + quick-start instructions into any release archives so end users can recalibrate quickly.

_Last updated: 2026-02-15 22:45 UTC-06:00_
