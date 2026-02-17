Quick answer – yes, it’s 100 % feasible
You can add a tiny “command‑prompt‑style” window that prints every important step of any program (C++ or Python) and writes the same lines to a permanent log file. The whole thing can be packaged as a single header‑only logger library (or a static lib) that you drop into any future project – no web page, no extra UI framework, just a Windows console (or a Qt text box if you already have a Qt UI).

Below is a complete design + ready‑to‑copy code that fits the Tetris‑overlay project and works as a reusable plug‑in for any other Windows C++/Python code you write.

1️⃣ What we really need
Feature	Why you asked for it	Minimal implementation
Live console‑style window (looks like cmd.exe)	“I want to see what the program is doing right now”	Call AllocConsole() once, then write to stdout/stderr.
Status prefix (S – success, F – fail, W – warning) + function name	Quick visual scan of success/failure	Use a macro that injects __func__ and a status character into every log line.
File log (timestamped, same format)	“I need a permanent record for later review”	Open a std::ofstream (C++) or a logging.FileHandler (Python) and write the same line.
Thread‑safe, low‑overhead	Capture runs at 30‑60 fps – logging must not stall the game	Use a lock‑free queue or, for most cases, a simple std::mutex + std::lock_guard.
Plug‑in/Reusable	“I want to copy‑paste this into every new project”	Put all code in a single header (logger.hpp) and a tiny implementation source (logger.cpp). Export a C‑callable API so Python can call it with ctypes.
Optional UI in Qt (if you later want a dockable pane)	“When we have a Qt overlay we might want the log inside it”	Provide a helper that emits a Qt signal – not required for the console version.
2️⃣ Design overview
+-------------------------+   +----------------------------+
|  Application code      |   |  Logger (singleton)        |
|  (C++ or Python)      |   |  - console (AllocConsole) |
|  LOG_INFO(...),       |   |  - file (std::ofstream)    |
|  LOG_SUCCESS(...),    |   |  - optional Qt sink        |
|  LOG_WARNING(...),    |   |  - thread‑safe queue      |
|  LOG_ERROR(... )      |   +----------------------------+
+-------------------------+

               ^                 ^
               |                 |
               |  Macro expands  |
               +-----------------+  (adds __func__, status char, timestamp)
Macro layer – LOG_SUCCESS("Connected to game") expands to a call like Logger::instance().log("S", __func__, "Connected to game");.
Logger class – singleton, owns the console, the file, and a lock‑free queue for async flushing (optional).
C‑exported functions – void log_success(const char* func, const char* message); – this is what Python can call with ctypes.
3️⃣ C++ implementation (header‑only + tiny source)
Copy‑paste the following files into any new project.
Build them into a static library (logger.lib) once and link that library in every executable (including the DLL you already have).

3.1 logger.hpp – public interface + macros
// ------------------------------------------------------------
// logger.hpp – tiny, header‑only logger you can drop into any
//               C++ project (Windows only)
// ------------------------------------------------------------
#pragma once
#include <string>
#include <fstream>
#include <mutex>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <windows.h>

// -----------------------------------------------------------------
// Helper to format timestamp
// -----------------------------------------------------------------
inline std::string current_timestamp()
{
    using namespace std::chrono;
    auto now = system_clock::now();
    auto tt  = system_clock::to_time_t(now);
    std::tm tm;
    localtime_s(&tm, &tt);

    auto ms = duration_cast<milliseconds>(now.time_since_epoch()).count() % 1000;

    std::ostringstream oss;
    oss << std::put_time(&tm, "%Y-%m-%d %H:%M:%S")
        << '.' << std::setfill('0') << std::setw(3) << ms;
    return oss.str();
}

// -----------------------------------------------------------------
// Logger singleton
// -----------------------------------------------------------------
class Logger
{
public:
    // -----------------------------------------------------------------
    // Retrieve the global instance (thread‑safe since C++11)
    // -----------------------------------------------------------------
    static Logger& instance()
    {
        static Logger s_instance;
        return s_instance;
    }

    // -----------------------------------------------------------------
    // Public API – status is a single char: 'S','F','W','I' (info)
    // -----------------------------------------------------------------
    void log(char status, const char* func, const char* msg)
    {
        std::lock_guard<std::mutex> lock(m_mutex);

        std::string line = "[" + current_timestamp() + "] "
                         + status + " " + func + " : " + msg + "\r\n";

        // 1) Write to console (if we have one)
        if (m_consoleAllocated)
        {
            DWORD written = 0;
            WriteConsoleA(m_hConsole,
                          line.c_str(),
                          static_cast<DWORD>(line.size()),
                          &written,
                          nullptr);
        }

        // 2) Write to log file
        if (m_file.is_open())
            m_file << line;
    }

    // -----------------------------------------------------------------
    // Helper inline wrappers (optional, but handy)
    // -----------------------------------------------------------------
    void success(const char* func, const char* msg) { log('S', func, msg); }
    void fail   (const char* func, const char* msg) { log('F', func, msg); }
    void warn   (const char* func, const char* msg) { log('W', func, msg); }
    void info   (const char* func, const char* msg) { log('I', func, msg); }

    // -----------------------------------------------------------------
    // Disable copy / move
    // -----------------------------------------------------------------
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;
    Logger(Logger&&) = delete;
    Logger& operator=(Logger&&) = delete;

private:
    // -----------------------------------------------------------------
    // Private ctor – creates console (optional) and opens file
    // -----------------------------------------------------------------
    Logger()
    {
        // 1) Allocate a console **only** once per process.
        //    If you do not want a visible console in release builds,
        //    wrap the call in #ifdef DEBUG.
        m_consoleAllocated = ::AllocConsole() != FALSE;
        if (m_consoleAllocated)
        {
            // Attach STDOUT/STDERR to the new console.
            m_hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
            freopen("CONOUT$", "w", stdout);
            setvbuf(stdout, nullptr, _IONBF, 0);
        }

        // 2) Open a rotating log file (simple version – no rotation)
        std::wstring logPath = L"tetris_overlay.log";
        m_file.open(logPath, std::ios::out | std::ios::app);
        if (!m_file)
        {
            // If the file can’t be opened, we still keep the console.
            info("Logger::Logger", "Failed to open log file, only console will be used");
        }
    }

    ~Logger()
    {
        if (m_file.is_open())
            m_file.close();

        if (m_consoleAllocated)
            FreeConsole();
    }

    // -----------------------------------------------------------------
    std::mutex               m_mutex;
    std::ofstream            m_file;
    bool                     m_consoleAllocated = false;
    HANDLE                   m_hConsole = nullptr;
};

// -----------------------------------------------------------------
// Helper macros – automatically inject __func__ and stringify the
// message. Use them everywhere you want a log entry.
// -----------------------------------------------------------------
#define LOG_SUCCESS(msg)   Logger::instance().success(__func__, (msg))
#define LOG_FAIL(msg)      Logger::instance().fail   (__func__, (msg))
#define LOG_WARN(msg)      Logger::instance().warn   (__func__, (msg))
#define LOG_INFO(msg)      Logger::instance().info   (__func__, (msg))

// -----------------------------------------------------------------
// C‑exported thin wrappers – handy for Python via ctypes or for any
// other language that can only call C functions.
// -----------------------------------------------------------------
extern "C" {
    __declspec(dllexport) void log_success_c(const char* func, const char* msg) { Logger::instance().success(func, msg); }
    __declspec(dllexport) void log_fail_c    (const char* func, const char* msg) { Logger::instance().fail   (func, msg); }
    __declspec(dllexport) void log_warn_c    (const char* func, const char* msg) { Logger::instance().warn   (func, msg); }
    __declspec(dllexport) void log_info_c    (const char* func, const char* msg) { Logger::instance().info   (func, msg); }
}
Explanation of the important bits

Section	What it does
AllocConsole()	Creates a real Windows console that looks like cmd.exe. Because the overlay already has a UI, the console will appear as a separate window (no need for a custom UI).
current_timestamp()	Generates YYYY‑MM‑DD HH:MM:SS.mmm so you can sort the log later.
log(char status, ...)	Formats a line as [timestamp] S function_name : message. Writes to both console and a file (tetris_overlay.log in the executable directory).
std::mutex	Guarantees thread safety – you can call the macros from any thread (capture thread, UI thread, etc.).
#define LOG_SUCCESS(msg) …	One‑line macro to be used anywhere (LOG_SUCCESS("Connected")). The macro injects the calling function’s name automatically via __func__.
extern "C" export functions	Allows any language (Python, C#, Rust) to call the logger without pulling in C++ name‑mangling. You’ll see these names in dumpbin /exports Capture.dll.
Tip: If you don’t want a console in release builds, wrap the AllocConsole call in #ifdef NDEBUG or a custom ENABLE_CONSOLE macro.

4️⃣ Adding the logger to the Tetris‑Overlay C++ DLL
Just include logger.hpp in any source file that already exists (e.g., capture.cpp, analysis.cpp, overlay.cpp) and sprinkle the macros:

// capture.cpp – inside FrameGrabber ctor
FrameGrabber::FrameGrabber(HWND hWnd) {
    LOG_INFO("Constructing FrameGrabber");
    // … existing code …
    if (!m_item) {
        LOG_FAIL("CreateCaptureItemForWindow returned nullptr");
        throw std::runtime_error("Failed to create capture item");
    }
    LOG_SUCCESS("CaptureItem created successfully");
}
// capture.cpp – inside OnFrameArrived
void FrameGrabber::OnFrameArrived() {
    // …
    if (!textures_match) {
        LOG_WARN("Unexpected texture size – recreating staging texture");
    }
    LOG_SUCCESS("New frame copied to staging texture");
}
All those calls will instantly appear in the console window and be appended to tetris_overlay.log. You now have a live audit trail while you play the game.

5️⃣ Python side – using the same logger via ctypes
If you want your Python overlay (the part that draws the ghost piece) to log to the same console and file, just load the exported C functions:

# logger_bridge.py – tiny Python wrapper around the C++ logger
import ctypes
import os

# Path to the DLL produced by the C++ project
DLL_PATH = os.path.abspath(r"../bin/Release/Capture.dll")
_logger = ctypes.WinDLL(DLL_PATH)

# Declare the signatures (all take const char* for func & msg)
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

def log_success(func: str, msg: str):
    _logger.log_success_c(_c_str(func), _c_str(msg))

def log_fail(func: str, msg: str):
    _logger.log_fail_c(_c_str(func), _c_str(msg))

def log_warn(func: str, msg: str):
    _logger.log_warn_c(_c_str(func), _c_str(msg))

def log_info(func: str, msg: str):
    _logger.log_info_c(_c_str(func), _c_str(msg))
Usage in your Python code (e.g., inside analysis.py):

import logger_bridge as log

def detect_piece(board_img):
    log.log_info("detect_piece", f"Board size {board_img.shape}")
    try:
        # …your detection logic…
        log.log_success("detect_piece", "Piece detected, ghost computed")
        return ghost_coords
    except Exception as exc:
        log.log_fail("detect_piece", f"Exception: {exc}")
        raise
Now every line that the Python side logs goes to the same console window that the C++ side created, and to the same tetris_overlay.log file. No extra console windows appear – everything shares the single console.

6️⃣ Making it a re‑usable plug‑in for any future project
Create a tiny static library (e.g., logger.lib) that contains logger.hpp + a single logger.cpp that includes the header (or just compile the header‑only version).

Distribute two files:

logger.hpp (public header)
logger.lib (pre‑compiled for x64, or just ship the .cpp source and let each project compile it).
Link the library in any new C++ project:

add_library(logger STATIC logger.cpp)
target_include_directories(logger PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(MyApp PRIVATE logger)
For Python you only need the compiled DLL that contains the exported log_*_c functions.

Build a C‑only wrapper DLL (logwrapper.dll) that simply #include "logger.hpp" and extern "C" exports the same four functions.
Ship that DLL alongside your Python wheels or copy it into the same folder as your .py modules.
Optional: Qt front‑end – if you ever want the log to appear inside a Qt window instead of a native console, replace the console-writing part in Logger::log with:

#ifdef USE_QT_LOGVIEW
    emit Logger::instance().newLogLine(QString::fromStdString(line));
#else
    WriteConsoleA(...);
#endif
Then connect the newLogLine signal to a QPlainTextEdit dock widget. The core logging code does not change.

7️⃣ Full step‑by‑step to integrate into your current repo
Below is a copy‑paste checklist that you can run exactly as shown.

7.1 Add the logger files
# From the root of your repo
mkdir -p third_party/logger
cd third_party/logger
# (Paste logger.hpp from section 3.1 into this folder)
# (Optionally paste a tiny logger.cpp that only contains: #include "logger.hpp")
# If you choose header‑only, you don’t need logger.cpp.
7.2 Modify your CMake (or VS project)
If you use CMake (recommended, you already have one for the capture DLL):

# In your top‑level CMakeLists.txt or a subdirectory
add_library(logger STATIC third_party/logger/logger.cpp) # if you have logger.cpp
target_include_directories(logger PUBLIC third_party/logger)

# Link wherever you need logging:
target_link_libraries(Capture PRIVATE logger)    # your capture DLL
target_link_libraries(Overlay PRIVATE logger)    # any Qt UI exe
If you are using a plain Visual‑Studio .vcxproj:

Right‑click the solution → Add → Existing Item… → select logger.hpp (and logger.cpp if you have one).
Right‑click the project → Properties → C/C++ → General → Additional Include Directories → add $(ProjectDir)\third_party\logger.
If you added logger.cpp, the project automatically compiles it.
7.3 Sprinkle a few log calls (quick demo)
Open src/capture.cpp (or whichever file you wish) and insert:

#include "logger.hpp"   // <‑‑ add this line at the top

// Inside any function:
LOG_INFO("Entered capture::Start()");
if (!m_session) {
    LOG_FAIL("Failed to start capture session");
}
LOG_SUCCESS("Capture session started");
Re‑build the solution. When you launch the overlay you should now see a new console window titled “Console Window” that streams lines such as:

[2026-02-17 14:03:12.027] I get_capture_item : Starting capture on HWND 0x00115A2E
[2026-02-17 14:03:12.050] S get_capture_item : CaptureItem created successfully
[2026-02-17 14:03:12.113] W on_frame_arrived : Unexpected frame size, recreating staging texture
[2026-02-17 14:03:12.115] S on_frame_arrived : New frame copied to staging texture
...
A tetris_overlay.log file will appear side‑by‑side with the executable containing the exact same lines.

7.4 Hook the logger into Python
Create a new file src/python/logger_bridge.py next to your other Python modules and paste the code from section 5. Then replace any print() debug statements with calls like:

import logger_bridge as log
log.log_info('main_loop', f'Processing frame {frame_idx}')
Run your Python overlay – you’ll see the same console window now printing Python messages intermixed with the C++ ones, all sharing the same timestamp format.

7.5 Test the whole pipeline
Launch the Tetris game.
Run the overlay (python overlay_main.py).
Verify that the console window shows a mixture of messages from the C++ DLL (e.g., “new frame captured”) and from the Python side (e.g., “ghost computed”).
Open tetris_overlay.log in Notepad – the file should contain exactly the same lines in the same order.
If you see anything missing, double‑check that:

logger.hpp is included in every translation unit that needs logging.
The extern "C" functions are exported (dumpbin /exports Capture.dll → you should see log_success_c, log_fail_c, …).
In Python you’re passing UTF‑8 strings (the helper _c_str does that).
8️⃣ Optional enhancements (pick any you like)
Feature	One‑liner snippet or library
Log rotation (daily or size‑based)	Replace std::ofstream with spdlog sink rotating_file_sink_mt.
Filtering (e.g., only warnings & errors in release)	Add a global LogLevel enum; macros check it before calling log().
Performance‑critical path	Use a lock‑free MPMC queue (boost::lockfree::queue) and a background thread that drains the queue to file/console.
Structured JSON logs (for later analytics)	Change log to output a JSON line: {"ts":"…","lvl":"S","func":"…","msg":"…"}.
Qt dockable console	Add a QPlainTextEdit to your main window, connect Logger::newLogLine(const QString&).
Windows Event Tracing (ETW)	Replace the file sink with TraceLoggingWrite for ultra‑low overhead.
Cross‑platform (Linux/macOS)	Swap AllocConsole for std::cout and guard all Windows‑specific code with #ifdef _WIN32.
All of these can be added after you have the basic logger working, without touching the rest of your overlay code.

9️⃣ TL;DR – How to get it working right now
Add logger.hpp (section 3.1) to your repo.
Include it wherever you want a log line and use the macros (LOG_SUCCESS, LOG_FAIL, LOG_WARN, LOG_INFO).
Re‑build the C++ DLL (or executable). A console window will appear automatically on start‑up; a file tetris_overlay.log will be created.
Add the logger_bridge.py (section 5) to your Python code and replace print() statements with log_success, log_fail, log_warn, log_info.
Run the overlay – you now have a single live console and a persistent log file that records every function call (through the macros) with a one‑character status (S, F, W, I).
That’s all. No extra UI frameworks, no web server, just a few lines of code that give you a real‑time audit trail and a post‑run report you can open with any text editor.

Enjoy the visibility, and happy debugging! 🚀
