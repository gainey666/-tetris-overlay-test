"""Performance monitoring for the overlay loop."""

import time
import logging
from typing import Dict, Any
from collections import deque

log = logging.getLogger(__name__)

class PerformanceMonitor:
    def __init__(self, history_size: int = 60):
        self.history_size = history_size
        self.frame_times = deque(maxlen=history_size)
        self.last_frame_time = time.time()
        self.frame_count = 0
        self.start_time = time.time()
    
    def start_frame(self):
        """Mark the start of a frame."""
        self.last_frame_time = time.time()
    
    def end_frame(self) -> float:
        """Mark the end of a frame and return the frame time."""
        frame_time = time.time() - self.last_frame_time
        self.frame_times.append(frame_time)
        self.frame_count += 1
        return frame_time
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        if not self.frame_times:
            return {
                "fps": 0,
                "avg_frame_time": 0,
                "min_frame_time": 0,
                "max_frame_time": 0,
                "total_frames": 0,
                "uptime": 0
            }
        
        current_time = time.time()
        uptime = current_time - self.start_time
        
        return {
            "fps": len(self.frame_times) / uptime if uptime > 0 else 0,
            "avg_frame_time": sum(self.frame_times) / len(self.frame_times),
            "min_frame_time": min(self.frame_times),
            "max_frame_time": max(self.frame_times),
            "total_frames": self.frame_count,
            "uptime": uptime
        }
    
    def is_target_fps_met(self, target_fps: float = 30.0) -> bool:
        """Check if we're meeting the target FPS."""
        if len(self.frame_times) < 10:  # Need some history
            return True
        avg_fps = len(self.frame_times) / (time.time() - self.start_time)
        return avg_fps >= (target_fps * 0.9)  # Allow 10% tolerance


# Global performance monitor instance
performance_monitor = PerformanceMonitor()
