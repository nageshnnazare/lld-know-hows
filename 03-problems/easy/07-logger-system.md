# Problem 7: Logger System

**Difficulty**: Easy  
**Time to Solve**: 20-25 minutes  
**Companies**: Almost all companies

## Problem Statement

Design a logging system that can:
1. Log messages at different levels (DEBUG, INFO, WARN, ERROR, FATAL)
2. Write to multiple destinations (Console, File, Database)
3. Support log filtering by level
4. Thread-safe logging
5. Log formatting with timestamp, level, message
6. Singleton pattern for global access

### Requirements

**Functional Requirements**:
- Multiple log levels
- Multiple output sinks (Console, File)
- Configurable minimum log level
- Timestamp for each log
- Thread-safe operations
- Easy to add new sinks

**Non-Functional Requirements**:
- Singleton instance
- Minimal performance overhead
- Buffer for file writing
- Rotation for large log files

---

## Concepts Involved

1. **Design Patterns**:
   - **Singleton** (Logger instance)
   - **Chain of Responsibility** (Log level filtering)
   - **Observer/Strategy** (Multiple sinks)
2. **Concurrency**: Thread-safe logging
3. **SOLID**: Open/Closed, Single Responsibility

---

## Class Diagram

```
┌────────────────────┐
│   Logger           │ ◄──── Singleton
├────────────────────┤
│ - instance         │
│ - minLevel         │
│ - sinks: vector    │
├────────────────────┤
│ + getInstance()    │
│ + log(level, msg)  │
│ + addSink()        │
│ + setLevel()       │
└────────┬───────────┘
         │
         │ has
         ▼
┌────────────────────┐
│   LogSink          │ ◄──── Abstract
├────────────────────┤
│ + write(entry)     │
└────────┬───────────┘
         │
    ┌────┴─────┬─────────┬──────────┐
    ▼          ▼         ▼          ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐
│Console  ││  File   ││Database ││ Remote  │
│  Sink   ││  Sink   ││  Sink   ││  Sink   │
└─────────┘└─────────┘└─────────┘└─────────┘

┌────────────────────┐
│   LogEntry         │
├────────────────────┤
│ - timestamp        │
│ - level            │
│ - message          │
│ - threadId         │
├────────────────────┤
│ + format()         │
└────────────────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <memory>
#include <mutex>
#include <ctime>
#include <sstream>
#include <iomanip>
#include <thread>
#include <queue>

using namespace std;

// ============== Enums ==============

enum class LogLevel {
    DEBUG = 0,
    INFO = 1,
    WARN = 2,
    ERROR = 3,
    FATAL = 4
};

// ============== Log Entry ==============

class LogEntry {
private:
    time_t timestamp;
    LogLevel level;
    string message;
    thread::id threadId;
    
public:
    LogEntry(LogLevel lvl, const string& msg)
        : timestamp(time(nullptr)), level(lvl), message(msg),
          threadId(this_thread::get_id()) {}
    
    string levelToString() const {
        switch(level) {
            case LogLevel::DEBUG: return "DEBUG";
            case LogLevel::INFO:  return "INFO ";
            case LogLevel::WARN:  return "WARN ";
            case LogLevel::ERROR: return "ERROR";
            case LogLevel::FATAL: return "FATAL";
            default: return "UNKNOWN";
        }
    }
    
    string format() const {
        stringstream ss;
        
        // Format timestamp
        char timeStr[26];
        ctime_r(&timestamp, timeStr);
        timeStr[24] = '\0'; // Remove newline
        
        // Format: [TIMESTAMP] [LEVEL] [THREAD] MESSAGE
        ss << "[" << timeStr << "] "
           << "[" << levelToString() << "] "
           << "[Thread-" << threadId << "] "
           << message;
        
        return ss.str();
    }
    
    LogLevel getLevel() const { return level; }
    string getMessage() const { return message; }
    time_t getTimestamp() const { return timestamp; }
};

// ============== Log Sink Interface ==============

class LogSink {
public:
    virtual ~LogSink() = default;
    virtual void write(const LogEntry& entry) = 0;
    virtual void flush() = 0;
};

// ============== Console Sink ==============

class ConsoleSink : public LogSink {
private:
    mutex consoleMutex;
    bool colorEnabled;
    
    string getColorCode(LogLevel level) const {
        if (!colorEnabled) return "";
        
        switch(level) {
            case LogLevel::DEBUG: return "\033[36m";  // Cyan
            case LogLevel::INFO:  return "\033[32m";  // Green
            case LogLevel::WARN:  return "\033[33m";  // Yellow
            case LogLevel::ERROR: return "\033[31m";  // Red
            case LogLevel::FATAL: return "\033[35m";  // Magenta
            default: return "";
        }
    }
    
    string getResetCode() const {
        return colorEnabled ? "\033[0m" : "";
    }
    
public:
    ConsoleSink(bool color = true) : colorEnabled(color) {}
    
    void write(const LogEntry& entry) override {
        lock_guard<mutex> lock(consoleMutex);
        cout << getColorCode(entry.getLevel())
             << entry.format()
             << getResetCode()
             << endl;
    }
    
    void flush() override {
        cout.flush();
    }
};

// ============== File Sink ==============

class FileSink : public LogSink {
private:
    string filename;
    ofstream fileStream;
    mutex fileMutex;
    size_t maxFileSize;
    size_t currentSize;
    int rotationCount;
    
    void rotateFile() {
        fileStream.close();
        
        // Rename old file
        string rotatedName = filename + "." + to_string(++rotationCount);
        rename(filename.c_str(), rotatedName.c_str());
        
        // Open new file
        fileStream.open(filename, ios::app);
        currentSize = 0;
    }
    
public:
    FileSink(const string& fname, size_t maxSize = 10 * 1024 * 1024) // 10MB default
        : filename(fname), maxFileSize(maxSize), currentSize(0), rotationCount(0) {
        
        fileStream.open(filename, ios::app);
        
        if (!fileStream.is_open()) {
            throw runtime_error("Failed to open log file: " + filename);
        }
        
        // Get current file size
        fileStream.seekp(0, ios::end);
        currentSize = fileStream.tellp();
    }
    
    ~FileSink() {
        if (fileStream.is_open()) {
            fileStream.close();
        }
    }
    
    void write(const LogEntry& entry) override {
        lock_guard<mutex> lock(fileMutex);
        
        string formatted = entry.format();
        fileStream << formatted << endl;
        
        currentSize += formatted.length() + 1;
        
        // Check if rotation needed
        if (currentSize >= maxFileSize) {
            rotateFile();
        }
    }
    
    void flush() override {
        lock_guard<mutex> lock(fileMutex);
        fileStream.flush();
    }
};

// ============== Async File Sink (Buffered) ==============

class AsyncFileSink : public LogSink {
private:
    string filename;
    ofstream fileStream;
    mutex queueMutex;
    queue<string> logQueue;
    thread writerThread;
    bool running;
    condition_variable cv;
    
    void writerLoop() {
        while (running || !logQueue.empty()) {
            unique_lock<mutex> lock(queueMutex);
            
            cv.wait_for(lock, chrono::milliseconds(100), [this] {
                return !logQueue.empty() || !running;
            });
            
            while (!logQueue.empty()) {
                string entry = logQueue.front();
                logQueue.pop();
                lock.unlock();
                
                fileStream << entry << endl;
                
                lock.lock();
            }
        }
        
        fileStream.flush();
    }
    
public:
    AsyncFileSink(const string& fname) : filename(fname), running(true) {
        fileStream.open(filename, ios::app);
        
        if (!fileStream.is_open()) {
            throw runtime_error("Failed to open log file: " + filename);
        }
        
        writerThread = thread(&AsyncFileSink::writerLoop, this);
    }
    
    ~AsyncFileSink() {
        running = false;
        cv.notify_all();
        
        if (writerThread.joinable()) {
            writerThread.join();
        }
        
        if (fileStream.is_open()) {
            fileStream.close();
        }
    }
    
    void write(const LogEntry& entry) override {
        lock_guard<mutex> lock(queueMutex);
        logQueue.push(entry.format());
        cv.notify_one();
    }
    
    void flush() override {
        // Wait for queue to be empty
        while (true) {
            {
                lock_guard<mutex> lock(queueMutex);
                if (logQueue.empty()) break;
            }
            this_thread::sleep_for(chrono::milliseconds(10));
        }
        fileStream.flush();
    }
};

// ============== Logger (Singleton) ==============

class Logger {
private:
    static Logger* instance;
    static mutex instanceMutex;
    
    LogLevel minLevel;
    vector<unique_ptr<LogSink>> sinks;
    mutex logMutex;
    
    Logger() : minLevel(LogLevel::DEBUG) {}
    
public:
    static Logger& getInstance() {
        lock_guard<mutex> lock(instanceMutex);
        if (instance == nullptr) {
            instance = new Logger();
        }
        return *instance;
    }
    
    // Delete copy constructor and assignment
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;
    
    void setMinLevel(LogLevel level) {
        lock_guard<mutex> lock(logMutex);
        minLevel = level;
    }
    
    void addSink(unique_ptr<LogSink> sink) {
        lock_guard<mutex> lock(logMutex);
        sinks.push_back(move(sink));
    }
    
    void log(LogLevel level, const string& message) {
        // Filter by minimum level
        if (level < minLevel) {
            return;
        }
        
        LogEntry entry(level, message);
        
        lock_guard<mutex> lock(logMutex);
        
        // Write to all sinks
        for (auto& sink : sinks) {
            sink->write(entry);
        }
    }
    
    // Convenience methods
    void debug(const string& message) { log(LogLevel::DEBUG, message); }
    void info(const string& message) { log(LogLevel::INFO, message); }
    void warn(const string& message) { log(LogLevel::WARN, message); }
    void error(const string& message) { log(LogLevel::ERROR, message); }
    void fatal(const string& message) { log(LogLevel::FATAL, message); }
    
    void flush() {
        lock_guard<mutex> lock(logMutex);
        for (auto& sink : sinks) {
            sink->flush();
        }
    }
    
    static void cleanup() {
        if (instance) {
            instance->flush();
            delete instance;
            instance = nullptr;
        }
    }
};

Logger* Logger::instance = nullptr;
mutex Logger::instanceMutex;

// ============== Macro Helpers ==============

#define LOG_DEBUG(msg) Logger::getInstance().debug(msg)
#define LOG_INFO(msg)  Logger::getInstance().info(msg)
#define LOG_WARN(msg)  Logger::getInstance().warn(msg)
#define LOG_ERROR(msg) Logger::getInstance().error(msg)
#define LOG_FATAL(msg) Logger::getInstance().fatal(msg)

// ============== Demo ==============

void workerThread(int id) {
    for (int i = 0; i < 5; i++) {
        LOG_INFO("Worker " + to_string(id) + " - Iteration " + to_string(i));
        this_thread::sleep_for(chrono::milliseconds(100));
    }
}

int main() {
    Logger& logger = Logger::getInstance();
    
    // Add console sink
    logger.addSink(make_unique<ConsoleSink>(true));
    
    // Add file sink
    logger.addSink(make_unique<FileSink>("application.log", 1024 * 1024)); // 1MB
    
    // Add async file sink
    logger.addSink(make_unique<AsyncFileSink>("async.log"));
    
    cout << "========== Logger System Demo ==========\n" << endl;
    
    // Test different log levels
    LOG_DEBUG("This is a debug message");
    LOG_INFO("Application started successfully");
    LOG_WARN("This is a warning message");
    LOG_ERROR("This is an error message");
    LOG_FATAL("This is a fatal error message");
    
    cout << "\n--- Testing Log Level Filtering ---\n" << endl;
    
    // Set minimum level to WARN
    logger.setMinLevel(LogLevel::WARN);
    
    LOG_DEBUG("This debug won't be logged");
    LOG_INFO("This info won't be logged");
    LOG_WARN("This warning will be logged");
    LOG_ERROR("This error will be logged");
    
    // Reset to DEBUG
    logger.setMinLevel(LogLevel::DEBUG);
    
    cout << "\n--- Testing Multi-threaded Logging ---\n" << endl;
    
    // Multi-threaded logging
    vector<thread> threads;
    for (int i = 0; i < 3; i++) {
        threads.emplace_back(workerThread, i + 1);
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    LOG_INFO("All threads completed");
    
    cout << "\n--- Testing Exception Logging ---\n" << endl;
    
    try {
        LOG_INFO("Attempting risky operation...");
        throw runtime_error("Something went wrong!");
    } catch (const exception& e) {
        LOG_ERROR(string("Exception caught: ") + e.what());
    }
    
    // Cleanup
    Logger::cleanup();
    
    cout << "\n========== Logs written to: ===========" << endl;
    cout << "1. Console (with colors)" << endl;
    cout << "2. application.log (synchronous)" << endl;
    cout << "3. async.log (asynchronous/buffered)" << endl;
    cout << "========================================\n" << endl;
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Singleton Pattern**
- Global access point for logger
- Thread-safe initialization
- Single instance ensures consistent logging

### 2. **Strategy Pattern (Sinks)**
- Multiple output destinations
- Easy to add new sinks
- Each sink handles its own formatting/writing

### 3. **Thread Safety**
- Mutex protection for all operations
- Async file sink with queue for performance
- Safe multi-threaded logging

### 4. **Log Levels**
- Filtering by minimum level
- Different severity levels
- Color coding for console output

---

## Follow-up Questions

**Q1: How to add log rotation based on date?**
```cpp
class DateBasedFileSink : public LogSink {
    string getDateSuffix() {
        time_t now = time(nullptr);
        char buf[20];
        strftime(buf, sizeof(buf), "%Y-%m-%d", localtime(&now));
        return string(buf);
    }
    
    string getCurrentFilename() {
        return baseFilename + "." + getDateSuffix() + ".log";
    }
};
```

**Q2: How to add remote logging (send to server)?**
```cpp
class RemoteSink : public LogSink {
    HttpClient client;
    
    void write(const LogEntry& entry) override {
        json logData = {
            {"level", entry.levelToString()},
            {"message", entry.getMessage()},
            {"timestamp", entry.getTimestamp()}
        };
        client.post("/api/logs", logData);
    }
};
```

**Q3: How to implement log filtering by pattern?**
```cpp
class FilteredSink : public LogSink {
    unique_ptr<LogSink> wrappedSink;
    regex pattern;
    
    void write(const LogEntry& entry) override {
        if (regex_search(entry.getMessage(), pattern)) {
            wrappedSink->write(entry);
        }
    }
};
```

**Q4: How to add structured logging (JSON)?**
```cpp
class JsonLogEntry : public LogEntry {
    string format() const override {
        json j = {
            {"timestamp", getTimestamp()},
            {"level", levelToString()},
            {"message", getMessage()},
            {"thread", threadId}
        };
        return j.dump();
    }
};
```

---

## Compilation & Execution

```bash
g++ -std=c++17 -pthread logger_system.cpp -o logger
./logger
```

**Output files**:
- `application.log` - Synchronous file logging
- `async.log` - Asynchronous buffered logging

---

## Sample Output

```
========== Logger System Demo ==========

[Thu Dec 25 10:30:45 2025] [DEBUG] [Thread-140735268] This is a debug message
[Thu Dec 25 10:30:45 2025] [INFO ] [Thread-140735268] Application started
[Thu Dec 25 10:30:45 2025] [WARN ] [Thread-140735268] This is a warning
[Thu Dec 25 10:30:45 2025] [ERROR] [Thread-140735268] This is an error
[Thu Dec 25 10:30:45 2025] [FATAL] [Thread-140735268] This is a fatal error

--- Testing Multi-threaded Logging ---

[Thu Dec 25 10:30:45 2025] [INFO ] [Thread-140735269] Worker 1 - Iteration 0
[Thu Dec 25 10:30:45 2025] [INFO ] [Thread-140735270] Worker 2 - Iteration 0
[Thu Dec 25 10:30:45 2025] [INFO ] [Thread-140735271] Worker 3 - Iteration 0
```

---

**Next Problem**: `08-url-shortener.md`

