"""Tests for performance monitoring functionality."""

import time
import pytest
from performance_monitor import PerformanceMonitor


def test_performance_monitor_basic():
    """Test basic performance monitoring functionality."""
    monitor = PerformanceMonitor(history_size=10)
    
    # Test initial state
    stats = monitor.get_stats()
    assert stats["fps"] == 0
    assert stats["total_frames"] == 0
    assert stats["uptime"] >= 0
    
    # Test frame timing
    monitor.start_frame()
    time.sleep(0.01)  # 10ms
    frame_time = monitor.end_frame()
    
    assert frame_time >= 0.01  # Should be at least 10ms
    assert frame_time < 0.05   # Should be less than 50ms
    
    # Test stats after one frame
    stats = monitor.get_stats()
    assert stats["total_frames"] == 1
    assert stats["avg_frame_time"] == frame_time
    assert stats["min_frame_time"] == frame_time
    assert stats["max_frame_time"] == frame_time


def test_performance_monitor_multiple_frames():
    """Test performance monitoring with multiple frames."""
    monitor = PerformanceMonitor(history_size=5)
    
    # Simulate multiple frames with different timings
    frame_times = [0.01, 0.02, 0.015, 0.025, 0.018]
    
    for expected_time in frame_times:
        monitor.start_frame()
        time.sleep(expected_time)
        monitor.end_frame()
    
    stats = monitor.get_stats()
    assert stats["total_frames"] == 5
    # Use approximation for floating point comparison
    expected_avg = sum(frame_times) / len(frame_times)
    assert abs(stats["avg_frame_time"] - expected_avg) < 0.005  # Allow 5ms tolerance
    assert abs(stats["min_frame_time"] - min(frame_times)) < 0.005  # Allow 5ms tolerance
    assert abs(stats["max_frame_time"] - max(frame_times)) < 0.005  # Allow 5ms tolerance
    assert stats["fps"] > 0  # Should have some FPS


def test_target_fps_check():
    """Test FPS target checking."""
    monitor = PerformanceMonitor()
    
    # Test with no frames (should return True)
    assert monitor.is_target_fps_met(30.0) == True
    
    # Add some fast frames
    for _ in range(10):
        monitor.start_frame()
        time.sleep(0.01)  # 10ms = 100 FPS
        monitor.end_frame()
    
    # Should meet 30 FPS target
    assert monitor.is_target_fps_met(30.0) == True
    
    # Should not meet 120 FPS target
    assert monitor.is_target_fps_met(120.0) == False


def test_performance_monitor_history_limit():
    """Test that performance monitor respects history size limit."""
    monitor = PerformanceMonitor(history_size=3)
    
    # Add more frames than history size
    for i in range(5):
        monitor.start_frame()
        time.sleep(0.01)
        monitor.end_frame()
    
    stats = monitor.get_stats()
    # Should only count the last 3 frames in FPS calculation
    assert stats["total_frames"] == 5  # Total frames still counted
    assert len(monitor.frame_times) == 3  # History limited


def test_performance_monitor_error_handling():
    """Test error handling in performance monitoring."""
    monitor = PerformanceMonitor()
    
    # Test calling end_frame without start_frame
    # This should still work but might give unusual timing
    frame_time = monitor.end_frame()
    assert frame_time >= 0
    
    # Test multiple end_frame calls without start_frame
    for _ in range(3):
        frame_time = monitor.end_frame()
        assert frame_time >= 0


if __name__ == "__main__":
    test_performance_monitor_basic()
    test_performance_monitor_multiple_frames()
    test_target_fps_check()
    test_performance_monitor_history_limit()
    test_performance_monitor_error_handling()
    print("All performance monitor tests passed!")
