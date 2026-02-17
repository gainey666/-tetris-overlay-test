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
                                payload = json.loads(line.decode("utf-8"))
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
        self._message_count = 0

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("🪲 Tracer listening on localhost:8765 | Messages: 0")

        # Timer that repopulates the table from the buffer
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(self.UPDATE_MS)

    # -----------------------------------------------------------------
    def clear_buffer(self):
        self._buffer.clear()
        self.table.setRowCount(0)
        self._message_count = 0
        self.status_bar.showMessage("🪲 Tracer listening on localhost:8765 | Messages: 0")

    # -----------------------------------------------------------------
    def refresh(self):
        if self.pause_act.isChecked():
            return
        # Pull all pending items (deque is thread‑safe for appends/pops)
        while self._buffer:
            payload = self._buffer.popleft()
            self._add_row(payload)
            self._message_count += 1

        # Update status bar
        self.status_bar.showMessage(f"🪲 Tracer listening on localhost:8765 | Messages: {self._message_count}")

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
