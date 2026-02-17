"""
Python IPC adapter for C++ Tetris Overlay Engine

Provides communication bridge between Python overlay system and C++ DirectX capture engine.
Uses JSON messaging over named pipes for low-latency communication.

Data Flow:
    Python → C++: {"board": [[0,1,...], ...], "next_queue": ["T", "I", ...]}
    C++ → Python: {"column": 3, "rotation": 2, "score": 1200}
"""

import json
import socket
import threading
import time
from typing import List, Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CPPEngineAdapter:
    """IPC adapter for communicating with C++ Tetris overlay engine."""
    
    def __init__(self, host: str = "localhost", port: int = 12345):
        """
        Initialize C++ engine adapter.
        
        Args:
            host: Host for UDP communication
            port: Port for UDP communication
        """
        self.host = host
        self.port = port
        self.socket = None
        self.is_connected = False
        self.response_thread = None
        self.latest_response = None
        self._running = False
        
    def connect(self) -> bool:
        """
        Establish connection to C++ engine.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(1.0)  # 1 second timeout
            self.socket.bind((self.host, self.port + 1))  # Bind to port+1 for responses
            self.is_connected = True
            self._running = True
            
            # Start response listener thread
            self.response_thread = threading.Thread(target=self._listen_for_responses, daemon=True)
            self.response_thread.start()
            
            logger.info(f"Connected to C++ engine on {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to C++ engine: {e}")
            return False
    
    def disconnect(self):
        """Close connection to C++ engine."""
        self._running = False
        self.is_connected = False
        
        if self.socket:
            self.socket.close()
            self.socket = None
            
        if self.response_thread and self.response_thread.is_alive():
            self.response_thread.join(timeout=2.0)
            
        logger.info("Disconnected from C++ engine")
    
    def send_board_state(self, board: List[List[int]], next_queue: List[str]) -> bool:
        """
        Send board state to C++ engine for move prediction.
        
        Args:
            board: 20x10 board matrix (0=empty, 1=block)
            next_queue: List of next pieces (e.g., ["T", "I", "O"])
            
        Returns:
            True if send successful, False otherwise
        """
        if not self.is_connected or not self.socket:
            logger.warning("Not connected to C++ engine")
            return False
            
        try:
            message = {
                "type": "board_state",
                "board": board,
                "next_queue": next_queue,
                "timestamp": time.time()
            }
            
            data = json.dumps(message).encode('utf-8')
            self.socket.sendto(data, (self.host, self.port))
            
            logger.debug(f"Sent board state to C++ engine: {len(board)}x{len(board[0])} board")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send board state: {e}")
            return False
    
    def get_prediction(self, timeout: float = 0.1) -> Optional[Dict[str, Any]]:
        """
        Get latest prediction from C++ engine.
        
        Args:
            timeout: Maximum time to wait for response
            
        Returns:
            Prediction dict with keys: column, rotation, score
            None if no prediction available
        """
        if not self.is_connected:
            return None
            
        # Return latest response if available
        if self.latest_response:
            response = self.latest_response.copy()
            self.latest_response = None  # Clear after reading
            return response
            
        return None
    
    def _listen_for_responses(self):
        """Background thread to listen for responses from C++ engine."""
        while self._running and self.is_connected:
            try:
                if self.socket:
                    data, addr = self.socket.recvfrom(4096)
                    response = json.loads(data.decode('utf-8'))
                    
                    if response.get("type") == "prediction":
                        self.latest_response = {
                            "column": response.get("column"),
                            "rotation": response.get("rotation"), 
                            "score": response.get("score", 0),
                            "timestamp": response.get("timestamp", time.time())
                        }
                        logger.debug(f"Received prediction: column={response.get('column')}, rotation={response.get('rotation')}")
                        
            except socket.timeout:
                continue  # Normal timeout, continue listening
            except Exception as e:
                if self._running:  # Only log if we're supposed to be running
                    logger.error(f"Error receiving response: {e}")
                break
    
    def ping(self) -> bool:
        """
        Send ping to C++ engine to check connectivity.
        
        Returns:
            True if ping successful, False otherwise
        """
        if not self.is_connected or not self.socket:
            return False
            
        try:
            message = {"type": "ping", "timestamp": time.time()}
            data = json.dumps(message).encode('utf-8')
            self.socket.sendto(data, (self.host, self.port))
            return True
            
        except Exception as e:
            logger.error(f"Failed to ping C++ engine: {e}")
            return False


class NamedPipeAdapter:
    """Alternative adapter using Windows named pipes for communication."""
    
    def __init__(self, pipe_name: str = r"\\.\pipe\tetris_overlay_cpp"):
        """
        Initialize named pipe adapter.
        
        Args:
            pipe_name: Windows named pipe path
        """
        self.pipe_name = pipe_name
        self.pipe_handle = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """Connect to named pipe."""
        try:
            import win32pipe
            import win32file
            
            self.pipe_handle = win32file.CreateFile(
                self.pipe_name,
                win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                0,
                None,
                win32file.OPEN_EXISTING,
                0,
                None
            )
            
            self.is_connected = True
            logger.info(f"Connected to named pipe: {self.pipe_name}")
            return True
            
        except ImportError:
            logger.error("pywin32 not available for named pipe communication")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to named pipe: {e}")
            return False
    
    def disconnect(self):
        """Close named pipe connection."""
        if self.pipe_handle:
            try:
                import win32file
                win32file.CloseHandle(self.pipe_handle)
            except:
                pass
            self.pipe_handle = None
            self.is_connected = False
            logger.info("Disconnected from named pipe")
    
    def send_message(self, message: Dict[str, Any]) -> bool:
        """Send message through named pipe."""
        if not self.is_connected or not self.pipe_handle:
            return False
            
        try:
            import win32file
            
            data = json.dumps(message).encode('utf-8')
            win32file.WriteFile(self.pipe_handle, data)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message through named pipe: {e}")
            return False
    
    def receive_message(self) -> Optional[Dict[str, Any]]:
        """Receive message from named pipe."""
        if not self.is_connected or not self.pipe_handle:
            return None
            
        try:
            import win32file
            
            result, data = win32file.ReadFile(self.pipe_handle, 4096)
            if result == 0:  # Success
                message = json.loads(data.decode('utf-8'))
                return message
                
        except Exception as e:
            logger.error(f"Failed to receive message from named pipe: {e}")
            
        return None


def create_cpp_adapter(adapter_type: str = "udp", **kwargs) -> CPPEngineAdapter:
    """
    Factory function to create C++ engine adapter.
    
    Args:
        adapter_type: Type of adapter ("udp" or "named_pipe")
        **kwargs: Additional arguments for adapter initialization
        
    Returns:
        Configured adapter instance
    """
    if adapter_type == "udp":
        return CPPEngineAdapter(**kwargs)
    elif adapter_type == "named_pipe":
        return NamedPipeAdapter(**kwargs)
    else:
        raise ValueError(f"Unknown adapter type: {adapter_type}")


# Example usage and testing
if __name__ == "__main__":
    # Test UDP adapter
    adapter = create_cpp_adapter("udp", host="localhost", port=12345)
    
    if adapter.connect():
        print("Connected to C++ engine")
        
        # Test board state send
        test_board = [[0 for _ in range(10)] for _ in range(20)]
        test_board[19][5] = 1  # Add a block at bottom center
        
        if adapter.send_board_state(test_board, ["T", "I", "O"]):
            print("Board state sent successfully")
            
            # Wait for response
            time.sleep(0.5)
            prediction = adapter.get_prediction()
            if prediction:
                print(f"Received prediction: {prediction}")
            else:
                print("No prediction received")
        
        adapter.disconnect()
    else:
        print("Failed to connect to C++ engine")
