# Problem 8: URL Shortener

**Difficulty**: Easy  
**Time to Solve**: 30-35 minutes  
**Companies**: Google, Amazon, Microsoft, Meta

## Problem Statement

Design a URL shortening service like bit.ly or TinyURL that can:
1. Shorten long URLs to short codes
2. Redirect short codes to original URLs
3. Generate unique short codes
4. Track click analytics
5. Support custom short codes
6. Handle expiration

### Requirements

**Functional Requirements**:
- Generate short URL for long URL
- Redirect short URL to original URL
- Custom short codes (if available)
- Analytics (click count, last accessed)
- Expiration time for URLs
- Delete URLs

**Non-Functional Requirements**:
- Short codes should be unique
- Fast redirection (< 100ms)
- Scalable to billions of URLs
- High availability

---

## Concepts Involved

1. **Algorithms**: Base62 encoding, Hash functions
2. **Design Patterns**: Factory, Repository
3. **Data Structures**: HashMap
4. **System Design**: Database schema, Caching

---

## Class Diagram

```
┌────────────────────┐
│  URLShortener      │ ◄──── Singleton
├────────────────────┤
│ - urlMap: map      │
│ - reverseMap: map  │
│ - analytics: map   │
├────────────────────┤
│ + shortenURL()     │
│ + expandURL()      │
│ + customShorten()  │
│ + deleteURL()      │
└────────┬───────────┘
         │
         │ uses
         ▼
┌────────────────────┐
│   URLEntry         │
├────────────────────┤
│ - shortCode        │
│ - longURL          │
│ - createdAt        │
│ - expiresAt        │
│ - userId           │
└────────────────────┘

┌────────────────────┐
│   Analytics        │
├────────────────────┤
│ - clickCount       │
│ - lastAccessed     │
│ - referrers        │
└────────────────────┘

┌────────────────────┐
│  CodeGenerator     │
├────────────────────┤
│ + generateCode()   │
│ + toBase62()       │
└────────────────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <ctime>
#include <random>
#include <algorithm>
#include <mutex>

using namespace std;

// ============== Analytics ==============

class Analytics {
private:
    int clickCount;
    time_t lastAccessed;
    time_t createdAt;
    
public:
    Analytics() : clickCount(0), lastAccessed(0), createdAt(time(nullptr)) {}
    
    void recordClick() {
        clickCount++;
        lastAccessed = time(nullptr);
    }
    
    int getClickCount() const { return clickCount; }
    time_t getLastAccessed() const { return lastAccessed; }
    time_t getCreatedAt() const { return createdAt; }
    
    void display() const {
        cout << "Clicks: " << clickCount << " | ";
        
        if (lastAccessed > 0) {
            char timeStr[26];
            ctime_r(&lastAccessed, timeStr);
            timeStr[24] = '\0';
            cout << "Last Access: " << timeStr;
        } else {
            cout << "Never accessed";
        }
        cout << endl;
    }
};

// ============== URL Entry ==============

class URLEntry {
private:
    string shortCode;
    string longURL;
    time_t createdAt;
    time_t expiresAt;
    string userId;
    Analytics analytics;
    
public:
    URLEntry(const string& code, const string& url, const string& user = "", 
             int expiryDays = 0)
        : shortCode(code), longURL(url), userId(user) {
        
        createdAt = time(nullptr);
        
        if (expiryDays > 0) {
            expiresAt = createdAt + (expiryDays * 24 * 3600);
        } else {
            expiresAt = 0; // No expiry
        }
    }
    
    string getShortCode() const { return shortCode; }
    string getLongURL() const { return longURL; }
    string getUserId() const { return userId; }
    
    bool isExpired() const {
        if (expiresAt == 0) return false;
        return time(nullptr) > expiresAt;
    }
    
    void recordClick() {
        analytics.recordClick();
    }
    
    const Analytics& getAnalytics() const { return analytics; }
    
    void display() const {
        cout << "\n--- URL Entry ---" << endl;
        cout << "Short Code: " << shortCode << endl;
        cout << "Long URL: " << longURL << endl;
        
        if (!userId.empty()) {
            cout << "Created By: " << userId << endl;
        }
        
        char createdStr[26];
        ctime_r(&createdAt, createdStr);
        createdStr[24] = '\0';
        cout << "Created: " << createdStr << endl;
        
        if (expiresAt > 0) {
            char expiryStr[26];
            ctime_r(&expiresAt, expiryStr);
            expiryStr[24] = '\0';
            cout << "Expires: " << expiryStr << endl;
        }
        
        analytics.display();
        cout << "----------------" << endl;
    }
};

// ============== Code Generator ==============

class CodeGenerator {
private:
    static const string BASE62_CHARS;
    static long long counter;
    random_device rd;
    mt19937 gen;
    
public:
    CodeGenerator() : gen(rd()) {}
    
    // Convert number to base62 string
    string toBase62(long long num) {
        if (num == 0) return string(1, BASE62_CHARS[0]);
        
        string result;
        while (num > 0) {
            result = BASE62_CHARS[num % 62] + result;
            num /= 62;
        }
        
        // Pad to 6 characters
        while (result.length() < 6) {
            result = BASE62_CHARS[0] + result;
        }
        
        return result;
    }
    
    // Generate code from counter (deterministic)
    string generateFromCounter() {
        return toBase62(++counter);
    }
    
    // Generate random code
    string generateRandom(int length = 6) {
        uniform_int_distribution<> dis(0, 61);
        string code;
        
        for (int i = 0; i < length; i++) {
            code += BASE62_CHARS[dis(gen)];
        }
        
        return code;
    }
    
    // Generate from hash
    string generateFromURL(const string& url) {
        hash<string> hasher;
        size_t hashValue = hasher(url);
        
        // Add timestamp to ensure uniqueness
        hashValue ^= time(nullptr);
        
        return toBase62(hashValue);
    }
};

const string CodeGenerator::BASE62_CHARS = 
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";

long long CodeGenerator::counter = 0;

// ============== URL Shortener ==============

class URLShortener {
private:
    static URLShortener* instance;
    static mutex mtx;
    
    unordered_map<string, unique_ptr<URLEntry>> shortToLong;  // short -> entry
    unordered_map<string, string> longToShort;  // long -> short
    unordered_set<string> customCodes;
    CodeGenerator codeGenerator;
    string baseURL;
    
    URLShortener(const string& base = "http://short.url/") : baseURL(base) {}
    
    bool isValidShortCode(const string& code) {
        if (code.empty() || code.length() > 10) return false;
        
        for (char c : code) {
            if (!isalnum(c) && c != '_' && c != '-') {
                return false;
            }
        }
        return true;
    }
    
public:
    static URLShortener* getInstance(const string& baseURL = "http://short.url/") {
        lock_guard<mutex> lock(mtx);
        if (instance == nullptr) {
            instance = new URLShortener(baseURL);
        }
        return instance;
    }
    
    // Shorten URL with auto-generated code
    string shortenURL(const string& longURL, const string& userId = "", 
                     int expiryDays = 0) {
        lock_guard<mutex> lock(mtx);
        
        // Check if already shortened
        auto it = longToShort.find(longURL);
        if (it != longToShort.end()) {
            cout << "URL already shortened!" << endl;
            return baseURL + it->second;
        }
        
        // Generate unique short code
        string shortCode;
        int attempts = 0;
        
        do {
            shortCode = codeGenerator.generateFromURL(longURL);
            attempts++;
            
            if (attempts > 10) {
                // Fallback to random if too many collisions
                shortCode = codeGenerator.generateRandom();
            }
        } while (shortToLong.find(shortCode) != shortToLong.end());
        
        // Create entry
        auto entry = make_unique<URLEntry>(shortCode, longURL, userId, expiryDays);
        shortToLong[shortCode] = move(entry);
        longToShort[longURL] = shortCode;
        
        cout << "✓ URL shortened successfully!" << endl;
        return baseURL + shortCode;
    }
    
    // Shorten with custom code
    string customShortenURL(const string& longURL, const string& customCode,
                           const string& userId = "", int expiryDays = 0) {
        lock_guard<mutex> lock(mtx);
        
        if (!isValidShortCode(customCode)) {
            throw invalid_argument("Invalid custom code format");
        }
        
        if (shortToLong.find(customCode) != shortToLong.end()) {
            throw runtime_error("Custom code already in use");
        }
        
        auto entry = make_unique<URLEntry>(customCode, longURL, userId, expiryDays);
        shortToLong[customCode] = move(entry);
        longToShort[longURL] = customCode;
        customCodes.insert(customCode);
        
        cout << "✓ Custom URL created successfully!" << endl;
        return baseURL + customCode;
    }
    
    // Expand short URL
    string expandURL(const string& shortURL) {
        lock_guard<mutex> lock(mtx);
        
        // Extract short code from URL
        string shortCode = shortURL;
        if (shortURL.find(baseURL) == 0) {
            shortCode = shortURL.substr(baseURL.length());
        }
        
        auto it = shortToLong.find(shortCode);
        if (it == shortToLong.end()) {
            throw runtime_error("Short URL not found");
        }
        
        URLEntry* entry = it->second.get();
        
        // Check expiration
        if (entry->isExpired()) {
            cout << "⚠️  URL has expired" << endl;
            // Optionally delete expired URLs
            return "";
        }
        
        // Record analytics
        entry->recordClick();
        
        return entry->getLongURL();
    }
    
    // Delete URL
    bool deleteURL(const string& shortCode, const string& userId = "") {
        lock_guard<mutex> lock(mtx);
        
        auto it = shortToLong.find(shortCode);
        if (it == shortToLong.end()) {
            return false;
        }
        
        // Check ownership if userId provided
        if (!userId.empty() && it->second->getUserId() != userId) {
            cout << "⚠️  Not authorized to delete this URL" << endl;
            return false;
        }
        
        string longURL = it->second->getLongURL();
        
        shortToLong.erase(it);
        longToShort.erase(longURL);
        customCodes.erase(shortCode);
        
        cout << "✓ URL deleted successfully" << endl;
        return true;
    }
    
    // Get analytics
    const Analytics* getAnalytics(const string& shortCode) {
        lock_guard<mutex> lock(mtx);
        
        auto it = shortToLong.find(shortCode);
        if (it == shortToLong.end()) {
            return nullptr;
        }
        
        return &(it->second->getAnalytics());
    }
    
    // Display URL info
    void displayURLInfo(const string& shortCode) {
        lock_guard<mutex> lock(mtx);
        
        auto it = shortToLong.find(shortCode);
        if (it == shortToLong.end()) {
            cout << "URL not found!" << endl;
            return;
        }
        
        it->second->display();
    }
    
    // List all URLs for user
    void listUserURLs(const string& userId) {
        lock_guard<mutex> lock(mtx);
        
        cout << "\n========== URLs for User: " << userId << " ==========" << endl;
        int count = 0;
        
        for (const auto& [code, entry] : shortToLong) {
            if (entry->getUserId() == userId) {
                cout << baseURL << code << " -> " << entry->getLongURL() << endl;
                count++;
            }
        }
        
        cout << "Total: " << count << " URLs" << endl;
        cout << "====================================================\n" << endl;
    }
    
    // Clean expired URLs
    int cleanExpiredURLs() {
        lock_guard<mutex> lock(mtx);
        
        vector<string> toDelete;
        
        for (const auto& [code, entry] : shortToLong) {
            if (entry->isExpired()) {
                toDelete.push_back(code);
            }
        }
        
        for (const string& code : toDelete) {
            string longURL = shortToLong[code]->getLongURL();
            shortToLong.erase(code);
            longToShort.erase(longURL);
        }
        
        cout << "✓ Cleaned " << toDelete.size() << " expired URLs" << endl;
        return toDelete.size();
    }
    
    void displayStats() {
        lock_guard<mutex> lock(mtx);
        
        cout << "\n========== URL Shortener Stats ==========" << endl;
        cout << "Total URLs: " << shortToLong.size() << endl;
        cout << "Custom URLs: " << customCodes.size() << endl;
        cout << "=========================================\n" << endl;
    }
    
    static void cleanup() {
        delete instance;
        instance = nullptr;
    }
};

URLShortener* URLShortener::instance = nullptr;
mutex URLShortener::mtx;

// ============== Demo ==============

int main() {
    URLShortener* shortener = URLShortener::getInstance("https://tiny.link/");
    
    cout << "========== URL Shortener Demo ==========\n" << endl;
    
    // Test 1: Basic URL shortening
    cout << "=== Test 1: Basic URL Shortening ===" << endl;
    string shortURL1 = shortener->shortenURL(
        "https://www.example.com/very/long/url/path/to/resource?param1=value1&param2=value2",
        "user123"
    );
    cout << "Short URL: " << shortURL1 << "\n" << endl;
    
    // Test 2: Custom short code
    cout << "=== Test 2: Custom Short Code ===" << endl;
    try {
        string shortURL2 = shortener->customShortenURL(
            "https://www.github.com/awesome-project",
            "github",
            "user123"
        );
        cout << "Custom Short URL: " << shortURL2 << "\n" << endl;
    } catch (const exception& e) {
        cout << "Error: " << e.what() << "\n" << endl;
    }
    
    // Test 3: URL expansion (redirection)
    cout << "=== Test 3: URL Expansion ===" << endl;
    try {
        string longURL = shortener->expandURL(shortURL1);
        cout << "Redirecting to: " << longURL << "\n" << endl;
        
        // Access multiple times to test analytics
        shortener->expandURL(shortURL1);
        shortener->expandURL(shortURL1);
    } catch (const exception& e) {
        cout << "Error: " << e.what() << "\n" << endl;
    }
    
    // Test 4: Display analytics
    cout << "=== Test 4: Analytics ===" << endl;
    shortener->displayURLInfo(shortURL1.substr(shortURL1.find_last_of('/') + 1));
    
    // Test 5: URL with expiration
    cout << "\n=== Test 5: URL with Expiration ===" << endl;
    string shortURL3 = shortener->shortenURL(
        "https://www.temporary-content.com/promo",
        "user456",
        7  // Expires in 7 days
    );
    cout << "Short URL (7 days expiry): " << shortURL3 << "\n" << endl;
    
    // Test 6: List user URLs
    cout << "=== Test 6: List User URLs ===" << endl;
    shortener->listUserURLs("user123");
    
    // Test 7: Delete URL
    cout << "=== Test 7: Delete URL ===" << endl;
    shortener->deleteURL("github", "user123");
    
    // Test 8: Stats
    cout << "\n=== Test 8: System Stats ===" << endl;
    shortener->displayStats();
    
    // Test 9: Duplicate URL
    cout << "=== Test 9: Duplicate URL ===" << endl;
    string duplicate = shortener->shortenURL(
        "https://www.example.com/very/long/url/path/to/resource?param1=value1&param2=value2",
        "user123"
    );
    cout << "Same short URL: " << duplicate << "\n" << endl;
    
    // Cleanup
    URLShortener::cleanup();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Base62 Encoding**
- Uses 0-9, A-Z, a-z (62 characters)
- Short codes: 6 characters = 62^6 = 56 billion URLs
- Collision resistant

### 2. **Multiple Generation Strategies**
- Hash-based (from URL + timestamp)
- Counter-based (sequential)
- Random generation
- Custom codes

### 3. **Analytics Tracking**
- Click count
- Last accessed time
- Easy to extend (referrers, geo-location, etc.)

### 4. **Expiration Support**
- Optional expiry time
- Cleanup of expired URLs
- Useful for temporary campaigns

---

## Follow-up Questions

**Q1: How to scale to billions of URLs?**
- Use distributed database (Cassandra, DynamoDB)
- Partition by hash of short code
- Cache frequently accessed URLs (Redis)
- Use CDN for static redirects

**Q2: How to handle high traffic (10K requests/sec)?**
- Redis cache for hot URLs
- Read replicas for database
- Load balancers
- Async analytics (message queue)

**Q3: How to prevent abuse?**
```cpp
class RateLimiter {
    unordered_map<string, queue<time_t>> userRequests;
    
    bool allowRequest(string userId) {
        // Allow 10 requests per minute
        auto& queue = userRequests[userId];
        time_t now = time(nullptr);
        
        while (!queue.empty() && queue.front() < now - 60) {
            queue.pop();
        }
        
        if (queue.size() >= 10) return false;
        
        queue.push(now);
        return true;
    }
};
```

**Q4: How to generate truly unique codes at scale?**
- Use ZooKeeper for distributed counter
- Or use Twitter Snowflake algorithm
- Or partition key space across servers

---

## Database Schema

```sql
CREATE TABLE urls (
    short_code VARCHAR(10) PRIMARY KEY,
    long_url TEXT NOT NULL,
    user_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_expiry (expires_at)
);

CREATE TABLE analytics (
    short_code VARCHAR(10),
    click_count INT DEFAULT 0,
    last_accessed TIMESTAMP,
    FOREIGN KEY (short_code) REFERENCES urls(short_code)
);
```

---

## Compilation & Execution

```bash
g++ -std=c++17 url_shortener.cpp -o urlshort
./urlshort
```

---

**Next Problem**: Moving to Medium difficulty - `medium/02-hotel-booking-system.md`

