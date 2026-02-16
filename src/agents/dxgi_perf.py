import time
from collections import deque


class DXGIPerfMonitor:
    def __init__(self, window_sec: float = 1.0):
        self.window = window_sec
        self.times = deque()

    def tick(self):
        now = time.perf_counter()
        self.times.append(now)
        while self.times and now - self.times[0] > self.window:
            self.times.popleft()

    def fps(self) -> float:
        if len(self.times) < 2:
            return 0.0
        return (len(self.times) - 1) / (self.times[-1] - self.times[0])
