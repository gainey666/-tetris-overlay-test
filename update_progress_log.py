import json, pathlib, datetime

log_path = pathlib.Path('progress_log.json')
if not log_path.exists():
    raise SystemExit('progress_log.json not found – run make_progress_log.py first')

log = json.loads(log_path.read_text())

# Full task list for Day 6 – update as needed
tasks = [
    {"task_id": 1, "name": "Log & tracker files", "status": "todo", "started_at": None, "finished_at": None, "note": None},
    {"task_id": 2, "name": "CI pipeline", "status": "todo", "started_at": None, "finished_at": None, "note": None},
    {"task_id": 3, "name": "Cross‑platform packaging", "status": "todo", "started_at": None, "finished_at": None, "note": None},
    {"task_id": 4, "name": "Unit‑test suite", "status": "todo", "started_at": None, "finished_at": None, "note": None},
    {"task_id": 5, "name": "Optional CNN backend", "status": "todo", "started_at": None, "finished_at": None, "note": None},
    {"task_id": 6, "name": "User‑config UI", "status": "todo", "started_at": None, "finished_at": None, "note": None},
    {"task_id": 7, "name": "Documentation polish", "status": "todo", "started_at": None, "finished_at": None, "note": None},
    {"task_id": 8, "name": "Verification & backup", "status": "todo", "started_at": None, "finished_at": None, "note": None}
]

log['tasks'] = tasks
log_path.write_text(json.dumps(log, indent=2))
print('progress_log.json updated with full task list')
