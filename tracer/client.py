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
# CONFIGURATION (change only if you know what you're doing)
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
                data = (msg + "\n").encode("utf-8")
                self._sock.sendall(data)
            except Exception:
                # Something went wrong – drop the socket & re‑queue the message
                self._sock.close()
                self._sock = None
                # re‑queue (but don't block forever)
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
            # Should never happen, but we don't want to bring the app down.
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
                "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + f".{int(time.time() * 1000) % 1000:03d}",
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
                raise  # re‑raise – we don't swallow errors.
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
