#!/usr/bin/env python3
"""
pre_write_code hook for Windsurf Cascade.

What it does (default = rename):
* If the target file already exists, move it to a versioned name
  (file_v1.py, file_v2.py, …) inside a .backup directory.
* Update all Python import statements that refer to the old name.
* If CASCADE_FILE_POLICY=delete → back‑up then delete the file.
* If CASCADE_FILE_POLICY=ignore → abort the write (exit 2).

The hook receives a JSON object on stdin:
{
  "agent_action_name": "pre_write_code",
  "tool_info": {
    "file_path": "/abs/path/to/file.py",
    "edits": [...]
  }
}
"""

import json
import os
import pathlib
import shutil
import re
import sys
from datetime import datetime

# ----------------------------------------------------------------------
# Config – can also be overridden with an env‑var before launching Windsurf
POLICY = os.getenv("CASCADE_FILE_POLICY", "rename").lower()  # rename|delete|ignore
# ----------------------------------------------------------------------


def _log(msg: str) -> None:
    """Write a short line to stdout – useful for debugging if you enable show_output."""
    print(f"[Cascade‑Hook] {msg}", file=sys.stderr)


def _backup_path(original: pathlib.Path) -> pathlib.Path:
    """Return a path inside a .backup folder where we can safely stash the old file."""
    backup_dir = original.parent / ".backup"
    backup_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return backup_dir / f"{original.name}.{ts}.bak"


def _rename_with_version(p: pathlib.Path) -> pathlib.Path:
    """Rename p → p_v<N>.ext where N is the smallest integer not in use."""
    stem, suffix = p.stem, p.suffix
    i = 1
    while True:
        candidate = p.with_name(f"{stem}_v{i}{suffix}")
        if not candidate.exists():
            break
        i += 1
    p.rename(candidate)
    return candidate


def _update_imports(old_name: str, new_name: str) -> None:
    """
    Walk the whole repo and replace plain imports of the old module.
    Handles:
        import old_name
        from old_name import X
    It does **not** touch strings or comments (good enough for most projects).
    """
    old_mod = old_name.rstrip(".py")
    new_mod = new_name.rstrip(".py")
    pattern = re.compile(rf"\b{re.escape(old_mod)}\b")
    root = pathlib.Path(".")
    for py_file in root.rglob("*.py"):
        try:
            text = py_file.read_text(encoding="utf-8")
        except Exception:
            continue
        if old_mod not in text:
            continue
        new_text = pattern.sub(new_mod, text)
        if new_text != text:
            py_file.write_text(new_text, encoding="utf-8")
            _log(f"Updated imports in {py_file}")


def main() -> int:
    # 1️⃣ read the JSON payload from stdin
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        _log(f"Invalid JSON from Cascade: {exc}")
        return 1

    tool_info = payload.get("tool_info", {})
    file_path = tool_info.get("file_path")
    if not file_path:
        _log("No file_path supplied – nothing to do.")
        return 0

    target = pathlib.Path(file_path)

    if not target.exists():
        # File does not exist – nothing to block/rename
        return 0

    # ------------------------------------------------------------
    # Existing file – decide what to do based on POLICY
    # ------------------------------------------------------------
    if POLICY == "ignore":
        _log(f"Ignoring write to existing {target} as per policy")
        # Exit 2 tells the hook system to block the action
        return 2

    if POLICY == "delete":
        backup = _backup_path(target)
        shutil.move(str(target), str(backup))
        _log(f"Deleted {target} → backup saved at {backup}")
        return 0

    # Default == rename (keeps old version & rewrites imports)
    new_name = _rename_with_version(target)
    _log(f"Renamed existing {target} → {new_name}")
    _update_imports(target.name, new_name.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
