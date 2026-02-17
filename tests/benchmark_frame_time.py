#!/usr/bin/env python3
"""
Performance benchmark script for frame processing.
Measures FPS, latency, and memory usage over extended runs.
"""

import time
import tracemalloc
import psutil
import numpy as np
from typing import Dict, List
import statistics
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from overlay_renderer import OverlayRenderer
from tetromino_shapes import get_piece_shape
from stats.service import stats_service


class FrameBenchmark:
    """Benchmark frame processing performance."""
    
    def __init__(self):
        self.results = {
            'frame_times': [],
            'fps_samples': [],
            'memory_samples': [],
            'cpu_samples': []
        }
        self.process = psutil.Process()
        
    def run_benchmark(self, num_frames: int = 500, target_fps: int = 30) -> Dict:
        """Run the frame processing benchmark."""
        print(f"Running benchmark: {num_frames} frames at {target_fps} FPS")
        
        # Start memory tracking
        tracemalloc.start()
        
        # Initialize components
        renderer = OverlayRenderer()
        board = np.zeros((10, 20), dtype=int)
        
        # Start timing
        start_time = time.time()
        frame_interval = 1.0 / target_fps
        
        # Process frames
        for frame_num in range(num_frames):
            frame_start = time.time()
            
            # Simulate frame processing
            pieces = ["I", "O", "T", "S", "Z", "J", "L"]
            piece = pieces[frame_num % len(pieces)]
            rotation = frame_num % 4
            
            # Draw ghost piece
            renderer.draw_ghost(board, piece, rotation)
            
            # Record frame time
            frame_end = time.time()
            frame_time = (frame_end - frame_start) * 1000  # Convert to ms
            self.results['frame_times'].append(frame_time)
            
            # Sample performance metrics every 10 frames
            if frame_num % 10 == 0:
                # Memory usage
                current, peak = tracemalloc.get_traced_memory()
                self.results['memory_samples'].append(current / 1024 / 1024)  # MB
                
                # CPU usage
                cpu_percent = self.process.cpu_percent()
                self.results['cpu_samples'].append(cpu_percent)
                
                # Calculate instantaneous FPS
                if frame_num > 0:
                    elapsed = frame_end - start_time
                    current_fps = frame_num / elapsed
                    self.results['fps_samples'].append(current_fps)
            
            # Maintain target FPS
            elapsed = time.time() - frame_start
            sleep_time = max(0, frame_interval - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Stop memory tracking
        tracemalloc.stop()
        
        # Calculate final statistics
        return self._calculate_statistics()
        
    def _calculate_statistics(self) -> Dict:
        """Calculate performance statistics."""
        frame_times = self.results['frame_times']
        fps_samples = self.results['fps_samples']
        memory_samples = self.results['memory_samples']
        cpu_samples = self.results['cpu_samples']
        
        stats = {
            'total_frames': len(frame_times),
            'frame_time_stats': {
                'mean_ms': statistics.mean(frame_times),
                'median_ms': statistics.median(frame_times),
                'min_ms': min(frame_times),
                'max_ms': max(frame_times),
                'std_dev_ms': statistics.stdev(frame_times) if len(frame_times) > 1 else 0
            },
            'fps_stats': {
                'mean_fps': statistics.mean(fps_samples) if fps_samples else 0,
                'median_fps': statistics.median(fps_samples) if fps_samples else 0,
                'min_fps': min(fps_samples) if fps_samples else 0,
                'max_fps': max(fps_samples) if fps_samples else 0
            },
            'memory_stats': {
                'mean_mb': statistics.mean(memory_samples) if memory_samples else 0,
                'peak_mb': max(memory_samples) if memory_samples else 0,
                'growth_mb': (memory_samples[-1] - memory_samples[0]) if len(memory_samples) > 1 else 0
            },
            'cpu_stats': {
                'mean_percent': statistics.mean(cpu_samples) if cpu_samples else 0,
                'max_percent': max(cpu_samples) if cpu_samples else 0
            }
        }
        
        return stats
        
    def print_results(self, stats: Dict):
        """Print benchmark results."""
        print("\n" + "="*60)
        print("FRAME PROCESSING BENCHMARK RESULTS")
        print("="*60)
        
        print(f"Total Frames Processed: {stats['total_frames']}")
        
        print("\nFrame Time (ms):")
        ft = stats['frame_time_stats']
        print(f"  Mean: {ft['mean_ms']:.2f}ms")
        print(f"  Median: {ft['median_ms']:.2f}ms")
        print(f"  Min: {ft['min_ms']:.2f}ms")
        print(f"  Max: {ft['max_ms']:.2f}ms")
        print(f"  Std Dev: {ft['std_dev_ms']:.2f}ms")
        
        print("\nFPS:")
        fps = stats['fps_stats']
        print(f"  Mean: {fps['mean_fps']:.1f}")
        print(f"  Median: {fps['median_fps']:.1f}")
        print(f"  Min: {fps['min_fps']:.1f}")
        print(f"  Max: {fps['max_fps']:.1f}")
        
        print("\nMemory Usage:")
        mem = stats['memory_stats']
        print(f"  Mean: {mem['mean_mb']:.1f}MB")
        print(f"  Peak: {mem['peak_mb']:.1f}MB")
        print(f"  Growth: {mem['growth_mb']:.1f}MB")
        
        print("\nCPU Usage:")
        cpu = stats['cpu_stats']
        print(f"  Mean: {cpu['mean_percent']:.1f}%")
        print(f"  Max: {cpu['max_percent']:.1f}%")
        
        # Performance assessment
        print("\n" + "="*60)
        print("PERFORMANCE ASSESSMENT")
        print("="*60)
        
        # FPS assessment
        target_fps = 30
        actual_fps = fps['mean_fps']
        if actual_fps >= target_fps:
            print(f"✅ FPS: {actual_fps:.1f} >= {target_fps} (TARGET MET)")
        else:
            print(f"❌ FPS: {actual_fps:.1f} < {target_fps} (BELOW TARGET)")
            
        # Frame time assessment
        target_frame_time = 1000 / target_fps  # ms
        actual_frame_time = ft['mean_ms']
        if actual_frame_time <= target_frame_time:
            print(f"✅ Frame Time: {actual_frame_time:.2f}ms <= {target_frame_time:.2f}ms (TARGET MET)")
        else:
            print(f"❌ Frame Time: {actual_frame_time:.2f}ms > {target_frame_time:.2f}ms (ABOVE TARGET)")
            
        # Memory assessment
        memory_growth = mem['growth_mb']
        if abs(memory_growth) < 2:  # Less than 2MB growth
            print(f"✅ Memory Growth: {memory_growth:.1f}MB < 2MB (GOOD)")
        else:
            print(f"⚠️  Memory Growth: {memory_growth:.1f}MB >= 2MB (POTENTIAL LEAK)")
            
        # CPU assessment
        cpu_usage = cpu['mean_percent']
        if cpu_usage < 20:
            print(f"✅ CPU Usage: {cpu_usage:.1f}% < 20% (EXCELLENT)")
        elif cpu_usage < 50:
            print(f"✅ CPU Usage: {cpu_usage:.1f}% < 50% (GOOD)")
        else:
            print(f"⚠️  CPU Usage: {cpu_usage:.1f}% >= 50% (HIGH)")
            
        print("="*60)
        
    def save_results(self, stats: Dict, filename: str = "benchmark_results.json"):
        """Save benchmark results to file."""
        import json
        
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"\nResults saved to {filename}")


def main():
    """Main benchmark execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Frame processing benchmark")
    parser.add_argument("--frames", type=int, default=500, help="Number of frames to process")
    parser.add_argument("--fps", type=int, default=30, help="Target FPS")
    parser.add_argument("--output", type=str, default="benchmark_results.json", help="Output file")
    
    args = parser.parse_args()
    
    # Run benchmark
    benchmark = FrameBenchmark()
    stats = benchmark.run_benchmark(args.frames, args.fps)
    
    # Print results
    benchmark.print_results(stats)
    
    # Save results
    benchmark.save_results(stats, args.output)
    
    # Return appropriate exit code
    target_fps = args.fps
    actual_fps = stats['fps_stats']['mean_fps']
    
    if actual_fps >= target_fps:
        print("\n🎉 BENCHMARK PASSED - Performance targets met!")
        return 0
    else:
        print("\n❌ BENCHMARK FAILED - Performance below target!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
