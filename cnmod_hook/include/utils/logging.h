#pragma once

#ifndef CNMOD_LOGGING_H
#define CNMOD_LOGGING_H

#include <windows.h>
#include <string>
#include <mutex>
#include <fstream>
#include <chrono>
#include <iomanip>
#include <sstream>

namespace CNMod {

enum class LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3,
    CRITICAL = 4
};

class Logger {
public:
    static Logger& Instance() {
        static Logger instance;
        return instance;
    }
    
    void Initialize(const char* log_file = nullptr, LogLevel console_level = LogLevel::INFO, LogLevel file_level = LogLevel::DEBUG) {
        std::lock_guard<std::mutex> lock(mutex_);
        
        console_level_ = console_level;
        file_level_ = file_level;
        
        if (log_file_.is_open()) {
            log_file_.close();
        }
        
        if (log_file) {
            log_file_.open(log_file, std::ios::out | std::ios::app);
            if (!log_file_.is_open()) {
                OutputDebugStringA("[Logger] Failed to open log file\n");
            }
        }
    }
    
    void Log(LogLevel level, const char* file, int line, const char* func, const char* format, ...) {
        if (level < console_level_ && level < file_level_) return;
        
        va_list args;
        va_start(args, format);
        
        // Format message
        char buffer[4096];
        vsnprintf(buffer, sizeof(buffer), format, args);
        va_end(args);
        
        // Build log line
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()) % 1000;
        
        std::ostringstream oss;
        oss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S") << '.' << std::setfill('0') << std::setw(3) << ms.count()
            << " [" << LevelToString(level) << "] "
            << buffer;
        
        std::string message = oss.str();
        
        // Console output
        if (level >= console_level_) {
            HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
            WORD color = GetColor(level);
            SetConsoleTextAttribute(hConsole, color);
            printf("%s\n", message.c_str());
            SetConsoleTextAttribute(hConsole, FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE);
        }
        
        // File output
        if (level >= file_level_ && log_file_.is_open()) {
            std::lock_guard<std::mutex> lock(file_mutex_);
            log_file_ << message << std::endl;
            log_file_.flush();
        }
        
        // Debug output
        OutputDebugStringA(message.c_str());
        OutputDebugStringA("\n");
    }
    
    void SetConsoleLevel(LogLevel level) { console_level_ = level; }
    void SetFileLevel(LogLevel level) { file_level_ = level; }
    
private:
    Logger() : console_level_(LogLevel::INFO), file_level_(LogLevel::DEBUG) {}
    
    static const char* LevelToString(LogLevel level) {
        switch (level) {
            case LogLevel::DEBUG: return "DEBUG";
            case LogLevel::INFO: return "INFO";
            case LogLevel::WARN: return "WARN";
            case LogLevel::ERROR: return "ERROR";
            case LogLevel::CRITICAL: return "CRITICAL";
            default: return "UNKNOWN";
        }
    }
    
    static WORD GetColor(LogLevel level) {
        switch (level) {
            case LogLevel::DEBUG: return FOREGROUND_BLUE | FOREGROUND_GREEN; // Cyan
            case LogLevel::INFO: return FOREGROUND_GREEN | FOREGROUND_BLUE | FOREGROUND_RED; // White
            case LogLevel::WARN: return FOREGROUND_RED | FOREGROUND_GREEN; // Yellow
            case LogLevel::ERROR: return FOREGROUND_RED | FOREGROUND_INTENSITY; // Bright Red
            case LogLevel::CRITICAL: return FOREGROUND_RED | FOREGROUND_BLUE | FOREGROUND_INTENSITY; // Magenta
            default: return FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE;
        }
    }
    
    LogLevel console_level_;
    LogLevel file_level_;
    std::ofstream log_file_;
    std::mutex mutex_;
    std::mutex file_mutex_;
};

// Macros for easy logging
#define LOG_DEBUG(fmt, ...) CNMod::Logger::Instance().Log(CNMod::LogLevel::DEBUG, __FILE__, __LINE__, __FUNCTION__, fmt, ##__VA_ARGS__)
#define LOG_INFO(fmt, ...)  CNMod::Logger::Instance().Log(CNMod::LogLevel::INFO,  __FILE__, __LINE__, __FUNCTION__, fmt, ##__VA_ARGS__)
#define LOG_WARN(fmt, ...)  CNMod::Logger::Instance().Log(CNMod::LogLevel::WARN,  __FILE__, __LINE__, __FUNCTION__, fmt, ##__VA_ARGS__)
#define LOG_ERROR(fmt, ...) CNMod::Logger::Instance().Log(CNMod::LogLevel::ERROR, __FILE__, __LINE__, __FUNCTION__, fmt, ##__VA_ARGS__)
#define LOG_CRITICAL(fmt, ...) CNMod::Logger::Instance().Log(CNMod::LogLevel::CRITICAL, __FILE__, __LINE__, __FUNCTION__, fmt, ##__VA_ARGS__)

inline void LogInitialize(const char* log_file = "cnmod_hook.log") {
    CNMod::Logger::Instance().Initialize(log_file);
}

} // namespace CNMod

#endif // CNMOD_LOGGING_H