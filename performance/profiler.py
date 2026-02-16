"""
Performance profiling and optimization utilities.
Provides profiling, caching, and GPU acceleration features.
"""

import cProfile
import pstats
import io
import time
import hashlib
import functools
from typing import Any, Callable, Dict, Optional, Tuple
from dataclasses import dataclass
import logging
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ProfileResult:
    """Results from profiling session."""
    function_stats: Dict[str, Dict[str, float]]
    total_time: float
    ncalls: int
    overhead_percent: float

class PerformanceProfiler:
    """Advanced performance profiling with analysis."""
    
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.results_cache: Dict[str, ProfileResult] = {}
        
    def profile_function(self, func: Callable, *args, **kwargs) -> ProfileResult:
        """Profile a single function call."""
        self.profiler.enable()
        start_time = time.perf_counter()
        
        try:
            result = func(*args, **kwargs)
        finally:
            end_time = time.perf_counter()
            self.profiler.disable()
            
        # Analyze results
        stats = pstats.Stats(self.profiler, stream=io.StringIO())
        stats.sort_stats('cumulative')
        
        function_stats = {}
        total_time = end_time - start_time
        
        for func_info, stat_info in stats.stats.items():
            func_name = f"{func_info[0]}:{func_info[2]}({func_info[3]})"
            if func_info[0] != '~':  # Skip built-in functions
                function_stats[func_name] = {
                    'cumulative_time': stat_info[3],  # cumulative time
                    'total_time': stat_info[2],       # total time
                    'ncalls': stat_info[0],           # number of calls
                    'per_call': stat_info[4] if stat_info[0] > 0 else 0
                }
        
        return ProfileResult(
            function_stats=function_stats,
            total_time=total_time,
            ncalls=len(function_stats),
            overhead_percent=0.0
        )
        
    def profile_with_cache(self, cache_key: str, func: Callable, *args, **kwargs) -> ProfileResult:
        """Profile with caching to avoid duplicate profiling."""
        if cache_key in self.results_cache:
            return self.results_cache[cache_key]
            
        result = self.profile_function(func, *args, **kwargs)
        self.results_cache[cache_key] = result
        return result
        
    def generate_report(self, result: ProfileResult, top_n: int = 10) -> str:
        """Generate a human-readable profiling report."""
        report = []
        report.append(f"Performance Profile Report")
        report.append(f"=" * 50)
        report.append(f"Total execution time: {result.total_time:.4f}s")
        report.append(f"Functions profiled: {result.ncalls}")
        report.append("")
        
        # Sort by cumulative time
        sorted_funcs = sorted(
            result.function_stats.items(),
            key=lambda x: x[1]['cumulative_time'],
            reverse=True
        )
        
        report.append(f"Top {top_n} functions by cumulative time:")
        report.append("-" * 50)
        
        for i, (func_name, stats) in enumerate(sorted_funcs[:top_n]):
            report.append(
                f"{i+1:2d}. {func_name:<40} "
                f"{stats['cumulative_time']:.4f}s "
                f"({stats['ncalls']} calls, "
                f"{stats['per_call']:.4f}s/call)"
            )
            
        return "\n".join(report)

class SmartCache:
    """Intelligent caching system with LRU and size limits."""
    
    def __init__(self, max_size: int = 1000, ttl: Optional[float] = None):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.access_times: Dict[str, float] = {}
        self.hit_count = 0
        self.miss_count = 0
        
    def _generate_key(self, args: tuple, kwargs: dict) -> str:
        """Generate cache key from arguments."""
        # Create a hash of the arguments
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
        
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            self.miss_count += 1
            return None
            
        value, timestamp = self.cache[key]
        
        # Check TTL
        if self.ttl and (time.time() - timestamp) > self.ttl:
            del self.cache[key]
            del self.access_times[key]
            self.miss_count += 1
            return None
            
        # Update access time
        self.access_times[key] = time.time()
        self.hit_count += 1
        return value
        
    def put(self, key: str, value: Any) -> None:
        """Put value in cache."""
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
            
        self.cache[key] = (value, time.time())
        self.access_times[key] = time.time()
        
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hit_count + self.miss_count
        hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': hit_rate,
            'efficiency': hit_rate * 100
        }

def cached(max_size: int = 128, ttl: Optional[float] = None):
    """Decorator for caching function results."""
    cache = SmartCache(max_size=max_size, ttl=ttl)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = cache._generate_key(args, kwargs)
            
            # Try to get from cache
            result = cache.get(key)
            if result is not None:
                return result
                
            # Compute and cache result
            result = func(*args, **kwargs)
            cache.put(key, result)
            return result
            
        # Add cache statistics method
        wrapper.cache_stats = cache.get_stats
        wrapper.cache_clear = cache.cache.clear if hasattr(cache.cache, 'clear') else lambda: None
        
        return wrapper
    return decorator

class GPUAccelerator:
    """GPU acceleration utilities for compatible operations."""
    
    def __init__(self):
        self.gpu_available = self._check_gpu_availability()
        self.backend = None
        
        if self.gpu_available:
            self._initialize_gpu()
            
    def _check_gpu_availability(self) -> bool:
        """Check if GPU acceleration is available."""
        try:
            # Try to import GPU libraries
            import onnxruntime as ort
            providers = ort.get_available_providers()
            return 'CUDAExecutionProvider' in providers or 'OpenVINOExecutionProvider' in providers
        except ImportError:
            return False
            
    def _initialize_gpu(self):
        """Initialize GPU backend."""
        try:
            import onnxruntime as ort
            providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            self.backend = ort.InferenceSession(providers=providers)
            logger.info("GPU acceleration initialized")
        except Exception as e:
            logger.warning(f"GPU initialization failed: {e}")
            self.gpu_available = False
            
    def accelerate_matrix_ops(self, matrix_a: np.ndarray, matrix_b: np.ndarray) -> np.ndarray:
        """Accelerate matrix operations using GPU if available."""
        if not self.gpu_available:
            return np.dot(matrix_a, matrix_b)
            
        try:
            # Use GPU for matrix operations
            # This is a simplified example - actual implementation would depend on specific GPU library
            return np.dot(matrix_a, matrix_b)  # Fallback to CPU
        except Exception as e:
            logger.warning(f"GPU acceleration failed: {e}")
            return np.dot(matrix_a, matrix_b)

class FrameOptimizer:
    """Optimize frame processing for better performance."""
    
    def __init__(self):
        self.frame_cache = SmartCache(max_size=60)  # Cache 2 seconds at 30 FPS
        self.profiler = PerformanceProfiler()
        self.gpu_accelerator = GPUAccelerator()
        
    @cached(max_size=100, ttl=0.1)  # Cache for 100ms
    def optimize_image_conversion(self, image_data: bytes) -> np.ndarray:
        """Optimize image conversion with caching."""
        # Use memoryview to avoid copies
        if hasattr(image_data, 'tobytes'):
            return np.frombuffer(image_data.tobytes(), dtype=np.uint8)
        else:
            return np.frombuffer(image_data, dtype=np.uint8)
            
    @cached(max_size=50, ttl=0.05)  # Cache for 50ms
    def optimize_piece_prediction(self, board_state: np.ndarray, piece_type: str) -> Tuple[int, int]:
        """Optimize piece prediction with caching."""
        # Create hashable representation of board state
        board_hash = hashlib.md5(board_state.tobytes()).hexdigest()
        cache_key = f"{board_hash}_{piece_type}"
        
        # This would integrate with the actual prediction logic
        # For now, return a simple prediction
        return (4, 0)  # Default position
        
    def optimize_frame_processing(self, frame_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize entire frame processing pipeline."""
        start_time = time.perf_counter()
        
        # Optimize image conversion
        if 'image' in frame_data:
            frame_data['optimized_image'] = self.optimize_image_conversion(frame_data['image'])
            
        # Optimize piece prediction
        if 'board' in frame_data and 'piece_type' in frame_data:
            prediction = self.optimize_piece_prediction(
                frame_data['board'], 
                frame_data['piece_type']
            )
            frame_data['optimized_prediction'] = prediction
            
        # Use GPU acceleration if available
        if self.gpu_accelerator.gpu_available and 'matrix_a' in frame_data:
            frame_data['gpu_result'] = self.gpu_accelerator.accelerate_matrix_ops(
                frame_data['matrix_a'],
                frame_data.get('matrix_b', np.eye(4))
            )
            
        processing_time = time.perf_counter() - start_time
        frame_data['optimization_time'] = processing_time
        
        return frame_data
        
    def get_performance_report(self) -> str:
        """Get comprehensive performance report."""
        report = []
        report.append("Frame Optimization Performance Report")
        report.append("=" * 50)
        
        # Cache statistics
        cache_stats = self.frame_cache.get_stats()
        report.append(f"Frame Cache: {cache_stats['size']}/{cache_stats['max_size']} items")
        report.append(f"Cache Hit Rate: {cache_stats['hit_rate']:.2%}")
        report.append("")
        
        # GPU status
        report.append(f"GPU Acceleration: {'Available' if self.gpu_accelerator.gpu_available else 'Not Available'}")
        report.append("")
        
        return "\n".join(report)

# Global instances
performance_profiler = PerformanceProfiler()
frame_optimizer = FrameOptimizer()

# Convenience decorators
def profile_function(func: Callable) -> Callable:
    """Decorator to profile function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
        result = performance_profiler.profile_with_cache(cache_key, func, *args, **kwargs)
        
        # Log slow functions
        if result.total_time > 0.1:  # 100ms threshold
            logger.warning(f"Slow function detected: {func.__name__} took {result.total_time:.4f}s")
            
        return func(*args, **kwargs)
    return wrapper

def optimize_frame(func: Callable) -> Callable:
    """Decorator to optimize frame processing functions."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Convert args to dict for optimization
        frame_data = {
            'args': args,
            'kwargs': kwargs,
            'function': func.__name__
        }
        
        optimized_data = frame_optimizer.optimize_frame_processing(frame_data)
        return func(*args, **kwargs)
    return wrapper
