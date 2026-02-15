# CI Pipeline – Local Execution

The repository contains a tiny automation script that:
1. Generates a GitHub-Actions workflow (`.github/workflows/ci.yml`).
2. Executes it locally with **`act`** (the open-source GitHub-Actions runner). If `act` is not installed, the script automatically falls back to a plain CMake build and benchmark.
3. Packages the built executable, benchmark output, and `calibration.json` into `tetris_artifacts.zip`.

## One-line usage (AFK-ready)
```powershell
.\run_ci_pipeline.ps1
```

The script updates `progress_log.json` automatically, so the Cursor-LLM never asks you for more input.

## What happens behind the scenes
| Phase | What the script does | Approx. wall-clock time |
|-------|----------------------|------------------------|
| Mark task in_progress | Calls update_task.ps1 → writes a timestamp to progress_log.json. | < 1s |
| Generate workflow | Writes .github/workflows/ci.yml (tiny file). | < 1s |
| Execute CI | If act is installed → runs the full GitHub-Actions job inside Docker (≈ 6-8min).<br>If not → performs a local CMake configure + build + benchmark (≈ 4-5min). | 4-8min |
| Package artifacts | Zips the built exe, benchmark log, calibration file. | < 30s |
| Mark task done / blocked | Updates progress_log.json with final timestamp + note. | < 1s |

## What to check after the script finishes
- `progress_log.json` – task 2 should read `"status":"done"` (or `"blocked"` with a note if something failed).
- `tetris_artifacts.zip` – should contain: `tetris_overlay.exe`, `benchmark.txt`, `calibration.json`.
- `benchmark.txt` – verify the latency numbers (≤ 30ms per the Day 5 claim).
- GitHub-Actions workflow file – open `.github/workflows/ci.yml` to confirm it matches the template.

## Trouble-shooting tips
| Symptom | Quick fix |
|---------|-----------|
| `act` command not found | The script automatically falls back to a direct CMake build. No intervention needed. |
| CMake configure fails | Make sure you have a clean vcpkg directory (`vcpkg\installed`) and that the toolchain path points to `vcpkg\scripts\buildsystems\vcpkg.cmake`. |
| Benchmark hangs | Ensure the game window is not in exclusive fullscreen; the overlay can still run in windowed mode. |
| `update_task.ps1` errors | Verify that `progress_log.json` exists and is valid JSON. The script will rewrite the file in place; a malformed file will cause a JSON parse error. |
| Artifact zip empty | Check that the artifacts folder actually contains the three files before `Compress-Archive` runs. |

## TL;DR – One-line command you can copy-paste now
```powershell
cd C:\path\to\tetris_overlay; .\run_ci_pipeline.ps1
```

Run that, sit back for ~10 minutes, then come back and verify the two files mentioned above. The progress-tracker will already be updated, so the Cursor-LLM won't ask you for anything else.
