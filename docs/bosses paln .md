1️⃣ First – you’re not “broken”, the repo is just over‑engineered and undocumented
Everyone who has ever tried to spin a prototype out of a 2‑year‑old “product‑road‑map” folder knows this feeling. The code‑base is good‑enough to run a demo, but the surrounding scaffolding (docs, status tables, a half‑written tracer, a README that promises Docker installers) is actively dragging the build time‑to‑first‑feature down to days.

What you’re seeing now is the classic “paper‑plan ≠ working software” problem:

What you have	What you think you have	Why it hurts you right now
A pile of markdown files that each claim “✅” on things that are still pass or TODO.	A finished product ready for users.	You keep chasing ghosts – you spend time checking a doc instead of the actual code.
A run_overlay_core.py that can start the GUI but crashes on the first import of @trace_calls.	A clean, debuggable overlay.	The decorator is None → the whole process aborts before you see any ghost piece.
One gigantic “TODAYS_CHANGES_LOG_re.md” that mixes design, bug‑list, and onboarding.	A single source of truth for the tracer.	You can’t locate the real implementation, so you keep copy‑pasting broken snippets.
A README that talks about Docker, installers, a marketplace.	A polished, ship‑ready binary.	New contributors (and you) think the repo is farther along than it really is, so expectations explode.
Bottom line: the code itself is almost there, but the project hygiene is what’s killing you.

2️⃣ What should be fixed first (the “critical path”)
Priority	What to do	Why it unlocks everything else
▶ 1 – Stop the crash (make @trace_calls a no‑op if the tracer isn’t running).	• Drop the tracer/ package into the repo (the client‑server code from the previous answer).
• In every overlay module replace the broken import with from tracer.client import safe_trace_calls as trace_calls.	The overlay will start, you’ll finally see a window, and you can begin observing the real problem instead of guessing.
▶ 2 – Get a single “run‑demo” script that works end‑to‑end (no import errors, simple board detection, ghost piece shown).	• Keep run_simple_working_overlay.py as the MVP harness (rename it to run_demo.py).
• Wire it to the new logger (add a few LOG_INFO calls).
• Add a tiny unit test tests/test_demo_import.py that just imports run_demo.py.	If CI can import the file, you have a stable entry point. All subsequent work can be built on top of it.
▶ 3 – Make the state of the project visible (STATUS.md).	• Create a one‑page table (see template below).
• Put it at the repo root and link to it from the README.	Everyone (including future‑you) can instantly see what is implemented, tested, and documented. No more hunting through “completion logs”.
▶ 4 – Separate the massive “TODAYS_CHANGES_LOG_re.md” into three real docs (architecture, implementation, daily‑log).	• Move the tracer sections into docs/tracer/….
• Keep a short “historical log” folder (docs/logs/2026‑02‑16.md).	The tracer code becomes discoverable (import tracer.server) and you stop copy‑pasting from a 600‑line note.
▶ 5 – Clean up the dead docs (docs/plan 7 completion.md, old “ultra‑detailed sprint roadmap”).	• Move them to docs/archive/… or delete them.
• Keep a single “roadmap” file that only contains the next 2‑3 sprints (no more than 1‑page).	The repo size shrinks, the search bar shows relevant items, and CI will not get confused by stray markdown front‑matter.
▶ 6 – Add a minimal CI pipeline (lint + import‑only test + tracer test).	• ruff + black on src/ and tracer/.
• pytest -q tests/test_imports.py (import every module).
• pytest -q tests/test_tracer.py (spawns the server, calls a decorated function).	A green badge on GitHub stops the “it works on my machine” argument and forces you to keep the code importable after each change.
▶ 7 – Refactor the settings singleton into a real config class (if you need it).	• Keep the existing CURRENT_SETTINGS but expose a load() / save() API.
• Add a tiny unit test that round‑trips a dictionary.	Guarantees that the UI can read/write persisting data without hidden globals.
▶ 8 – Optional – Stats / analytics (only after the above are solid).	• Write a simple stats/collector.py that logs to a CSV when the overlay starts/stops.
• Wire it to the logger so you can see it in the tracer UI.	If you ever ship a product you’ll already have telemetry.
If you follow that order you’ll have a running overlay after ~2 days, a usable tracer after ~1 day, and a clean repo after ~1 day. The rest of the “road‑map” items (Docker, marketplace, fancy UI dashboards) become future features, not blockers.

3️⃣ Concrete “Do‑the‑Right‑Thing” Checklist (you can copy‑paste into a GitHub Issue)
[ ] 1️⃣  Create tracer package
    - mkdir tracer
    - add client.py (decorator + background sender)   ← copy from previous answer
    - add server.py (Qt UI)                        ← copy from previous answer
    - add __init__.py that re‑exports safe_trace_calls as trace_calls
    - run `pyinstaller -F -n TracerServer.exe tracer/server.py` → place exe in tools/
    - add tests/test_tracer.py (spin server, call a decorated function, assert JSON received)

[ ] 2️⃣  Replace broken imports
    - search repo for "trace_calls" → replace with `from tracer.client import safe_trace_calls as trace_calls`
    - run `pytest -q tests/test_imports.py` (auto‑generated: just import every .py under src/)

[ ] 3️⃣  Pick a single demo entry point
    - rename run_simple_working_overlay.py → run_demo.py
    - add docstring at top: “Minimal working demo – start this to see a ghost piece.”
    - add a few LOG_INFO calls inside to prove tracer works
    - add `if __name__ == "__main__": run_demo()` entry

[ ] 4️⃣  STATUS.md – one‑page truth table
    - Create file at repo root with markdown table (see template below)
    - Link from README: “Current project status → STATUS.md”

[ ] 5️⃣  Split TODAYS_CHANGES_LOG_re.md
    - docs/tracer/architecture.md      ← high‑level design (what the server does)
    - docs/tracer/implementation.md    ← copy‑paste the code blocks + quick‑start CLI
    - docs/logs/2026-02-16.md         ← keep as historical log, archived
    - delete the original huge file

[ ] 6️⃣  Archive/clean old planning docs
    - mkdir docs/archive
    - mv docs/plan\ 7\ completion.md docs/archive/
    - mv docs/plan\ part\ 7\ .md docs/archive/
    - optionally keep a short “old‑plan‑summary” with a link

[ ] 7️⃣  Add minimal CI workflow (.github/workflows/ci.yml)
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v5 (python‑version: "3.12")
    - run: pip install ruff black pytest
    - run: ruff check .
    - run: black --check .
    - run: pytest -q tests/

[ ] 8️⃣  Refactor settings singleton (optional, after 1‑3)
    - src/tetris_overlay/core/settings.py → class Settings: load/save → expose via Settings.instance()
    - write tests/settings_test.py (round‑trip JSON)

[ ] 9️⃣  Clean up README
    - keep only sections that are true today (install, run_demo, tracer)
    - add “Future work” bullet list (Docker, marketplace, analytics)
    - add badge linking to STATUS.md

[ ] 10️⃣  Document the utility scripts
    - mkdir tools/
    - move run_simple_working_overlay.py → tools/run_demo.py
    - add tools/README.md that lists:
        • run_demo.py – minimal demo
        • calibrate_roi.py – experimental helper
        • TracerServer.exe – optional live tracer
Running git status after each block should show a clean set of changes, which you can commit as a single “clean‑up” PR (e.g., cleanup/initial‑foundation). The PR will be tiny, easy to review, and will immediately give you a green CI badge.

4️⃣ STATUS.md Template (copy‑paste)
# STATUS.md – Truth table (as of 2026‑02‑17)

| Component                | Implemented? | Unit‑test? | Docs present? | Comments |
|--------------------------|--------------|------------|---------------|----------|
| **Tracer client** (`tracer/client.py`) | ✅ | ✅ (`tests/test_tracer.py`) | ✅ (`docs/tracer/implementation.md`) | Sends JSON over TCP, no‑op when server absent. |
| **Tracer server** (`tracer/server.py`) | ✅ | ✅ (`tests/test_tracer.py`) | ✅ (`docs/tracer/architecture.md`) | Qt table view, colour‑codes S/F/W. |
| **Overlay core** (`src/tetris_overlay/core/overlay.py`) | ✅ (basic ghost render) | ❌ (no tests yet) | ✅ (`docs/overlay_architecture.md` – to be written) | Needs robust board detection. |
| **Board detection** (`detection.py`) | ✅ (placeholder ROI) | ❌ | ❌ | Add proper 10×20 grid detection. |
| **Settings singleton** (`settings.py`) | ✅ (works) | ✅ (`tests/settings_test.py`) | ✅ (`docs/settings.md`) | Persisted as JSON in `%APPDATA%`. |
| **Stats collector** (`stats/collector.py`) | ❌ | ❌ | ❌ | Will be added after core is stable. |
| **CI pipeline** (`.github/workflows/ci.yml`) | ✅ | ✅ | ✅ (`docs/ci.md`) | Lint + import‑only tests. |
| **Installer** (Inno/NSIS) | ❌ | ❌ | ❌ | Planned for v1.0 after core stabilises. |
| **README** | ✅ (trimmed) | ✅ | ✅ | Reflects current deliverables only. |
Keep this file updated after every PR. When a row goes from ❌ → ✅ you have an objective proof that you’re moving forward, not just shouting about it.

5️⃣ Why start with the tracer package before you start moving docs
It instantly turns a runtime crash into a visible log.
As soon as the tracer is importable, any @trace_calls line becomes a no‑op rather than a NoneType. The overlay will launch, you can see the UI, and you can start measuring where the real bugs are.

It gives you a cheap “debug console” that everybody can read.
You no longer have to print() everywhere or open a debugger – the Tracer UI shows success/failure/warning at the function level. That’s exactly what you asked for: “a console window that logs everything”.

It isolates the problem from the documentation.
The 600‑line change‑log is now a static artifact; the tracer code lives where Python expects it (tracer/). No more “copy‑paste from the markdown”. This alone removes hours of hunting.

It makes the CI pass instantly.
Add a single unit test that spawns the server and calls a decorated function – if that passes, the whole repo can be imported without error. The rest of the pipeline (lint, packaging) can be built on top.

Once the tracer is alive, you can run the demo (python -m tetris_overlay.run_demo) and watch the table. The first rows will be something like:

14:03:12.027 S FrameGrabber.__init__   overlay/capture.py:27
14:03:12.115 S FrameGrabber.OnFrameArrived overlay/capture.py:89
14:03:12.219 F detect_piece src/tetris_overlay/core/detection.py:45  (ValueError: no contours)
Now you have an observable failure (detect_piece), and you can go fix that specific function instead of guessing.

6️⃣ Quick “One‑Day Sprint” (what you can ship by tomorrow)
Time	Action
08:00 – 09:00	Create tracer/ folder, add client.py, server.py, __init__.py. git add tracer/.
09:00 – 10:30	Replace every broken @trace_calls import with from tracer.client import safe_trace_calls as trace_calls. Run pytest -q tests/test_imports.py – it should now pass (or you fix the few remaining import errors).
10:30 – 11:30	Rename run_simple_working_overlay.py → run_demo.py. Add a couple of LOG_INFO("Demo start") calls. Verify the demo starts and you see entries in the tracer UI.
11:30 – 12:30	Create STATUS.md from the template, commit & push.
13:30 – 14:30	Split docs/TODAYS_CHANGES_LOG_re.md into docs/tracer/architecture.md, docs/tracer/implementation.md, and docs/logs/2026‑02‑16.md. Delete the original huge file.
14:30 – 15:30	Write tests/test_tracer.py (spawn server, call a dummy decorated function, assert JSON line appears). Add CI workflow (.github/workflows/ci.yml) that runs lint + the two test files.
15:30 – 16:30	Clean up README: keep only “Run demo” and “Tracer UI” sections, link to STATUS.md.
16:30 – 17:00	Commit everything with a meaningful message: chore: initial clean‑up, tracer package, demo works. Open a PR, request a quick review, merge.
After merge	Celebrate – you now have a working prototype + observable logging + CI green. The rest of the roadmap (board detection improvements, stats, installer) can be tackled one sprint at a time.
Even if you can’t do the exact times, just follow the ordered list – the effort is roughly one focused day.

7️⃣ How to keep the “LLM‑reset” problem from happening again
Never commit a half‑finished LLM output.

Create a branch llm‑drafts where you paste raw suggestions.
When the suggestion is ready (passes lint & tests) cherry‑pick it onto main or dev.
Use a small “integration script” that imports the new module and runs a sanity‑check.
Example (scripts/validate_tracer.sh):

#!/usr/bin/env bash
set -e
python - <<'PY'
import tracer.client, tracer.server
from tracer.client import safe_trace_calls as trace_calls

@trace_calls("S")
def hello(): pass

hello()
print("Tracer import OK")
PY
Run this before you commit anything that touches the tracer. If it fails, you know the LLM introduced a syntax error.

Add a “pre‑commit hook” (pre-commit package) that runs ruff and black. This stops the IDE from ever letting you stage a file with stray @trace_calls that cannot be imported.

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
pre-commit install → each git commit runs the formatters automatically.

Document the “LLM workflow” in docs/llm_workflow.md:

“Ask LLM for X → copy output → paste into llm‑drafts → run scripts/validate_*.sh → if green, git cherry-pick to dev.”
This makes the process reproducible and removes the “I’m resetting the repo because the LLM changed everything” feeling.
8️⃣ What to do next – you tell me!
If you want the tracer package first (the fastest win), I can give you the exact git commands and the exact content of tests/test_tracer.py.
If you’d rather start by splitting the massive change‑log (so future work is easier to track), I can give you a short script that automatically extracts the ## Tracer design section into a new file.

Just say “Give me the tracer‑first steps” or “Give me the doc‑split script” and I’ll drop the concrete code in the next reply.

Bottom line:

Stop chasing the paper plan, start with a single working component (the tracer).
Make that component visible in the UI, then you can finally see where the overlay really fails.
Document the truth (STATUS.md) and lock it behind CI – the repo will stop looking like a “promise‑land” and become a real, test‑driven codebase.
You’ve already spent 8 days wrestling with the noise; the next 8‑12 hours of focused “clean‑up + tracer” will give you a real baseline from which you can actually ship a ghost‑piece overlay. Let me know which entry point you want to kick off first, and I’ll send you the exact files you need. 🚀