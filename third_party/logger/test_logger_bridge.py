# test_logger_bridge.py - simple test for Python logger bridge
import sys
import os

# Add the src directory to path so we can import logger_bridge
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    import logger_bridge as log
    
    print("Testing Python logger bridge...")
    
    # Test all logging functions
    log.log_info("test_python", "Python logger bridge test starting")
    log.log_success("test_python", "Python logger imported successfully")
    log.log_warn("test_python", "This is a warning from Python")
    log.log_fail("test_python", "This is a failure from Python")
    
    print("Python logger bridge test completed!")
    print("Check the console window and tetris_overlay.log file")
    
except ImportError as e:
    print(f"Failed to import logger_bridge: {e}")
    print("This is expected if the C++ DLL hasn't been built yet")
except Exception as e:
    print(f"Error testing logger bridge: {e}")
