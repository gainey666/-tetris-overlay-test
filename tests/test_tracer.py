"""Integration test for tracer client/server."""
import json
import socket
import time

import pytest

from tracer.client import safe_trace_calls as trace_calls


@pytest.fixture(scope="session")
def tracer_server():
    """Start tracer server listener once per session."""
    from tracer import server  # noqa: F401

    time.sleep(0.2)
    yield
    server._listener.stop()
    time.sleep(0.1)


def _connect_raw_socket():
    sock = socket.create_connection(("127.0.0.1", 8765), timeout=1.0)
    sock.settimeout(1.0)
    return sock


@trace_calls("S")
def _demo_success():
    return "ok"


@trace_calls("F")
def _demo_failure():
    raise RuntimeError("boom")


def test_tracer_receives_success_and_failure(tracer_server):
    sock = _connect_raw_socket()
    received = []

    assert _demo_success() == "ok"
    with pytest.raises(RuntimeError):
        _demo_failure()

    start = time.time()
    while len(received) < 2 and time.time() - start < 2.0:
        try:
            data = sock.recv(4096)
            if not data:
                break
            for line in data.decode("utf-8").splitlines():
                line = line.strip()
                if line:
                    received.append(json.loads(line))
        except socket.timeout:
            break

    sock.close()

    assert len(received) == 2, f"expected 2 log lines, got {received}"
    statuses = {msg["status"] for msg in received}
    assert statuses == {"S", "F"}

    names = {msg["func"] for msg in received}
    assert "_demo_success" in names
    assert "_demo_failure" in names
