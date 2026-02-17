"""Utility script to rewrite legacy tracer imports."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERN_FULL = "from tracer.client import safe_trace_calls as trace_calls"
PATTERN_SIMPLE = "from tracer.client import safe_trace_calls as trace_calls"
REPLACEMENT = "from tracer.client import safe_trace_calls as trace_calls"

updated = 0
for file_path in ROOT.rglob("*.py"):
    text = file_path.read_text(encoding="utf-8")
    new_text = text.replace(PATTERN_FULL, REPLACEMENT).replace(PATTERN_SIMPLE, REPLACEMENT)
    if new_text != text:
        file_path.write_text(new_text, encoding="utf-8")
        updated += 1

print(f"Updated {updated} files.")
