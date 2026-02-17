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
#include <filesystem>
#include <vector>
#include <algorithm>
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
// Logger singleton with detailed function tracking
// -----------------------------------------------------------------
class Logger
{
public:
    static constexpr size_t MAX_LINES = 10000;  // Maximum lines before rotation
    static constexpr int MAX_DAYS = 3;           // Maximum age in days
    
    // Color-coded status levels
    enum class LogLevel {
        SUCCESS = 'G',  // 🟢 Green - passed with flying colors
        WARNING = 'Y',  // 🟡 Yellow - caution/warning  
        ERROR   = 'R',  // 🔴 Red - critical error/RED FLAG
        INFO    = 'W',  // ⚪ White/Gray - informational
        DEBUG   = 'D'   // 🔵 Blue - detailed debug info
    };

    // -----------------------------------------------------------------
    // Retrieve the global instance (thread‑safe since C++11)
    // -----------------------------------------------------------------
    static Logger& instance()
    {
        static Logger s_instance;
        return s_instance;
    }

    // -----------------------------------------------------------------
    // Public API – detailed function tracking with line numbers
    // -----------------------------------------------------------------
    void log_function_enter(const char* func, int line, const char* file, const char* inputs)
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        std::string log_line = format_function_log('D', func, line, file, inputs, "ENTER", "function_started");
        write_to_outputs(log_line);
    }
    
    void log_function_success(const char* func, int line, const char* file, const char* message)
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        std::string log_line = format_function_log('G', func, line, file, "", message, "SUCCESS");
        write_to_outputs(log_line);
    }
    
    void log_function_warning(const char* func, int line, const char* file, const char* message)
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        std::string log_line = format_function_log('Y', func, line, file, "", message, "WARNING");
        write_to_outputs(log_line);
    }
    
    void log_function_error(const char* func, int line, const char* file, const char* message)
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        std::string log_line = format_function_log('R', func, line, file, "", message, "ERROR");
        write_to_outputs(log_line);
    }
    
    void log_function_info(const char* func, int line, const char* file, const char* message)
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        std::string log_line = format_function_log('W', func, line, file, "", message, "INFO");
        write_to_outputs(log_line);
    }
    
    void log_function_debug(const char* func, int line, const char* file, const char* message)
    {
        std::lock_guard<std::mutex> lock(m_mutex);
        std::string log_line = format_function_log('D', func, line, file, "", message, "DEBUG");
        write_to_outputs(log_line);
    }

    // -----------------------------------------------------------------
    // Legacy API – status is a single char: 'S','F','W','I' (info)
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

        // 2) Write to log file with rotation
        if (m_file.is_open()) {
            m_file << line;
            m_lineCount++;
            
            // Check if we need rotation
            if (m_lineCount >= MAX_LINES) {
                rotate_logs();
            }
        }
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

    // -----------------------------------------------------------------
    // Helper methods for detailed function logging
    // -----------------------------------------------------------------
    std::string get_status_emoji(char status) {
        switch (status) {
            case 'G': return "🟢";  // Green - Success
            case 'Y': return "🟡";  // Yellow - Warning  
            case 'R': return "🔴";  // Red - Error
            case 'W': return "⚪";  // White - Info
            case 'D': return "🔵";  // Blue - Debug
            default:  return "❓";  // Unknown
        }
    }
    
    std::string format_function_log(char status, const char* func, int line, const char* file, 
                                   const char* inputs, const char* expected_actual, const char* status_text) {
        std::ostringstream oss;
        oss << "[" << current_timestamp() << "] " 
            << get_status_emoji(status) << " "
            << func << "(line " << line << ") in " << file << ": ";
        
        if (strlen(inputs) > 0) {
            oss << "INPUT(" << inputs << ") -> ";
        }
        
        if (strlen(expected_actual) > 0) {
            oss << expected_actual << " ";
        }
        
        oss << get_status_emoji(status) << " " << status_text << "\r\n";
        return oss.str();
    }
    
    void write_to_outputs(const std::string& log_line) {
        // 1) Write to console (if we have one)
        if (m_consoleAllocated) {
            DWORD written = 0;
            WriteConsoleA(m_hConsole,
                          log_line.c_str(),
                          static_cast<DWORD>(log_line.size()),
                          &written,
                          nullptr);
        }

        // 2) Write to log file with rotation
        if (m_file.is_open()) {
            m_file << log_line;
            m_lineCount++;
            
            // Check if we need rotation
            if (m_lineCount >= MAX_LINES) {
                rotate_logs();
            }
        }
    }

private:
    // -----------------------------------------------------------------
    // Private ctor – creates console (optional) and opens file
    // -----------------------------------------------------------------
    Logger() : m_lineCount(0)
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

        // 2) Clean up old logs and open current log file
        cleanup_old_logs();
        open_log_file();
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
    size_t                   m_lineCount = 0;
    
    void open_log_file() {
        std::wstring logPath = L"tetris_overlay.log";
        
        // Count existing lines if file exists
        if (std::filesystem::exists(logPath)) {
            std::ifstream inFile(logPath);
            m_lineCount = std::count(std::istreambuf_iterator<char>(inFile),
                                   std::istreambuf_iterator<char>(), '\n');
        }
        
        m_file.open(logPath, std::ios::out | std::ios::app);
        if (!m_file) {
            info("Logger::open_log_file", "Failed to open log file, only console will be used");
        }
    }
    
    void rotate_logs() {
        m_file.close();
        
        // Create timestamped backup
        auto now = std::chrono::system_clock::now();
        auto tt = std::chrono::system_clock::to_time_t(now);
        std::tm tm;
        localtime_s(&tm, &tt);
        
        std::ostringstream oss;
        oss << "tetris_overlay_" 
            << std::put_time(&tm, "%Y%m%d_%H%M%S") 
            << ".log";
        
        std::string backupName = oss.str();
        std::filesystem::rename("tetris_overlay.log", backupName);
        
        // Clean up old logs
        cleanup_old_logs();
        
        // Open new log file
        m_lineCount = 0;
        open_log_file();
        
        info("Logger::rotate_logs", ("Log rotated, backup saved as " + backupName).c_str());
    }
    
    void cleanup_old_logs() {
        try {
            auto now = std::chrono::system_clock::now();
            auto cutoff = now - std::chrono::hours(24 * MAX_DAYS);
            
            for (const auto& entry : std::filesystem::directory_iterator(".")) {
                if (entry.path().extension() == ".log" && 
                    entry.path().filename().string().starts_with("tetris_overlay_")) {
                    
                    auto ftime = std::filesystem::last_write_time(entry.path());
                    auto sftime = std::chrono::time_point_cast<std::chrono::system_clock::duration>(
                        ftime - std::filesystem::file_time_type::clock::now()
                        + std::chrono::system_clock::now());
                    
                    if (sftime < cutoff) {
                        std::filesystem::remove(entry.path());
                        info("Logger::cleanup_old_logs", 
                             ("Removed old log: " + entry.path().filename().string()).c_str());
                    }
                }
            }
        } catch (const std::exception& e) {
            // Don't let cleanup errors break logging
            info("Logger::cleanup_old_logs", 
                 ("Cleanup failed: " + std::string(e.what())).c_str());
        }
    }
};

// -----------------------------------------------------------------
// Helper macros – automatically inject __func__, __LINE__, and file
// -----------------------------------------------------------------
#define LOG_SUCCESS(msg)   Logger::instance().success(__func__, (msg))
#define LOG_FAIL(msg)      Logger::instance().fail   (__func__, (msg))
#define LOG_WARN(msg)      Logger::instance().warn   (__func__, (msg))
#define LOG_INFO(msg)      Logger::instance().info   (__func__, (msg))

// -----------------------------------------------------------------
// MANDATORY Function Logging Macros - EVERY function must use these
// -----------------------------------------------------------------
#define LOG_FUNCTION_ENTER(inputs) \
    Logger::instance().log_function_enter(__func__, __LINE__, __FILE__, (inputs))

#define LOG_FUNCTION_SUCCESS(message) \
    Logger::instance().log_function_success(__func__, __LINE__, __FILE__, (message))

#define LOG_FUNCTION_WARNING(message) \
    Logger::instance().log_function_warning(__func__, __LINE__, __FILE__, (message))

#define LOG_FUNCTION_ERROR(message) \
    Logger::instance().log_function_error(__func__, __LINE__, __FILE__, (message))

#define LOG_FUNCTION_INFO(message) \
    Logger::instance().log_function_info(__func__, __LINE__, __FILE__, (message))

#define LOG_FUNCTION_DEBUG(message) \
    Logger::instance().log_function_debug(__func__, __LINE__, __FILE__, (message))

// -----------------------------------------------------------------
// C‑exported thin wrappers – handy for Python via ctypes or for any
// other language that can only call C functions.
// -----------------------------------------------------------------
extern "C" {
    __declspec(dllexport) void log_success_c(const char* func, const char* msg) { Logger::instance().success(func, msg); }
    __declspec(dllexport) void log_fail_c    (const char* func, const char* msg) { Logger::instance().fail   (func, msg); }
    __declspec(dllexport) void log_warn_c    (const char* func, const char* msg) { Logger::instance().warn   (func, msg); }
    __declspec(dllexport) void log_info_c    (const char* func, const char* msg) { Logger::instance().info   (func, msg); }
    
    // Enhanced function logging exports for Python
    __declspec(dllexport) void log_function_enter_c(const char* func, int line, const char* file, const char* inputs) {
        Logger::instance().log_function_enter(func, line, file, inputs);
    }
    __declspec(dllexport) void log_function_success_c(const char* func, int line, const char* file, const char* message) {
        Logger::instance().log_function_success(func, line, file, message);
    }
    __declspec(dllexport) void log_function_warning_c(const char* func, int line, const char* file, const char* message) {
        Logger::instance().log_function_warning(func, line, file, message);
    }
    __declspec(dllexport) void log_function_error_c(const char* func, int line, const char* file, const char* message) {
        Logger::instance().log_function_error(func, line, file, message);
    }
    __declspec(dllexport) void log_function_info_c(const char* func, int line, const char* file, const char* message) {
        Logger::instance().log_function_info(func, line, file, message);
    }
    __declspec(dllexport) void log_function_debug_c(const char* func, int line, const char* file, const char* message) {
        Logger::instance().log_function_debug(func, line, file, message);
    }
}
