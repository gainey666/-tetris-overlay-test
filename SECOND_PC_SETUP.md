# Second-PC Setup & Sync Guide

This guide explains how to bring the Tetris Overlay project onto a new Windows PC, build the portable overlay/installer, and keep it in sync with the GitHub backup at <https://github.com/gainey666/-tetris-overlay-test>.

---

## 1. Project Snapshot (Feb 15, 2026)

| Task | Status | Notes |
|------|--------|-------|
| 1. Log & tracker cleanup | ✅ done | `progress_log.json` initialized, stale temp folders cleaned. |
| 2. CI pipeline | ✅ done | Python CI green; artifacts saved to `tetris_artifacts.zip`. |
| 3. Cross-platform packaging | ✅ done | Linux tarball produced; Windows handled by portable build script. |
| 4. Unit tests | ✅ done | Smoke tests under `tests/` pass. |
| 5. CNN verification | ✅ done | `tetris_cnn.onnx` inference verified; latency captured. |
| 6. ImGui config UI | ✅ done | GLFW/ImGui overlay working. |
| 7. Documentation refresh | ⚠️ in_progress | README auto-updated via `scripts/task7_doc_purge.ps1`. |
| 8. Verification & backup | ✅ done | Repo + build artifacts backed up; GitHub mirror active. |

Key artifacts:
- Portable build root: `C:\TetrisOverlay`.
- PyInstaller output: `C:\TetrisOverlay\dist\MyOverlay.exe` (or custom `-TargetExeName`).
- Installer: `MyOverlay-Setup.exe` in repo root after `build_portable.ps1` succeeds.

---

## 2. Prerequisites on the New PC

1. **Windows 10/11** with PowerShell (default).
2. **Git for Windows** (includes Git Credential Manager). Accept default options.
3. **Visual C++ Redistributable 2015-2022** (most systems already have this; required for PyInstaller output).
4. **Inno Setup** is auto-downloaded by the build script if missing—no manual install required.

Optional (for development):
- Python 3.11.x (not required for the portable build because the script downloads the embeddable runtime).
- VS Code / preferred IDE.

---

## 3. Cloning the Repository

```powershell
# Choose a working folder first, e.g. D:\work or G:\dev
cd G:\dev

# Clone from GitHub
git clone https://github.com/gainey666/-tetris-overlay-test.git
cd -tetris-overlay-test

# Configure identity if needed
git config user.name "tacosneedlove"
git config user.email "gainey666@gmail.com"
```

If Git prompts for credentials, sign in with your GitHub username and Personal Access Token (PAT). Credential Manager will cache it.

---

## 4. Running Day-6 Automation Tasks (Optional)

All automation scripts live under `scripts/`. To re-run individual tasks:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\task1_log_tracker_cleanup.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\task5_cnn_verify.ps1
# ...etc
```

To run the full Day-6 master workflow:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_day6_all.ps1
```

`progress_log.json` will update as each task completes.

---

## 5. Building the Portable Overlay + Installer

### Default build (portable EXE + installer)
```powershell
Set-Location "G:\dev\-tetris-overlay-test"
.\scripts\build_portable.ps1 -TargetExeName "MyOverlay.exe"
```

What happens:
1. Cleans `C:\TetrisOverlay` and recreates `python`, `build`, `dist` subfolders.
2. Downloads Python 3.11 embeddable ZIP, enables `import site`, and bootstraps pip.
3. Installs runtime packages (`imgui`, `glfw`, `onnxruntime`, `numpy`, `pillow`, `tqdm`, `pyinstaller`).
4. Copies project assets (scripts, README, `models/tetris_cnn.onnx`, optional `bin/` if present).
5. Generates `run_overlay.py` driver and compiles it into a one-file EXE via PyInstaller.
6. If `-SkipInstaller` is **not** provided, downloads Inno Setup portable (if missing) and builds `MyOverlay-Setup.exe` in the repo root.

Artifacts:
- Portable EXE: `C:\TetrisOverlay\dist\MyOverlay.exe`
- Installer: `G:\dev\-tetris-overlay-test\MyOverlay-Setup.exe`

### Skipping the installer
```powershell
.\scripts\build_portable.ps1 -TargetExeName "Overlay.exe" -SkipInstaller
```

---

## 6. Deploying on End Users

1. Ship either the **portable EXE** (runs standalone) or the **installer** (`MyOverlay-Setup.exe`).
2. Installer flow copies the EXE to Program Files, adds Start Menu + Desktop shortcuts, and registers an uninstaller.
3. End users do **not** need Python, Git, or PowerShell.

---

## 7. Syncing Changes Between PCs

Always pull before you start, push after you finish.

```powershell
# Update local copy with remote changes
git pull origin main

# After editing files
git add -A
git commit -m "Describe your change"
git push origin main
```

If `git pull` reports conflicts:
1. Open the conflicted files (Git marks sections with `<<<<<<<` / `=======` / `>>>>>>>`).
2. Keep the desired content, delete conflict markers.
3. `git add <file>` for each resolved file, then `git commit`.
4. `git push origin main`.

Troubleshooting tips:
- If Git says "not a repository," ensure you’re inside the cloned folder.
- If credential prompts fail, open Windows Credential Manager, remove old entries for `github.com`, then run `git push` again.
- Large pushes may take a few minutes because the repo includes ONNX models and build artifacts.

---

## 8. Quick Checklist for a Fresh Machine

1. Install Git for Windows (Credential Manager on).
2. `git clone https://github.com/gainey666/-tetris-overlay-test.git`.
3. `cd -tetris-overlay-test`.
4. (Optional) Run `scripts\run_day6_all.ps1` to regenerate progress artifacts.
5. Run `scripts\build_portable.ps1` to produce the EXE and installer.
6. Distribute `C:\TetrisOverlay\dist\MyOverlay.exe` or `MyOverlay-Setup.exe` to testers/users.
7. Commit/push any changes back to GitHub when done.

---

Need help? Ping the assistant with the exact command output (especially for build, git, or installer errors) and we’ll debug from there.
