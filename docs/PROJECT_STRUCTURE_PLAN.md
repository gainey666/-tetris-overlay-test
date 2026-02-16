# Project Structure Plan – Organize loose files by type

## Goal
Group every loose file into logical folders so anyone can understand what each item is and where it belongs, then fix any import/path references.

## Proposed folder layout

```
-tetris-overlay-test/
│
├─ src/                     # Core runtime source
│   ├─ agents/              # Agent modules (only keep capture_agent shim)
│   └─ capture_agent.py     # Main capture class
│
├─ tools/                   # Helper scripts and utilities
│   ├─ calibration/         # Calibration helpers
│   │   └─ calibration_ui.py
│   ├─ debug/               # Debug utilities
│   │   ├─ debug_auto_fit.py
│   │   └─ debug_windows.py
│   ├─ window/              # Window/filter utilities
│   │   ├─ create_window_filter.py
│   │   └─ window_manager.py
│   ├─ build/               # Build/install scripts
│   └─ misc/                # Miscellaneous helpers
│       └─ safe_create.py
│
├─ tests/                   # Test suite (pytest)
│   ├─ test_shared_ui.py
│   ├─ test_telemetry_logging.py
│   └─ test_regression.py
│
├─ docs/                    # Documentation
│   ├─ README.md
│   ├─ LLM_QUICK_START.md
│   ├─ DAY6_CHANGES.md
│   ├─ PROJECT_CLEANUP_GUIDE.md
│   └─ PROJECT_STRUCTURE_PLAN.md
│
├─ config/                  # Configuration files
│   ├─ roi_config.json
│   ├─ config.json
│   └─ calibration.json
│
├─ scripts/                 # Automation/CI scripts
│   └─ run_all_tests.py
│
├─ assets/                  # Large binary assets (optional)
│   └─ (models, screenshots, etc. if needed)
│
└─ legacy/                  # Already ignored; contains archived files
```

## Actions to take
1. **Create the new folders** (tools/calibration, tools/debug, tools/window, tools/build, tools/misc, docs, config, scripts, assets).
2. **Move files** into the appropriate folders per the mapping above.
3. **Update imports** in any Python files that reference moved files (e.g., `from calibration_ui` → `from tools.calibration.calibration_ui`).
4. **Update run_all_tests.py** if it references files by relative path.
5. **Update documentation** that mentions file locations (README.md, LLM_QUICK_START.md).
6. **Run the overlay and calibration** to ensure nothing breaks after the moves.
7. **Commit the restructure** with a clear commit message.

## Files to move (current → target)

- `calibration_ui.py` → `tools/calibration/calibration_ui.py`
- `debug_auto_fit.py` → `tools/debug/debug_auto_fit.py`
- `debug_windows.py` → `tools/debug/debug_windows.py`
- `create_window_filter.py` → `tools/window/create_window_filter.py`
- `window_manager.py` → `tools/window/window_manager.py`
- `safe_create.py` → `tools/misc/safe_create.py`
- `README.md`, `LLM_QUICK_START.md`, `DAY6_CHANGES.md`, `PROJECT_CLEANUP_GUIDE.md` → `docs/`
- `roi_config.json`, `config.json` → `config/`
- `run_all_tests.py` → `scripts/`

## Imports to update (examples)
- Any `import calibration_ui` → `from tools.calibration import calibration_ui`
- Any `import debug_auto_fit` → `from tools.debug import debug_auto_fit`
- Any `import create_window_filter` → `from tools.window import create_window_filter`
- Any `import window_manager` → `from tools.window import window_manager`
- Any `import safe_create` → `from tools.misc import safe_create`

## Result
- Clear separation of concerns.
- Easy to find files by purpose.
- Minimal top‑level clutter.
- All paths and imports updated and tested.
