"""
Threaded overlay implementation following senior dev architecture.
"""

import threading
import time
import cv2
import numpy as np
from typing import Optional, Dict, Any
from queue import Queue, Empty
from dataclasses import dataclass
import signal
import sys
from .wgc_capture import create_capture
from .tetromino_shapes import get_piece_shape, get_piece_color
from ..utils.logger import logger

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



@dataclass
class GhostPosition:
    """Thread-safe ghost position data."""
    x: int = 0
    y: int = 0
    piece_type: str = "T"
    rotation: int = 0
    valid: bool = False
    timestamp: float = 0.0


class CaptureThread(threading.Thread):
    """Background thread for frame capture."""
    
    def __init__(self, hwnd: int, frame_queue: Queue, shutdown_event: threading.Event):
    @trace_calls('__init__', 'threaded_overlay.py', 49)
        super().__init__(daemon=True, name="CaptureThread")
        self.hwnd = hwnd
        self.frame_queue = frame_queue
        self.shutdown_event = shutdown_event
        self.running = False
        self.capture = None
        
    def run(self):
    @trace_calls('run', 'threaded_overlay.py', 57)
        """Run capture loop."""
        self.running = True
        logger.info(f"Capture thread started for window {self.hwnd}")
        
        try:
            # Create capture (try WGC first, fallback to BitBlt)
            self.capture = create_capture(self.hwnd, prefer_wgc=True)
            
            if not self.capture:
                logger.error("Failed to create capture")
                return
            
            while self.running and not self.shutdown_event.is_set():
                try:
                    frame = self.capture.try_get_frame()
                    if frame is not None:
                        # Put frame in queue (non-blocking)
                        try:
                            self.frame_queue.put_nowait(frame)
                        except:
                            # Queue full, drop frame
                            pass
                    else:
                        # No frame available, wait a bit
                        self.shutdown_event.wait(0.001)
                        
                except Exception as e:
                    logger.error(f"Capture error: {e}")
                    self.shutdown_event.wait(0.01)
                    
        except Exception as e:
            logger.error(f"Capture thread crashed: {e}")
        finally:
            if self.capture:
                del self.capture
            logger.info("Capture thread stopped")
    
    def stop(self):
    @trace_calls('stop', 'threaded_overlay.py', 95)
        """Stop capture thread."""
        self.running = False


class AnalysisThread(threading.Thread):
    """Background thread for game analysis."""
    
    def __init__(self, frame_queue: Queue, ghost_position: GhostPosition, shutdown_event: threading.Event):
    @trace_calls('__init__', 'threaded_overlay.py', 103)
        super().__init__(daemon=True, name="AnalysisThread")
        self.frame_queue = frame_queue
        self.ghost_position = ghost_position
        self.shutdown_event = shutdown_event
        self.running = False
        self.board_roi = None
        
    def run(self):
    @trace_calls('run', 'threaded_overlay.py', 111)
        """Run analysis loop."""
        self.running = True
        logger.info("Analysis thread started")
        
        try:
            while self.running and not self.shutdown_event.is_set():
                try:
                    # Get frame from queue (blocking with timeout)
                    frame = self.frame_queue.get(timeout=0.1)
                    
                    # Process frame
                    self.process_frame(frame)
                    
                except Empty:
                    # No frame available
                    continue
                except Exception as e:
                    logger.error(f"Analysis error: {e}")
                    self.shutdown_event.wait(0.01)
                    
        except Exception as e:
            logger.error(f"Analysis thread crashed: {e}")
        finally:
            logger.info("Analysis thread stopped")
    
    def process_frame(self, frame: np.ndarray):
    @trace_calls('process_frame', 'threaded_overlay.py', 137)
        """Process a frame to find ghost position."""
        try:
            h, w = frame.shape[:2]
            
            # Simple placeholder analysis - in real implementation,
            # this would detect the current piece and calculate ghost position
            
            # For now, just put a ghost piece in the center
            cell_width = w // 10
            cell_height = h // 20
            
            # Use a simple pattern for demonstration
            piece_type = "T"
            rotation = int(time.time() * 0.5) % 4  # Rotate every 2 seconds
            
            # Calculate ghost position (center of board)
            ghost_x = 5 * cell_width  # Center column
            ghost_y = 15 * cell_height  # Near bottom
            
            # Update shared position atomically
            self.ghost_position.x = ghost_x
            self.ghost_position.y = ghost_y
            self.ghost_position.piece_type = piece_type
            self.ghost_position.rotation = rotation
            self.ghost_position.valid = True
            self.ghost_position.timestamp = time.time()
            
        except Exception as e:
            logger.error(f"Frame processing error: {e}")
    
    def stop(self):
    @trace_calls('stop', 'threaded_overlay.py', 168)
        """Stop analysis thread."""
        self.running = False


class ThreadedOverlay:
    """Main overlay class using threaded architecture."""
    
    def __init__(self, hwnd: int):
    @trace_calls('__init__', 'threaded_overlay.py', 176)
        self.hwnd = hwnd
        self.shutdown_event = threading.Event()
        
        # Shared state
        self.ghost_position = GhostPosition()
        
        # Queues for thread communication
        self.frame_queue = Queue(maxsize=2)  # Small buffer to prevent memory buildup
        
        # Threads
        self.capture_thread = None
        self.analysis_thread = None
        
        # Start threads
        self._start_threads()
        
        # Setup signal handlers for proper cleanup
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Threaded overlay initialized")
    
    def _signal_handler(self, signum, frame):
    @trace_calls('_signal_handler', 'threaded_overlay.py', 199)
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def _start_threads(self):
    @trace_calls('_start_threads', 'threaded_overlay.py', 204)
        """Start background threads."""
        try:
            self.capture_thread = CaptureThread(self.hwnd, self.frame_queue, self.shutdown_event)
            self.analysis_thread = AnalysisThread(self.frame_queue, self.ghost_position, self.shutdown_event)
            
            self.capture_thread.start()
            self.analysis_thread.start()
            
            logger.info("Background threads started")
        except Exception as e:
            logger.error(f"Failed to start threads: {e}")
            self.stop()
            raise
    
    def get_ghost_position(self) -> GhostPosition:
    @trace_calls('get_ghost_position', 'threaded_overlay.py', 219)
        """Get current ghost position (thread-safe)."""
        # Check if position is recent (within 100ms)
        if time.time() - self.ghost_position.timestamp > 0.1:
            self.ghost_position.valid = False
        
        return self.ghost_position
    
    def stop(self):
    @trace_calls('stop', 'threaded_overlay.py', 227)
        """Stop all threads properly."""
        logger.info("Stopping threads...")
        
        # Signal threads to stop
        self.shutdown_event.set()
        
        # Wait for threads to finish with timeout
        threads_to_join = []
        if self.capture_thread and self.capture_thread.is_alive():
            threads_to_join.append(self.capture_thread)
        if self.analysis_thread and self.analysis_thread.is_alive():
            threads_to_join.append(self.analysis_thread)
        
        # Join threads with timeout
        for thread in threads_to_join:
            thread.join(timeout=2.0)
            if thread.is_alive():
                logger.warning(f"Thread {thread.name} did not stop gracefully")
        
        # Clear queue
        while not self.frame_queue.empty():
            try:
                self.frame_queue.get_nowait()
            except Empty:
                break
        
        logger.info("Threads stopped")
