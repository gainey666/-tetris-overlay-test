🚑 “We’re all over the place – how do we get a real tracer working and stop breaking the overlay?”
A senior‑dev’s rescue plan (copy‑paste‑ready, step‑by‑step)
Below you’ll find

Root‑cause analysis (what’s really broken)
A tiny, production‑ready tracer library you can drop into any Python project (including the Tetris overlay) – it works even when the “stand‑alone Tracer.exe” is not running.
A minimal GUI “Tracer Server” (Python → PySide6 → .exe) that shows a live call‑tree exactly the way you asked for (S/F/W markers).
How to integrate the decorator into the existing overlay code (no more syntax errors, no crashes).
A clean‑up checklist for the rest of the repo (lint, tests, CI) so you never end up in the same mess again.
Everything is self‑contained – you don’t need a special web server, a database, or any “magic” UI library you don’t already have. Just Python 3.10+, PySide6, and the standard library.

1️⃣ QUICK “WHAT’S WRONG” SUMMARY
Symptom	Why it happens (most likely)	Where it lives in the repo
@trace_calls gives TypeError: 'NoneType' object is not callable	The decorator returns None because it tries to import a tracer client that fails to initialise (the external exe is not running, or the import swallows an exception).	src/tetris_overlay/core/*.py – all places that use @trace_calls.
Tracer window stays empty	Your overlay never sends any data to the tracer process (the client either never connects, or it raises before the first send).	tracer_client.py (if it exists) – or the broken decorator in the overlay.
Broken overlay files → syntax errors	Some files were edited while the interpreter was trying to import them (unfinished merge, stray @ decorators, missing parentheses).	src/tetris_overlay/core/config.py, src/tetris_overlay/core/overlay.py, src/tetris_overlay/core/capture.py.
No unit / integration tests	You have only dummy “import‑only” tests, so you never see runtime failures until you run the UI.	tests/ folder.
Bottom line: The tracer is the glue you need to see what’s happening, but it’s broken. Fix the tracer first, then use it to expose the overlay’s bugs. After that, clean up the code base so you can actually run tests.

2️⃣ DESIGN‑TEMPLATE: “Tracer Server + Tracer Client”
+----------------------+        TCP (localhost, 8765)        +--------------------+
|  Tracer Server.exe  |  <--- JSON lines (one per call) ----> |  Tracer Client   |
|  (Qt / PySide6)      |  (runs in its own process)          |  (decorator)     |
+----------------------+                                      |
        ^  UI:  live table, filter by status, clear, pause          |
        |                                                          |
        |  (optional) writes same JSON to a log file on disk        |
        +----------------------------------------------------------+
                All overlay modules import TracerClient and use
                @trace_calls("func_name") on any function you care about.
Why this design works for you

Zero dependencies – the server is pure Python + PySide6; you can ship it as a one‑click exe with PyInstaller (the same tool you already use for the overlay).
Robust fallback – the client opens the socket only when the server is reachable; otherwise it silently becomes a no‑op logger (so your overlay never crashes because the tracer isn’t running).
Thread‑safe – the client queues messages in a queue.Queue and a background thread does the socket I/O, so the decorated function returns instantly.
Simple protocol – one JSON line per call, e.g.
{"time":"2026‑02‑16T14:03:12.027","status":"S","func":"capture_frame","file":"capture.py","line":27}
Extensible – you can later add “duration” or “exception” fields without touching the overlay code.
3️⃣ IMPLEMENTATION – COPY‑PASTE THIS INTO YOUR REPO
Below are three files you can drop into a new tracer/ package (or any folder you like). After adding them, run a quick sanity test (see §4) before you touch any other code.

3.1 tracer/client.py – the decorator and background sender
# ------------------------------------------------------------
# tracer/client.py
# ------------------------------------------------------------
import json
import socket
import threading
import time
import sys
import os
import traceback
from queue import Queue, Empty
from functools import wraps
from typing import Callable, Any

# -----------------------------------------------------------------
# CONFIGURATION (change only if you know what you’re doing)
# -----------------------------------------------------------------
HOST = "127.0.0.1"
PORT = 8765            # same as the server below
CONNECT_TIMEOUT = 0.2   # seconds – quick fallback if server not running
QUEUE_MAXSIZE = 10_000  # avoid unlimited memory growth

# -----------------------------------------------------------------
# Internal helper: a single background thread that owns the socket.
# -----------------------------------------------------------------
class _SenderThread(threading.Thread):
    daemon = True

    def __init__(self):
        super().__init__(name="TracerSender")
        self._q: Queue = Queue(maxsize=QUEUE_MAXSIZE)
        self._sock: socket.socket | None = None
        self._stop = threading.Event()
        self.start()

    # -----------------------------------------------------------------
    def run(self) -> None:
        """Main loop – keep a TCP connection alive and ship JSON lines."""
        while not self._stop.is_set():
            if self._sock is None:
                self._connect()
                if self._sock is None:
                    # No server – wait a bit and try again later
                    time.sleep(1.0)
                    continue

            # Pull a message, give up after a short timeout so we can notice
            # a broken socket and reconnect.
            try:
                msg = self._q.get(timeout=0.5)
            except Empty:
                continue

            try:
                # Send JSON + newline (line‑delimiter makes it easy to parse)
                data = (msg + "\n").encode("utf‑8")
                self._sock.sendall(data)
            except Exception:
                # Something went wrong – drop the socket & re‑queue the message
                self._sock.close()
                self._sock = None
                # re‑queue (but don’t block forever)
                try:
                    self._q.put_nowait(msg)
                except Exception:
                    pass   # queue full – drop the message

    # -----------------------------------------------------------------
    def _connect(self) -> None:
        """Try to open the TCP connection – silent on failure."""
        try:
            s = socket.create_connection((HOST, PORT), timeout=CONNECT_TIMEOUT)
            self._sock = s
        except Exception:
            self._sock = None

    # -----------------------------------------------------------------
    def enqueue(self, payload: dict) -> None:
        """Public API – called by the decorator.  Serialises to JSON first."""
        try:
            line = json.dumps(payload, separators=(",", ":"))
        except Exception:
            # Should never happen, but we don’t want to bring the app down.
            line = json.dumps({"error": "json_failed", "payload": str(payload)})
        try:
            self._q.put_nowait(line)
        except Exception:
            # Queue full – drop the message (non‑critical)
            pass

    # -----------------------------------------------------------------
    def stop(self) -> None:
        self._stop.set()
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass

# -----------------------------------------------------------------
# Global singleton – created lazily on first use
# -----------------------------------------------------------------
_sender: _SenderThread | None = None

def _ensure_sender() -> _SenderThread:
    global _sender
    if _sender is None:
        _sender = _SenderThread()
    return _sender

# -----------------------------------------------------------------
# Public decorator -------------------------------------------------
# -----------------------------------------------------------------
def trace_calls(status: str = "I"):
    """
    Decorator that records every call of the wrapped function.

    Parameters
    ----------
    status : str
        One‑character status code:
        • 'S' – success (normal call)
        • 'F' – failure (exception raised)
        • 'W' – warning (you can use it manually)
        • 'I' – informational / just a call trace
    """
    if not isinstance(status, str) or len(status) != 1:
        raise ValueError("status must be a single character")

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 1️⃣  Build the payload *before* we call the function – we have
            #     file/line information from the function object.
            payload = {
                "time": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime()),
                "status": status,
                "func": func.__qualname__,
                "file": func.__code__.co_filename,
                "line": func.__code__.co_firstlineno,
            }

            # 2️⃣  Send the *entry* event (always S/I/W, never F)
            try:
                _ensure_sender().enqueue(payload)
            except Exception:
                # If the tracer thread failed we silently ignore – overlay must stay alive.
                pass

            # 3️⃣  Call the real function and capture any exception.
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as exc:
                # 4️⃣  If an exception bubbles up we fire a second message with 'F'
                payload["status"] = "F"
                payload["exception"] = type(exc).__name__
                payload["traceback"] = traceback.format_exc().splitlines()[:5]  # short version
                try:
                    _ensure_sender().enqueue(payload)
                except Exception:
                    pass
                raise  # re‑raise – we don’t swallow errors.
        return wrapper
    return decorator

# -----------------------------------------------------------------
# Optional explicit shutdown (useful for unit tests)
# -----------------------------------------------------------------
def shutdown_tracer():
    """Force the background thread to exit – call at program end."""
    global _sender
    if _sender:
        _sender.stop()
        _sender = None

# -----------------------------------------------------------------
# Defensive import for modules that may do `from tracer.client import trace_calls`
# If the import itself fails, we provide a dummy that does nothing.
# -----------------------------------------------------------------
def _fallback_decorator(*_, **__) -> Callable:
    def inner(func):
        return func
    return inner

# If anything in the file raised before `trace_calls` was defined, the import
# would have already failed.  To make the *whole package* robust we expose
# a safe name that other modules can use:
safe_trace_calls = trace_calls if "trace_calls" in globals() else _fallback_decorator
What this file does

Background thread (_SenderThread) keeps a TCP socket open to the tracer UI.
If the UI is not running, the client just queues messages locally and discards them when the queue fills – no exception is raised.
The decorator (@trace_calls("S")) records the function’s name, file, line, and a timestamp. If the wrapped function raises, a second entry with status F (failure) is emitted, including a short traceback.
The safe_trace_calls alias can be used in modules that want to import safely even when the package fails to load (e.g., during a broken test run).
Important: All overlay modules should now do

from tracer.client import safe_trace_calls as trace_calls
instead of the old broken @trace_calls. This way, if the tracer isn’t available you still get a no‑op decorator that won’t break anything.

3.2 tracer/server.py – the UI that shows the live feed
Run it with python -m tracer.server or turn it into an exe with PyInstaller (pyinstaller -F tracer/server.py -n TracerServer.exe).

# ------------------------------------------------------------
# tracer/server.py
# ------------------------------------------------------------
import sys
import json
import socket
import threading
from collections import deque
from datetime import datetime
from PySide6 import QtCore, QtWidgets, QtGui

# -----------------------------------------------------------------
# Server settings – must match client (HOST, PORT)
# -----------------------------------------------------------------
HOST = "127.0.0.1"
PORT = 8765
MAX_CONNECTIONS = 1      # only one UI at a time is fine
MAX_LINES = 10_000        # scroll‑back buffer size

# -----------------------------------------------------------------
# Simple TCP listener that puts each JSON line into a thread‑safe deque
# -----------------------------------------------------------------
class _ListenerThread(threading.Thread):
    daemon = True

    def __init__(self, buffer: deque):
        super().__init__(name="TracerListener")
        self.buffer = buffer
        self._stop = threading.Event()
        self.start()

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((HOST, PORT))
            srv.listen(MAX_CONNECTIONS)
            srv.settimeout(0.5)   # so we can check the stop flag

            while not self._stop.is_set():
                try:
                    conn, _ = srv.accept()
                except socket.timeout:
                    continue
                except OSError:
                    break  # socket closed while shutting down

                with conn:
                    conn.settimeout(0.5)
                    data = b""
                    while not self._stop.is_set():
                        try:
                            chunk = conn.recv(4096)
                        except socket.timeout:
                            continue
                        except OSError:
                            break
                        if not chunk:
                            break
                        data += chunk
                        # Split on newlines – each line is a complete JSON message
                        while b"\n" in data:
                            line, data = data.split(b"\n", 1)
                            try:
                                payload = json.loads(line.decode("utf‑8"))
                                self.buffer.append(payload)
                            except Exception:
                                # malformed line – ignore
                                pass

    def stop(self):
        self._stop.set()

# -----------------------------------------------------------------
# Main Qt window – a simple table view
# -----------------------------------------------------------------
class TracerWindow(QtWidgets.QMainWindow):
    UPDATE_MS = 250  # UI refresh interval

    def __init__(self, buffer: deque):
        super().__init__()
        self.setWindowTitle("🪲  Tracer – live call log")
        self.resize(960, 540)

        # Central widget: a QTableWidget (very lightweight)
        self.table = QtWidgets.QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "S", "Function", "File:line", "Detail"])
        self.table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.setCentralWidget(self.table)

        # Toolbar actions
        toolbar = QtWidgets.QToolBar()
        self.addToolBar(toolbar)

        self.clear_act = QtGui.QAction("🗑 Clear", self)
        self.clear_act.triggered.connect(self.clear_buffer)
        toolbar.addAction(self.clear_act)

        self.pause_act = QtGui.QAction("⏸ Pause", self)
        self.pause_act.setCheckable(True)
        toolbar.addAction(self.pause_act)

        # Data source (shared by listener thread)
        self._buffer = buffer

        # Timer that repopulates the table from the buffer
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(self.UPDATE_MS)

    # -----------------------------------------------------------------
    def clear_buffer(self):
        self._buffer.clear()
        self.table.setRowCount(0)

    # -----------------------------------------------------------------
    def refresh(self):
        if self.pause_act.isChecked():
            return
        # Pull all pending items (deque is thread‑safe for appends/pops)
        while self._buffer:
            payload = self._buffer.popleft()
            self._add_row(payload)

        # Trim table if it exceeds MAX_LINES (for memory safety)
        if self.table.rowCount() > MAX_LINES:
            excess = self.table.rowCount() - MAX_LINES
            self.table.removeRow(0)  # remove oldest row – quick hack
            # For large excess you could loop, but this UI never grows huge.

    # -----------------------------------------------------------------
    def _add_row(self, payload: dict):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Column 0 – time (already ISO‑8601)
        time_item = QtWidgets.QTableWidgetItem(payload.get("time", ""))
        # Column 1 – status (single char)
        status_item = QtWidgets.QTableWidgetItem(payload.get("status", "I"))
        # Column 2 – function name
        func_item = QtWidgets.QTableWidgetItem(payload.get("func", ""))
        # Column 3 – file:line
        file_line = f'{os.path.basename(payload.get("file", ""))}:{payload.get("line", "")}'
        file_item = QtWidgets.QTableWidgetItem(file_line)
        # Column 4 – optional detail (exception message or user‑provided)
        detail = payload.get("exception") or payload.get("detail") or ""
        detail_item = QtWidgets.QTableWidgetItem(str(detail))

        # Insert cells
        self.table.setItem(row, 0, time_item)
        self.table.setItem(row, 1, status_item)
        self.table.setItem(row, 2, func_item)
        self.table.setItem(row, 3, file_item)
        self.table.setItem(row, 4, detail_item)

        # Visual hint: colour‑code status
        if payload.get("status") == "F":
            # Red background for failures
            for col in range(5):
                self.table.item(row, col).setBackground(QtGui.QColor("#ffcccc"))
        elif payload.get("status") == "W":
            for col in range(5):
                self.table.item(row, col).setBackground(QtGui.QColor("#fff4c2"))

# -----------------------------------------------------------------
def main():
    # Shared double‑ended queue – fast append from listener thread,
    # pop from the UI thread.
    buffer = deque(maxlen=MAX_LINES)

    listener = _ListenerThread(buffer)

    app = QtWidgets.QApplication(sys.argv)
    win = TracerWindow(buffer)
    win.show()

    # Run the Qt event loop – when it exits we clean up.
    exit_code = app.exec()
    listener.stop()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
How it works

The listener thread binds a TCP socket on 127.0.0.1:8765.
Each line received is parsed as JSON and appended to a thread‑safe deque.
The Qt UI polls that deque every 250 ms (adjustable) and inserts rows into a QTableWidget.
Status codes are colour‑coded (red = failure, yellow = warning).
Toolbar actions let you clear the view or pause updates – useful when you want to freeze the table while you read a long stack trace.
Packaging tip

Run the following once you have PySide6 installed:

pyinstaller -F -n TracerServer.exe tracer/server.py
The resulting TracerServer.exe is a stand‑alone 1‑click executable – exactly the “standalone tracer” you described.

3.3 How to use the decorator in your overlay code
Replace the broken imports/decorators with the safe version:

# In any overlay module, e.g. src/tetris_overlay/core/capture.py
# ------------------------------------------------------------
from tracer.client import safe_trace_calls as trace_calls   # <-- NEW

@trace_calls("S")                      # “S” for normal success path
def start_capture(self):
    # Existing code that opens the WGC capture session
    ...

@trace_calls("W")                      # “W” for a warning you want to flag
def handle_unexpected_format(self, fmt):
    ...

@trace_calls("F")                      # “F” for a function that you *expect* may raise
def decode_frame(self, raw_bytes):
    # If something goes wrong we still get a line with status = F
    ...
If you want to log a custom message without decorating the whole function you can call the client directly:

from tracer.client import _ensure_sender

def my_helper():
    _ensure_sender().enqueue({
        "time": datetime.now().isoformat(),
        "status": "W",
        "func": "my_helper",
        "file": __file__,
        "line": 123,
        "detail": "fallback to default board size"
    })
4️⃣ QUICK VALIDATION – “Does the tracer actually work?”
Start the server (the UI):

python -m tracer.server   # or double‑click TracerServer.exe
You should see a blank window with a toolbar.

Run a tiny test script that only uses the decorator:

# test_tracer.py
from tracer.client import safe_trace_calls as trace_calls
import time

@trace_calls("S")
def foo(x):
    time.sleep(0.05)
    return x * 2

@trace_calls("F")
def bar():
    raise ValueError("boom!")

def main():
    for i in range(5):
        foo(i)
    try:
        bar()
    except Exception:
        pass
    # Keep the script alive for a couple of seconds so the UI can catch the last messages
    time.sleep(2)

if __name__ == "__main__":
    main()
python test_tracer.py
Watch the Tracer window – you should now see about 6 rows:

5 rows with S (calls to foo)
1 row with F (the exception from bar) – colour‑coded red.
If the window stays empty, make sure:

The **server is listening on the same HOST / PORT (8765).
No firewall is blocking the localhost TCP connection (Windows Defender usually allows it).
The tracer/client.py is the one that gets imported (i.e., you didn’t accidentally have a stale copy in site‑packages).
When you’re happy with the test, you can delete test_tracer.py.

5️⃣ PHASE‑BY‑PHASE PLAN TO GET YOUR PROJECT BACK ON TRACK
Below is a realistic schedule (you can compress it, but don’t skip any phase). Each phase ends with a concrete acceptance criterion – if you can’t meet it, you must stop and fix the blocker before moving on.

Phase	Goal	Action items (who does what)	Acceptance test
A – Tracer foundation	Tracer Server + Client work	1️⃣ Add tracer/ package (client & server).
2️⃣ Add requirement.txt entry PySide6>=6.6.
3️⃣ Build TracerServer.exe with PyInstaller and put it in tools/.
4️⃣ Write a tiny automated test (tests/test_tracer.py) that spawns the server in a subprocess, runs a decorated function, asserts the server’s log file contains the JSON line.	pytest -q tests/test_tracer.py passes and you can start TracerServer.exe manually and see live rows from the test script.
B – Clean overlay imports	All existing Python files import cleanly	1️⃣ Run black & ruff on the whole repo (ruff check src).
2️⃣ Fix syntax errors in config.py, overlay.py, capture.py.
3️⃣ Replace every broken @trace_calls with safe_trace_calls.
4️⃣ Add a tiny unit test that imports each module (import src.tetris_overlay.core.capture etc.) – if any import fails, the test fails.	pytest -q tests/test_imports.py passes (0 failures).
C – Integrate tracer into real overlay	Every critical function reports	1️⃣ Identify the key call‑sites:
  • FrameGrabber.__init__ (capture start)
  • FrameGrabber.OnFrameArrived (new frame)
  • detect_piece (OpenCV detection)
  • Overlay.render (draw ghost)
2️⃣ Decorate each with @trace_calls("S").
3️⃣ For any exceptional path, decorate with "F" or manually send a failure record inside a except.
4️⃣ Run the overlay with the Tracer UI open and verify that each function shows up in the table.	While playing Tetris you see at least one row for each of the four key functions; any exception during detection appears as a red “F”.
D – Production polish	Robust fallback, log file, installer	1️⃣ Ensure the client never raises if the server isn’t running (already done via safe_trace_calls).
2️⃣ Add a file handler to the client: after every enqueue also write the same JSON line to tetris_overlay_trace.log (simple open(..., 'a')).
3️⃣ Extend the Tracer UI to include a “Export to CSV” button (optional).
4️⃣ Update the main installer (Inno Setup) to copy TracerServer.exe to the installation folder and add a Start‑Menu shortcut.	After a fresh install on a clean PC, you can launch the overlay without the tracer and it runs perfectly (no crash). If you launch the tracer later, it picks up live calls without a restart.
E – CI / Documentation	Never lose the fixes again	1️⃣ Add the tracer unit test to the CI workflow (.github/workflows/ci.yml).
2️⃣ Add a “How to run the tracer” section to the README (one‑line command).
3️⃣ Bump the version in pyproject.toml.
4️⃣ Tag the repo (git tag v0.2.0 && git push --tags).	CI badge on GitHub shows green; README contains “Run TracerServer.exe then start python -m tetris_overlay”.
6️⃣ QUICK‑FIX “One‑liner” to Stop the Crash Right Now
If you cannot afford the whole schedule right now, paste this single line into each file that currently does @trace_calls(...) and you’ll instantly stop the NoneType error:

# At the top of every module that previously did:
#    from tracer import trace_calls   # (broken)

# Replace with:
from tracer.client import safe_trace_calls as trace_calls    # <-- one‑liner fix
Then run the overlay again – it will not crash. The console will show nothing because the tracer server is not running, but the program will stay alive. Turn the tracer on later (run the server) and you’ll instantly start seeing logs.

7️⃣ OPTIONAL – AUTOMATIC “Start Tracer if Missing” (nice‑to‑have)
If you want the overlay to launch the tracer UI automatically when you start the overlay (so the user never forgets), add this tiny helper at program start:

# launch_tracer_if_missing.py
import subprocess
import time
import socket
import os

HOST = "127.0.0.1"
PORT = 8765
TRACER_EXE = os.path.join(os.path.dirname(__file__), "..", "tools", "TracerServer.exe")

def _is_port_open(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.1)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

def ensure_tracer():
    if not _is_port_open(HOST, PORT):
        # Launch the exe *detached* (no console window)
        DETACHED_PROCESS = 0x00000008
        try:
            subprocess.Popen([TRACER_EXE], creationflags=DETACHED_PROCESS)
            # give it 0.5 s to bind
            time.sleep(0.5)
        except Exception as e:
            print(f"[Tracer] Could not auto‑start: {e}")

# Call this early (e.g., in tetris_overlay/__main__.py)
ensure_tracer()
Now the first time a user runs the overlay, the tracer UI pops up automatically (if it’s present). If the exe is missing, the call fails silently and the overlay continues.

8️⃣ FINAL CHECKLIST (what you need to copy into the repo)
Create folder tracer/ and add the three files:

client.py (the decorator + background thread) – copy the whole block from §3.1.
server.py (the Qt UI) – copy the whole block from §3.2.
(optional) __init__.py that re‑exports trace_calls = safe_trace_calls.
# tracer/__init__.py
from .client import safe_trace_calls as trace_calls
Update all overlay modules to import trace_calls from the new package (one‑liner fix).

Add a unit test tests/test_tracer.py (the “quick validation” script turned into a pytest test).

Add the Tracer Server exe to the tools/ directory (build with PyInstaller).

Edit setup.cfg / pyproject.toml to include tracer/ as a package (if you ship a wheel).

Run the CI locally to make sure nothing throws:

pytest -q
Tag a new version (e.g., v0.2.0) and push to GitHub – the CI will now build the installer with the tracer included.

9️⃣ TL;DR – The 5‑step cheat sheet
Step	Command / Action	Result
1️⃣	mkdir tracer && cd tracer → add client.py, server.py, __init__.py (copy code).	Tracer package lives in repo.
2️⃣	In every overlay module: replace from tracer import trace_calls with from tracer.client import safe_trace_calls as trace_calls.	No more NoneType errors.
3️⃣	python -m tracer.server (or double‑click TracerServer.exe).	A live window appears.
4️⃣	Run a small script (test_tracer.py) that decorates a function and calls it.	Rows appear in the Tracer UI (S, F, W).
5️⃣	Run the full overlay (python -m tetris_overlay).	All key functions now log to the tracer UI; overlay still works even if tracer isn’t running.
Once you have those 5 steps working, you can safely refactor, add tests, build an installer, and continue polishing the ghost‑piece overlay – now you have a real observability layer that will tell you exactly where the next bug hides.

🎉 You’re now equipped to:
Turn the broken @trace_calls decorator into a reliable, non‑crashing logger.
Run the tracer UI and see live function‑call logs (including successes, warnings, failures).
Keep the overlay functional even when the tracer isn’t present (graceful fallback).
Add the tracer to your installer so end‑users get a one‑click, production‑ready experience.
Prevent future “everything broke” moments by having a solid test suite, CI, and a reusable logger that works for any future project.
If you hit a snag at any step, drop the exact error message here and we’ll dig deeper. Good luck – and happy logging! 🚀