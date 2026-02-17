Below is a step‑by‑step “clean‑up playbook” that will:

Tell you which part of the tree is the “real product” (the one you will ship).
Show you how to isolate the other pieces (C++ prototype, old design docs, the huge vcpkg/ copy) so they no longer bloat the repo, slow down search, or waste disk space.
Give you concrete Git commands, scripts and tooling you can run today to make the repository lean, fast to clone, and easy to navigate.
Explain how to keep the best bits of each project (e.g., keep the fast DXGI capture code, keep the Python GUI, keep the useful docs) while eliminating duplication.
You can copy‑paste the commands, adapt the paths, and run them in a fresh clone. All actions are reversible (they are just git mv / git rm / branch moves), so you can always roll back if you spot a mistake.

1️⃣ Decide the “authoritative” product
Project	What it does	Why you probably want it as the main repo
-tetris-overlay-test/	Full‑featured Python overlay (GUI, settings, analytics, tracer, installers).	Already documented, has CI, pip‑installable, works on Windows out‑of‑the‑box.
temp_backup/tetris_overlay/ (C++ DXGI)	High‑performance capture + ONNX‑based AI pipeline (sub‑5 ms).	Technically superior but a separate language/runtime; currently lives in a temporary folder, no packaging, no tests.
temp_backup/tetris-overlay/ (early design docs)	Vision / architecture markdown from the first prototype.	No code, only design ideas.
vcpkg/	A full clone of Microsoft’s package manager (≈ 2 GB).	Not a dependency of the product; you only need the port manifests you might have tweaked.
Recommendation:

Keep -tetris-overlay-test/ as the canonical repo that you ship to users (pip package, installer, docs).
Treat the C++ overlay as a separate, self‑contained repository (tetris-overlay-cpp/), possibly linked as a git submodule if you ever need to build both from one place.
Archive the old design docs inside the main repo’s docs/legacy/ folder.
Remove the massive vcpkg/ copy; replace it with a submodule (or an external install script) that points to the official upstream.
2️⃣ High‑level clean‑up roadmap
Phase	Goal	Approx. effort	Outcome
Phase 0 – Safety net	Create a backup branch that contains the current state (so you can always revert).	5 min	git checkout -b backup_before_cleanup
Phase 1 – prune & archive	Move / delete the three “extra” trees (C++, old design docs, vcpkg).	1 day	Repo size drops from ~2 GB → < 200 MB; search/indexing becomes instant.
Phase 2 – refactor the Python project	Consolidate duplicate scripts, move truly obsolete runner files to legacy/, tighten the test suite.	½ day	Cleaner src/ tree, faster CI, easier navigation.
Phase 3 – create a C++ overlay repo	Extract temp_backup/tetris_overlay/ into its own Git repository, keep a submodule link.	½ day	Independent build pipeline; you can version the C++ part separately.
Phase 4 – finalize docs & CI	Merge the early design markdown into docs/, update README with links to the new submodule, add .gitignore/.gitattributes for large files.	½ day	A single source‑of‑truth README, no stray files.
Phase 5 – optional – host vcpkg elsewhere	Replace the local copy with a submodule that points to the official vcpkg repo (or drop it entirely).	15 min	Repo stays tiny; developers can still run vcpkg if they need it.
3️⃣ Detailed commands & scripts
Below are ready‑to‑run snippets. Run them in the root of the cloned repo (c:\dev\stack\tetris‑again‑tetris-overlay-test).

⚠️ IMPORTANT – make sure you have a clean working tree (git status shows nothing to commit) before you start. If you have uncommitted changes, stash them (git stash) first.

3.1 Phase 0 – backup branch
git checkout -b backup_before_cleanup
git push -u origin backup_before_cleanup   # keep a remote copy just in case
git checkout main
Now you can always go back with git checkout backup_before_cleanup.

3.2 Phase 1 – prune the three extra trees
3.2.1 Move the C++ prototype out of temp_backup into its own repo
# 1️⃣ Create a fresh repo on GitHub (e.g. gainey666/tetris-overlay-cpp)
#    – give it a short README that points to the Python repo.

# 2️⃣ From your local machine:
cd temp_backup               # go into the folder that contains tetris_overlay/
git init                     # make it a standalone repo
git add .                    # stage everything
git commit -m "Initial import of C++ DXGI overlay (v2) – independent repo"
# Add the remote you just created on GitHub
git remote add origin https://github.com/gainey666/tetris-overlay-cpp.git
git push -u origin master

# 3️⃣ Return to the main repo and delete the local copy
cd ../../                    # back to repo root
git rm -r --cached temp_backup/tetris_overlay   # remove from index (keep .gitignore for safety)
git commit -m "Extract C++ overlay to its own repository (tetris-overlay-cpp)"
Result: The C++ code lives in a separate repo and the main repo no longer contains ~200 MB of C++ source and build artifacts.

If you still need a tiny reference to it, add it as a submodule:

git submodule add https://github.com/gainey666/tetris-overlay-cpp.git cpp_overlay
git commit -m "Add C++ overlay as submodule (optional) for developers"
The submodule folder (cpp_overlay/) will be just a pointer (≈ 1 KB) until a developer runs git submodule update --init.

3.2.2 Archive the early design docs (temp_backup/tetris-overlay/)
# Move the markdown files into the Python repo's docs/legacy folder
mkdir -p docs/legacy
git mv temp_backup/tetris-overlay/project.md docs/legacy/
git mv temp_backup/tetris-overlay/system.md  docs/legacy/
git commit -m "Archive early design docs in docs/legacy"
git rm -r --cached temp_backup/tetris-overlay   # remove the now‑empty folder
git commit -m "Delete empty temp_backup/tetris-overlay folder"
If you ever need to reference them, they live under docs/legacy/ and are part of the repo history.

3.2.3 Drop the full vcpkg copy (≈ 1.8 GB)
You almost never want a whole external source tree inside your project. Do one of the following:

Option A – Submodule the official vcpkg repo (keeps only the git metadata).

# First, make sure you have no local changes inside vcpkg/
git rm -r --cached vcpkg
git commit -m "Remove embedded vcpkg copy (will be submodule)."

# Add it back as a submodule pointing to the official upstream:
git submodule add https://github.com/microsoft/vcpkg.git vcpkg
git commit -m "Add vcpkg as submodule (reference only)."
Now the folder vcpkg/ contains only the .git directory linking to the official repo; the massive source files are not stored in your repository. When a developer needs them, they run:

git submodule update --init --recursive
Option B – Remove completely and provide an install script

If you never customized any ports, you can just delete the folder and tell users to install vcpkg themselves.

git rm -r --cached vcpkg
git commit -m "Delete embedded vcpkg; users should install it locally"
Add a short script under tools/install_vcpkg.sh (or a README entry) explaining:

# tools/install_vcpkg.sh
git clone https://github.com/microsoft/vcpkg.git %USERPROFILE%\vcpkg
%USERPROFILE%\vcpkg\bootstrap-vcpkg.bat
Pick the option that matches your workflow. Most teams go with the submodule, because it still gives you a stable reference to any custom ports you added.

3.3 Phase 2 – tidy the Python overlay (-tetris-overlay-test)
3.3.1 Move truly obsolete runner scripts into legacy/
mkdir -p legacy
# List of files that are not part of the “official” entry points.
# (You already have `run_simple_working_overlay.py`, `run_real_tetris_overlay.py`,
# `run_threaded_overlay.py`, `run_working_tetris_overlay.py` – keep those.)
# Anything else that starts with “run_” and is not one of the four above goes to legacy.

git mv run_legacy_demo.py legacy/
git mv run_experimental_xyz.py legacy/
# repeat for all scripts you deem obsolete

git commit -m "Move old runner scripts to legacy/ (keep only four official entry points)."
3.3.2 Consolidate duplicated UI / settings code
If you notice that ui/settings.py and ui/settings_dialog.py duplicate data‑structures, do a quick refactor:

# Example: pull the Settings data model into a single file
mv src/tetris_overlay/core/settings.py ui/settings_model.py
# Update imports (search‑and‑replace):
grep -R "settings.py" -n . | cut -d: -f1 | while read f; do
    sed -i 's/from .*settings import /from ui.settings_model import /' "$f"
done
git commit -m "Consolidate Settings model into ui/settings_model.py"
(You can run a similar script for any duplicated logic you find.)

3.3.3 Trim the test suite
Delete any image‑heavy tests that are flaky (e.g., test_game_images.py).
Keep only logic‑focused unit tests that run quickly (under a second each).
git rm tests/test_game_images.py
git rm tests/simple_game_test.py   # if they just load big PNGs
git commit -m "Remove flaky / heavy image tests – keep lightweight unit tests."
If you need those tests for documentation, move them to docs/legacy/tests/ (they won’t be part of CI).

3.3.4 Add a .gitattributes to keep binaries out of the repo
If you ever store large binary artifacts (e.g., screenshots) inside assets/, mark them for Git LFS:

# Install Git LFS if you haven’t yet
git lfs install

# Tell Git LFS to track PNG/JPG under assets/
echo "assets/*.png filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
echo "assets/*.jpg filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
git add .gitattributes
git commit -m "Add LFS tracking for image assets"
All future commits of those files will be stored as pointers, keeping the repository size small.

3.4 Phase 3 – finalize docs and CI
3.4.1 Merge the early design markdown
# Move the old design docs into /docs/legacy/
mkdir -p docs/legacy
git mv temp_backup/tetris-overlay/project.md docs/legacy/
git mv temp_backup/tetris-overlay/system.md  docs/legacy/
git commit -m "Archive early design docs in docs/legacy"
Add a small section to the README that points to them:

## 📚 Legacy Design Docs
Older design sketches and system diagrams are kept for reference in `docs/legacy/`. They are not part of the current implementation but may be useful for historical context.
3.4.2 Update the README with submodule notes
If you kept the C++ overlay as a submodule, add a “Optional – C++ high‑performance overlay” section:

## 🚀 Optional – High‑Performance C++ Overlay
A C++ implementation that captures the game window via DXGI and renders with Direct2D is available as a submodule:

```bash
git submodule update --init --recursive   # pulls the C++ source into ./cpp_overlay
You can build it with CMake:

cd cpp_overlay
mkdir build && cd build
cmake .. -A x64
cmake --build . --config Release
(See cpp_overlay/README.md for full instructions.)


#### 3.4.3  Clean CI config (remove vcpkg steps)

If your CI pipeline currently runs something like:

```yaml
- name: Install vcpkg
  run: git clone --depth 1 https://github.com/microsoft/vcpkg.git
Replace it with a simple git submodule update --init (or remove it entirely if you decided to delete vcpkg).

- name: Checkout submodules
  run: git submodule update --init --recursive
4️⃣ Quick‑check after each phase
Check	Command	Expected result
Repo size	git count-objects -vH	size: < 200 MB (instead of > 2 GB)
Clone time	Clone a fresh copy on another machine (git clone …)	Should finish in seconds, not minutes.
Search speed	Open VS Code or any IDE and type run_standalone_tracer	Zero results, no stale files indexed.
CI build	Push a commit, watch GitHub Actions	Fails only on real bugs, not on missing folders.
Submodule sync	Clone fresh repo with --recurse-submodules	C++ code appears in cpp_overlay/ (or not, if you removed it).
Large‑file handling	git lfs ls-files	Lists only the assets you deliberately tracked.
5️⃣ TL;DR – One‑run “do it now” script (optional)
If you want to execute everything in one go (make sure you have a fresh backup branch first!), copy the block below into tools/clean_up_repo.sh, make it executable (chmod +x tools/clean_up_repo.sh), and run it.

#!/usr/bin/env bash
set -euo pipefail

# ------------------------------------------------------------
# 0️⃣ Safety – create a backup branch (you can delete later)
# ------------------------------------------------------------
git checkout -b backup_before_cleanup
git push -u origin backup_before_cleanup
git checkout main

# ------------------------------------------------------------
# 1️⃣ Extract C++ overlay into its own repo and submodule
# ------------------------------------------------------------
mkdir -p temp_cpp_repo
cd temp_backup/tetris_overlay
git init
git add .
git commit -m "Initial import of C++ DXGI overlay"
git remote add origin https://github.com/gainey666/tetris-overlay-cpp.git
git push -u origin master
cd ../../..
git rm -r --cached temp_backup/tetris_overlay
git commit -m "Extract C++ overlay to separate repo (tetris-overlay-cpp)"
git submodule add https://github.com/gainey666/tetris-overlay-cpp.git cpp_overlay
git commit -m "Add C++ overlay as submodule (optional)"

# ------------------------------------------------------------
# 2️⃣ Archive early design docs
# ------------------------------------------------------------
mkdir -p docs/legacy
git mv temp_backup/tetris-overlay/project.md docs/legacy/
git mv temp_backup/tetris-overlay/system.md docs/legacy/
git commit -m "Archive early design docs in docs/legacy"
git rm -r --cached temp_backup/tetris-overlay
git commit -m "Remove empty temp_backup/tetris-overlay folder"

# ------------------------------------------------------------
# 3️⃣ Replace giant vcpkg copy with submodule (or delete)
# ------------------------------------------------------------
git rm -r --cached vcpkg
git commit -m "Remove embedded vcpkg source tree"
git submodule add https://github.com/microsoft/vcpkg.git vcpkg
git commit -m "Add vcpkg as submodule (reference only)"

# ------------------------------------------------------------
# 4️⃣ Move old runner scripts to legacy/
# ------------------------------------------------------------
mkdir -p legacy
# Keep the four official entry points, move anything else that starts with run_
for f in run_*.py; do
    case "$f" in
        run_simple_working_overlay.py|run_real_tetris_overlay.py|run_threaded_overlay.py|run_working_tetris_overlay.py) ;;
        *) git mv "$f" legacy/ ;;
    esac
done
git commit -m "Move deprecated runner scripts to legacy/"

# ------------------------------------------------------------
# 5️⃣ Clean up heavy tests
# ------------------------------------------------------------
git rm -f tests/test_game_images.py tests/simple_game_test.py
git commit -m "Remove heavy / flaky image tests"

# ------------------------------------------------------------
# 6️⃣ Add .gitattributes for large assets (optional)
# ------------------------------------------------------------
echo "assets/*.png filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
echo "assets/*.jpg filter=lfs diff=lfs merge=lfs -text" >> .gitattributes
git add .gitattributes
git commit -m "Add LFS tracking for image assets"

# ------------------------------------------------------------
# 7️⃣ Final sanity check
# ------------------------------------------------------------
git gc --prune=now --aggressive
echo "=== Clean‑up complete! ==="
echo "Repo size:"
git count-objects -vH
Run it once, push the changes, and watch the repo shrink dramatically.
If you spot anything you didn’t intend to delete, simply git checkout backup_before_cleanup and cherry‑pick the pieces you still need.

6️⃣ What to do next (your call)
If you want…	Suggested next sprint
A. Faster, more reliable Python overlay	Finish Phase 2 (remove dead scripts, tighten tests), then start the board‑detection & ghost‑piece work (the core product feature).
B. Keep the C++ version for power users	Treat it as a separate project (tetris-overlay-cpp). Add a thin Python wrapper (e.g., a small ctypes shim) if you ever need to call it from the Python UI.
C. Ship a one‑click installer	After Phase 2 is clean, move to Phase 4 (CI packaging, Inno Setup, signed installer).
D. Reduce repo footprint for collaborators	Finish Phase 1 (remove vcpkg, archive docs), push the new submodule changes, inform the team to run git submodule update --init.
Let me know which of those you’d like to start with, and I’ll draft the exact code changes / CI snippets you need for the chosen path. 🎯🚀