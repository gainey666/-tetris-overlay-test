import time
from collections import deque

# Import our logger bridge
try:
    import logger_bridge as log

# Import global function tracer
try:
    from tracer.client import safe_trace_calls as trace_calls
    TRACER_AVAILABLE = True
except ImportError:
    TRACER_AVAILABLE = False

    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False



class DXGIPerfMonitor:
    def __init__(self, window_sec: float = 1.0):
    @trace_calls('__init__', 'dxgi_perf.py', 22)
        self.window = window_sec
        self.times = deque()

    def tick(self):
    @trace_calls('tick', 'dxgi_perf.py', 26)
        now = time.perf_counter()
        self.times.append(now)
        while self.times and now - self.times[0] > self.window:
            self.times.popleft()

    def fps(self) -> float:
    @trace_calls('fps', 'dxgi_perf.py', 32)
        if len(self.times) < 2:
            return 0.0
        return (len(self.times) - 1) / (self.times[-1] - self.times[0])
