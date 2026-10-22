// Logging Implementation

#include "cnmod_hook.h"
#include "utils/logging.h"
#include <windows.h>
#include <chrono>
#include <iomanip>
#include <sstream>

namespace CNMod {

Logger& Logger::Instance() {
    static Logger instance;
    return instance;
}

void Logger::Initialize(const char* log_file, LogLevel console_level, LogLevel file_level) {
    std::lock_guard<std::mutex> lock(mutex_);
    console_level_ = console_level;
    file_level_ = file_level;
    if (log_file_.is_open()) log_file_.close();
    if (log_file) {
        log_file_.open(log_file, std::ios::out | std::ios::app);
    }
}

void Logger::Log(LogLevel level, const char* file, int line, const char* func, const char* format, ...) {
    if (level < console_level_ && level < file_level_) return;
    
    va_list args;
    va_start(args, format);
    char buffer[4096];
    vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    
    auto now = std::chrono::system_clock::now();
    auto time_t = std::chrono::system_clock::to_time_t(now);
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;
    
    std::ostringstream oss;
    oss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S") << '.'
        << std::setfill('0') << std::setw(3) << ms.count()
        << " [" << LevelToString(level) << "] "
        << buffer;
    
    std::string message = oss.str();
    
    if (level >= console_level_) {
        HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
        WORD color = GetColor(level);
        SetConsoleTextAttribute(hConsole, color);
        printf("%s\n", message.c_str());
        SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE);
    }
    
    if (level >= file_level_ && log_file_.is_open()) {
        std::lock_guard<std::mutex> lock(file_mutex_);
        log_file_ << message << std::endl;
        log_file_.flush();
    }
    
    OutputDebugStringA(message.c_str());
    OutputDebugStringA("\n");
}

void Logger::SetConsoleLevel(LogLevel level) { console_level_ = level; }
void Logger::SetFileLevel(LogLevel level) { file_level_ = level; }

const char* Logger::LevelToString(LogLevel level) {
    switch (level) {
        case LogLevel::DEBUG: return "DEBUG";
        case LogLevel::INFO: return "INFO";
        case LogLevel::WARN: return "WARN";
        case LogLevel::ERROR: return "ERROR";
        case LogLevel::CRITICAL: return "CRITICAL";
        default: return "UNKNOWN";
    }
}

WORD Logger::GetColor(LogLevel level) {
    switch (level) {
        case LogLevel::DEBUG: return FOREGROUND_BLUE | FOREGROUND_GREEN;
        case LogLevel::INFO: return FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE;
        case LogLevel::WARN: return FOREGROUND_RED | FOREGROUND_GREEN;
        case LogLevel::ERROR: return FOREGROUND_RED | FOREGROUND_INTENSITY;
        case LogLevel::CRITICAL: return FOREGROUND_RED | FOREGROUND_BLUE | FOREGROUND_INTENSITY;
        default: return FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE;
    }
}

} // namespace CNMod