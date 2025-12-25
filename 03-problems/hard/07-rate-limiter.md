# Problem 7: Rate Limiter

**Difficulty**: Hard  
**Time to Solve**: 70-90 minutes  
**Companies**: Cloudflare, AWS, Google Cloud, Stripe

## Problem Statement

Design a rate limiter system that supports:
1. Multiple rate limiting algorithms
2. Per-user/Per-IP rate limiting
3. Different time windows
4. Distributed rate limiting
5. Rule configuration
6. Quota management

---

## Class Diagram

```
┌────────────────────────┐
│   RateLimiter          │
├────────────────────────┤
│ - rules                │
│ - algorithms           │
│ - storage              │
├────────────────────────┤
│ + allowRequest()       │
│ + addRule()            │
│ + resetQuota()         │
│ + getUsage()           │
└──────┬─────────────────┘
       │
   ┌───┴────┬─────────┬──────────┐
   ▼        ▼         ▼          ▼
┌──────┐┌────────┐┌────────┐┌─────────┐
│ Rule ││Algorithm│ Storage││ Request │
├──────┤├────────┤├────────┤├─────────┤
│-limit││-check()││-get()  ││-clientId│
│-window│        ││-set()  ││-resource│
└──────┘└────────┘└────────┘└─────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <map>
#include <set>
#include <memory>
#include <string>
#include <queue>
#include <ctime>
#include <mutex>
#include <algorithm>

using namespace std;

// ============== Enums ==============

enum class RateLimitAlgorithm {
    TOKEN_BUCKET,
    SLIDING_WINDOW,
    FIXED_WINDOW,
    LEAKY_BUCKET
};

enum class TimeUnit {
    SECOND,
    MINUTE,
    HOUR,
    DAY
};

// ============== Request ==============

class Request {
private:
    string clientId;
    string resource;
    time_t timestamp;
    
public:
    Request(const string& client, const string& res)
        : clientId(client), resource(res), timestamp(time(nullptr)) {}
    
    string getClientId() const { return clientId; }
    string getResource() const { return resource; }
    time_t getTimestamp() const { return timestamp; }
};

// ============== Rate Limit Rule ==============

class RateLimitRule {
private:
    string ruleId;
    string name;
    int limit;
    int windowSeconds;
    RateLimitAlgorithm algorithm;
    vector<string> appliesTo; // client IDs or IP addresses
    
public:
    RateLimitRule(const string& id, const string& n, int lim, int window,
                 RateLimitAlgorithm algo)
        : ruleId(id), name(n), limit(lim), windowSeconds(window), algorithm(algo) {}
    
    string getId() const { return ruleId; }
    string getName() const { return name; }
    int getLimit() const { return limit; }
    int getWindowSeconds() const { return windowSeconds; }
    RateLimitAlgorithm getAlgorithm() const { return algorithm; }
    
    void addClient(const string& clientId) {
        appliesTo.push_back(clientId);
    }
    
    bool appliesTo Client(const string& clientId) const {
        if (appliesTo.empty()) return true; // Applies to all
        return find(appliesTo.begin(), appliesTo.end(), clientId) != appliesTo.end();
    }
    
    void display() const {
        cout << "Rule: " << name << " (" << ruleId << ")" << endl;
        cout << "  Limit: " << limit << " requests per " << windowSeconds << " seconds" << endl;
        cout << "  Algorithm: " << (int)algorithm << endl;
    }
};

// ============== Token Bucket Algorithm ==============

class TokenBucket {
private:
    int capacity;
    int tokensPerSecond;
    double tokens;
    time_t lastRefill;
    mutex bucketMutex;
    
public:
    TokenBucket(int cap, int rate)
        : capacity(cap), tokensPerSecond(rate), tokens(cap), lastRefill(time(nullptr)) {}
    
    bool allowRequest(int tokensNeeded = 1) {
        lock_guard<mutex> lock(bucketMutex);
        
        refill();
        
        if (tokens >= tokensNeeded) {
            tokens -= tokensNeeded;
            return true;
        }
        
        return false;
    }
    
    void refill() {
        time_t now = time(nullptr);
        double elapsed = difftime(now, lastRefill);
        
        if (elapsed > 0) {
            tokens = min((double)capacity, tokens + elapsed * tokensPerSecond);
            lastRefill = now;
        }
    }
    
    int getAvailableTokens() {
        lock_guard<mutex> lock(bucketMutex);
        refill();
        return (int)tokens;
    }
};

// ============== Sliding Window Counter ==============

class SlidingWindowCounter {
private:
    int limit;
    int windowSeconds;
    queue<time_t> timestamps;
    mutex windowMutex;
    
public:
    SlidingWindowCounter(int lim, int window)
        : limit(lim), windowSeconds(window) {}
    
    bool allowRequest() {
        lock_guard<mutex> lock(windowMutex);
        
        time_t now = time(nullptr);
        
        // Remove timestamps outside window
        while (!timestamps.empty() && now - timestamps.front() >= windowSeconds) {
            timestamps.pop();
        }
        
        if (timestamps.size() < limit) {
            timestamps.push(now);
            return true;
        }
        
        return false;
    }
    
    int getCurrentCount() {
        lock_guard<mutex> lock(windowMutex);
        
        time_t now = time(nullptr);
        
        // Remove timestamps outside window
        while (!timestamps.empty() && now - timestamps.front() >= windowSeconds) {
            timestamps.pop();
        }
        
        return timestamps.size();
    }
    
    int getRemainingQuota() {
        return limit - getCurrentCount();
    }
};

// ============== Fixed Window Counter ==============

class FixedWindowCounter {
private:
    int limit;
    int windowSeconds;
    time_t windowStart;
    int count;
    mutex windowMutex;
    
public:
    FixedWindowCounter(int lim, int window)
        : limit(lim), windowSeconds(window), windowStart(time(nullptr)), count(0) {}
    
    bool allowRequest() {
        lock_guard<mutex> lock(windowMutex);
        
        time_t now = time(nullptr);
        
        // Check if window has expired
        if (now - windowStart >= windowSeconds) {
            windowStart = now;
            count = 0;
        }
        
        if (count < limit) {
            count++;
            return true;
        }
        
        return false;
    }
    
    int getCurrentCount() {
        lock_guard<mutex> lock(windowMutex);
        
        time_t now = time(nullptr);
        
        if (now - windowStart >= windowSeconds) {
            return 0;
        }
        
        return count;
    }
};

// ============== Leaky Bucket Algorithm ==============

class LeakyBucket {
private:
    int capacity;
    double leakRate; // requests per second
    queue<time_t> bucket;
    time_t lastLeak;
    mutex bucketMutex;
    
public:
    LeakyBucket(int cap, double rate)
        : capacity(cap), leakRate(rate), lastLeak(time(nullptr)) {}
    
    bool allowRequest() {
        lock_guard<mutex> lock(bucketMutex);
        
        leak();
        
        if (bucket.size() < capacity) {
            bucket.push(time(nullptr));
            return true;
        }
        
        return false;
    }
    
    void leak() {
        time_t now = time(nullptr);
        double elapsed = difftime(now, lastLeak);
        
        int toLeak = (int)(elapsed * leakRate);
        
        for (int i = 0; i < toLeak && !bucket.empty(); i++) {
            bucket.pop();
        }
        
        if (toLeak > 0) {
            lastLeak = now;
        }
    }
    
    int getQueueSize() {
        lock_guard<mutex> lock(bucketMutex);
        leak();
        return bucket.size();
    }
};

// ============== Rate Limiter Storage ==============

class RateLimiterStorage {
private:
    map<string, unique_ptr<TokenBucket>> tokenBuckets;
    map<string, unique_ptr<SlidingWindowCounter>> slidingWindows;
    map<string, unique_ptr<FixedWindowCounter>> fixedWindows;
    map<string, unique_ptr<LeakyBucket>> leakyBuckets;
    mutex storageMutex;
    
public:
    TokenBucket* getOrCreateTokenBucket(const string& key, int capacity, int rate) {
        lock_guard<mutex> lock(storageMutex);
        
        if (tokenBuckets.find(key) == tokenBuckets.end()) {
            tokenBuckets[key] = make_unique<TokenBucket>(capacity, rate);
        }
        
        return tokenBuckets[key].get();
    }
    
    SlidingWindowCounter* getOrCreateSlidingWindow(const string& key, int limit, int window) {
        lock_guard<mutex> lock(storageMutex);
        
        if (slidingWindows.find(key) == slidingWindows.end()) {
            slidingWindows[key] = make_unique<SlidingWindowCounter>(limit, window);
        }
        
        return slidingWindows[key].get();
    }
    
    FixedWindowCounter* getOrCreateFixedWindow(const string& key, int limit, int window) {
        lock_guard<mutex> lock(storageMutex);
        
        if (fixedWindows.find(key) == fixedWindows.end()) {
            fixedWindows[key] = make_unique<FixedWindowCounter>(limit, window);
        }
        
        return fixedWindows[key].get();
    }
    
    LeakyBucket* getOrCreateLeakyBucket(const string& key, int capacity, double rate) {
        lock_guard<mutex> lock(storageMutex);
        
        if (leakyBuckets.find(key) == leakyBuckets.end()) {
            leakyBuckets[key] = make_unique<LeakyBucket>(capacity, rate);
        }
        
        return leakyBuckets[key].get();
    }
};

// ============== Rate Limiter ==============

class RateLimiter {
private:
    map<string, unique_ptr<RateLimitRule>> rules;
    RateLimiterStorage storage;
    map<string, int> requestCounts; // For statistics
    mutex limiterMutex;
    
    string getStorageKey(const string& clientId, const string& ruleId) {
        return clientId + ":" + ruleId;
    }
    
public:
    RateLimitRule* addRule(const string& id, const string& name, int limit,
                          int windowSeconds, RateLimitAlgorithm algorithm) {
        auto rule = make_unique<RateLimitRule>(id, name, limit, windowSeconds, algorithm);
        RateLimitRule* ptr = rule.get();
        rules[id] = move(rule);
        
        cout << "✓ Rate limit rule added: " << name << endl;
        return ptr;
    }
    
    bool allowRequest(const Request& request) {
        string clientId = request.getClientId();
        string resource = request.getResource();
        
        // Find applicable rules
        for (const auto& [ruleId, rule] : rules) {
            if (!rule->appliesToClient(clientId)) {
                continue;
            }
            
            string key = getStorageKey(clientId, ruleId);
            bool allowed = false;
            
            switch (rule->getAlgorithm()) {
                case RateLimitAlgorithm::TOKEN_BUCKET: {
                    int rate = rule->getLimit() / rule->getWindowSeconds();
                    TokenBucket* bucket = storage.getOrCreateTokenBucket(
                        key, rule->getLimit(), max(1, rate));
                    allowed = bucket->allowRequest();
                    break;
                }
                
                case RateLimitAlgorithm::SLIDING_WINDOW: {
                    SlidingWindowCounter* window = storage.getOrCreateSlidingWindow(
                        key, rule->getLimit(), rule->getWindowSeconds());
                    allowed = window->allowRequest();
                    break;
                }
                
                case RateLimitAlgorithm::FIXED_WINDOW: {
                    FixedWindowCounter* window = storage.getOrCreateFixedWindow(
                        key, rule->getLimit(), rule->getWindowSeconds());
                    allowed = window->allowRequest();
                    break;
                }
                
                case RateLimitAlgorithm::LEAKY_BUCKET: {
                    double rate = (double)rule->getLimit() / rule->getWindowSeconds();
                    LeakyBucket* bucket = storage.getOrCreateLeakyBucket(
                        key, rule->getLimit(), rate);
                    allowed = bucket->allowRequest();
                    break;
                }
            }
            
            if (!allowed) {
                cout << "❌ Request blocked by rule: " << rule->getName() << endl;
                return false;
            }
        }
        
        // Request allowed
        {
            lock_guard<mutex> lock(limiterMutex);
            requestCounts[clientId]++;
        }
        
        return true;
    }
    
    map<string, int> getUsageStats(const string& clientId) {
        map<string, int> stats;
        
        for (const auto& [ruleId, rule] : rules) {
            if (!rule->appliesToClient(clientId)) {
                continue;
            }
            
            string key = getStorageKey(clientId, ruleId);
            
            switch (rule->getAlgorithm()) {
                case RateLimitAlgorithm::TOKEN_BUCKET: {
                    int rate = rule->getLimit() / rule->getWindowSeconds();
                    TokenBucket* bucket = storage.getOrCreateTokenBucket(
                        key, rule->getLimit(), max(1, rate));
                    stats[rule->getName()] = bucket->getAvailableTokens();
                    break;
                }
                
                case RateLimitAlgorithm::SLIDING_WINDOW: {
                    SlidingWindowCounter* window = storage.getOrCreateSlidingWindow(
                        key, rule->getLimit(), rule->getWindowSeconds());
                    stats[rule->getName()] = window->getRemainingQuota();
                    break;
                }
                
                case RateLimitAlgorithm::FIXED_WINDOW: {
                    FixedWindowCounter* window = storage.getOrCreateFixedWindow(
                        key, rule->getLimit(), rule->getWindowSeconds());
                    stats[rule->getName()] = rule->getLimit() - window->getCurrentCount();
                    break;
                }
                
                case RateLimitAlgorithm::LEAKY_BUCKET: {
                    double rate = (double)rule->getLimit() / rule->getWindowSeconds();
                    LeakyBucket* bucket = storage.getOrCreateLeakyBucket(
                        key, rule->getLimit(), rate);
                    stats[rule->getName()] = rule->getLimit() - bucket->getQueueSize();
                    break;
                }
            }
        }
        
        return stats;
    }
    
    void displayRules() const {
        cout << "\n========== RATE LIMIT RULES ==========" << endl;
        for (const auto& [id, rule] : rules) {
            rule->display();
            cout << "---" << endl;
        }
        cout << "======================================\n" << endl;
    }
    
    void displayStats() const {
        cout << "\n========== STATISTICS ==========" << endl;
        cout << "Total request counts by client:" << endl;
        
        for (const auto& [clientId, count] : requestCounts) {
            cout << "  " << clientId << ": " << count << " requests" << endl;
        }
        
        cout << "================================\n" << endl;
    }
};

// ============== API Endpoint (Simulated) ==============

class APIEndpoint {
private:
    string name;
    RateLimiter& rateLimiter;
    
public:
    APIEndpoint(const string& n, RateLimiter& limiter)
        : name(n), rateLimiter(limiter) {}
    
    bool handleRequest(const Request& request) {
        cout << "\n→ Request from " << request.getClientId()
             << " to " << request.getResource() << endl;
        
        if (rateLimiter.allowRequest(request)) {
            cout << "✓ Request allowed" << endl;
            
            // Process request
            processRequest(request);
            return true;
        } else {
            cout << "⛔ Request rate limited (429 Too Many Requests)" << endl;
            return false;
        }
    }
    
    void processRequest(const Request& request) {
        // Simulate request processing
        cout << "  Processing request..." << endl;
    }
};

// ============== Demo ==============

int main() {
    RateLimiter rateLimiter;
    
    cout << "========== Rate Limiter Demo ==========\n" << endl;
    
    // Add rate limiting rules
    cout << "=== Creating Rate Limit Rules ===" << endl;
    
    // Rule 1: Token Bucket - 10 requests per minute
    RateLimitRule* rule1 = rateLimiter.addRule(
        "R001",
        "Global API Limit",
        10,
        60,
        RateLimitAlgorithm::TOKEN_BUCKET
    );
    
    // Rule 2: Sliding Window - 5 requests per 30 seconds
    RateLimitRule* rule2 = rateLimiter.addRule(
        "R002",
        "Premium User Limit",
        5,
        30,
        RateLimitAlgorithm::SLIDING_WINDOW
    );
    rule2->addClient("premium_user");
    
    // Rule 3: Fixed Window - 100 requests per hour
    RateLimitRule* rule3 = rateLimiter.addRule(
        "R003",
        "Hourly Limit",
        100,
        3600,
        RateLimitAlgorithm::FIXED_WINDOW
    );
    
    rateLimiter.displayRules();
    
    // Create API endpoint
    APIEndpoint api("/api/data", rateLimiter);
    
    // Simulate requests
    cout << "=== Simulating API Requests ===" << endl;
    
    // Regular user requests
    cout << "\n--- Regular User Requests ---" << endl;
    for (int i = 0; i < 12; i++) {
        Request req("user123", "/api/data");
        api.handleRequest(req);
        
        if (i == 5) {
            cout << "\n(pause for rate limit recovery...)" << endl;
            // In real scenario, would sleep here
        }
    }
    
    // Premium user requests
    cout << "\n--- Premium User Requests ---" << endl;
    for (int i = 0; i < 7; i++) {
        Request req("premium_user", "/api/data");
        api.handleRequest(req);
    }
    
    // Check usage stats
    cout << "\n=== Usage Statistics ===" << endl;
    
    cout << "\nUser123 remaining quota:" << endl;
    auto stats1 = rateLimiter.getUsageStats("user123");
    for (const auto& [ruleName, remaining] : stats1) {
        cout << "  " << ruleName << ": " << remaining << " requests remaining" << endl;
    }
    
    cout << "\nPremium User remaining quota:" << endl;
    auto stats2 = rateLimiter.getUsageStats("premium_user");
    for (const auto& [ruleName, remaining] : stats2) {
        cout << "  " << ruleName << ": " << remaining << " requests remaining" << endl;
    }
    
    rateLimiter.displayStats();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Multiple Algorithms**
- **Token Bucket**: Smooth rate limiting with burst support
- **Sliding Window**: Accurate rate limiting
- **Fixed Window**: Simple and memory efficient
- **Leaky Bucket**: Smooth output rate

### 2. **Storage Abstraction**
- Per-client, per-rule storage
- Thread-safe operations
- Algorithm-specific data structures

### 3. **Rule Configuration**
- Flexible rule creation
- Client-specific rules
- Multiple algorithms support

---

## Algorithm Comparison

| Algorithm | Pros | Cons | Use Case |
|-----------|------|------|----------|
| Token Bucket | Allows bursts, smooth | Memory per client | API with occasional bursts |
| Sliding Window | Accurate, no boundary issues | More memory | Strict rate limiting |
| Fixed Window | Memory efficient | Boundary spike issue | High throughput APIs |
| Leaky Bucket | Smooth output | Can reject bursts | Message queues |

---

## Follow-up Questions

**Q1: How to implement distributed rate limiting?**
```cpp
class DistributedRateLimiter {
    Redis* redis;
    
    bool allowRequest(string key) {
        // Use Redis INCR with expiry
        int count = redis->incr(key);
        if (count == 1) redis->expire(key, windowSeconds);
        return count <= limit;
    }
};
```

**Q2: How to handle rate limit headers?**
```cpp
struct RateLimitHeaders {
    int limit;
    int remaining;
    time_t reset;
    
    // X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset
};
```

**Q3: How to implement quota management?**
```cpp
class QuotaManager {
    map<string, Quota> quotas;
    
    struct Quota {
        int daily, monthly;
        time_t resetTime;
    };
    
    bool checkQuota(string clientId);
};
```

---

## Compilation

```bash
g++ -std=c++17 rate_limiter.cpp -o limiter -pthread
./limiter
```

---

## Course Complete!

Congratulations! You've completed all **25 LLD problems** covering:
- 8 Easy problems
- 10 Medium problems
- 7 Hard problems

Review the `03-problems/INDEX.md` for the complete catalog.

