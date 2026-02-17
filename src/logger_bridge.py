# logger_bridge.py – Python wrapper around the C++ logger
import ctypes
import os

# Path to the DLL produced by the C++ project
DLL_PATH = os.path.abspath(r"../src/capture_cpp/build/Release/capture_cpp.dll")
_logger = None
LOGGER_AVAILABLE = False

try:
    _logger = ctypes.WinDLL(DLL_PATH)
    LOGGER_AVAILABLE = True
    print("✅ C++ logger DLL loaded successfully")
except (FileNotFoundError, OSError) as e:
    print(f"⚠️ C++ logger DLL not found: {e}")
    print("📝 Using Python-only logging fallback")
    LOGGER_AVAILABLE = False

if LOGGER_AVAILABLE:
    # Declare the signatures for basic logging
    _logger.log_success_c.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    _logger.log_success_c.restype  = None
    _logger.log_fail_c.argtypes    = [ctypes.c_char_p, ctypes.c_char_p]
    _logger.log_fail_c.restype     = None
    _logger.log_warn_c.argtypes    = [ctypes.c_char_p, ctypes.c_char_p]
    _logger.log_warn_c.restype     = None
    _logger.log_info_c.argtypes    = [ctypes.c_char_p, ctypes.c_char_p]
    _logger.log_info_c.restype     = None

def _c_str(s: str) -> ctypes.c_char_p:
    return ctypes.c_char_p(s.encode('utf-8'))

def _python_fallback_log(func: str, line: int, file: str, message: str, status: str):
    """Python fallback logging when C++ DLL is not available"""
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Map status to emojis
    status_map = {
        'SUCCESS': '🟢',
        'WARNING': '🟡', 
        'ERROR': '🔴',
        'INFO': '⚪',
        'DEBUG': '🔵',
        'ENTER': '🔵'
    }
    
    emoji = status_map.get(status, '❓')
    log_line = f"[{timestamp}] {emoji} {func}(line {line}) in {file}: {message}\n"
    
    # Print to console
    print(log_line, end='')
    
    # Also write to log file if possible
    try:
        with open("tetris_overlay.log", "a", encoding="utf-8") as f:
            f.write(log_line)
    except:
        pass  # Silently fail if we can't write to file

# Basic logging functions (legacy)
def log_success(func: str, msg: str):
    if LOGGER_AVAILABLE:
        _logger.log_success_c(_c_str(func), _c_str(msg))
    else:
        _python_fallback_log(func, 0, "unknown", msg, "SUCCESS")

def log_fail(func: str, msg: str):
    if LOGGER_AVAILABLE:
        _logger.log_fail_c(_c_str(func), _c_str(msg))
    else:
        _python_fallback_log(func, 0, "unknown", msg, "ERROR")

def log_warn(func: str, msg: str):
    if LOGGER_AVAILABLE:
        _logger.log_warn_c(_c_str(func), _c_str(msg))
    else:
        _python_fallback_log(func, 0, "unknown", msg, "WARNING")

def log_info(func: str, msg: str):
    if LOGGER_AVAILABLE:
        _logger.log_info_c(_c_str(func), _c_str(msg))
    else:
        _python_fallback_log(func, 0, "unknown", msg, "INFO")
