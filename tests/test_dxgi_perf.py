import time
import pytest
from src.agents.dxgi_perf import DXGIPerfMonitor

def test_fps_calculation():
    mon = DXGIPerfMonitor(window_sec=0.5)
    start = time.perf_counter()
    for _ in range(5):
        mon.tick()
        time.sleep(0.1)          # 10 fps ideal
    fps = mon.fps()
    assert 8 <= fps <= 12       # tolerance
