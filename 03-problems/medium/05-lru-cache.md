# Problem 5: LRU Cache

**Difficulty**: Medium  
**Time to Solve**: 30-40 minutes  
**Companies**: Google, Facebook, Amazon, Microsoft, Apple

## Problem Statement

Design and implement a data structure for Least Recently Used (LRU) Cache. It should support:
1. `get(key)` - Get the value of the key if exists, otherwise return -1
2. `put(key, value)` - Set or update the value of the key
3. When cache reaches capacity, invalidate the least recently used item before inserting new item
4. All operations should be O(1) time complexity

### Requirements

**Functional Requirements**:
- Fixed capacity cache
- Get operation returns value or -1
- Put operation adds/updates key-value
- Automatic eviction of LRU item when full
- Track access order (most recent to least recent)

**Non-Functional Requirements**:
- O(1) time complexity for get and put
- O(capacity) space complexity
- Thread-safe operations (extension)

---

## Concepts Involved

1. **Data Structures**:
   - **Doubly Linked List** (for order)
   - **Hash Map** (for O(1) access)
2. **Design Patterns**: 
   - Decorator (for thread-safety)
3. **Algorithms**: LRU eviction policy
4. **SOLID**: SRP, OCP

---

## Architecture & Design

### Why Doubly Linked List + HashMap?

```
HashMap for O(1) access:
┌─────┬──────┐
│ Key │ Node*│
├─────┼──────┤
│  1  │  →   │ ──┐
│  2  │  →   │ ──┼──→ Doubly Linked List (maintains order)
│  3  │  →   │ ──┘
└─────┴──────┘

Doubly Linked List for O(1) insertion/deletion:
  HEAD ←→ [Node 3] ←→ [Node 2] ←→ [Node 1] ←→ TAIL
 (Most Recent)                        (Least Recent)
```

### Operations Visualization

**GET(2)**: Move accessed node to head
```
Before: HEAD ←→ [3] ←→ [2] ←→ [1] ←→ TAIL
After:  HEAD ←→ [2] ←→ [3] ←→ [1] ←→ TAIL
```

**PUT(4)** when full: Remove tail, add to head
```
Before: HEAD ←→ [3] ←→ [2] ←→ [1] ←→ TAIL
After:  HEAD ←→ [4] ←→ [3] ←→ [2] ←→ TAIL
        (Node 1 evicted)
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <unordered_map>
#include <list>
#include <mutex>
#include <memory>

using namespace std;

// ============== Basic LRU Cache ==============

template<typename K, typename V>
class LRUCache {
private:
    struct Node {
        K key;
        V value;
        
        Node(const K& k, const V& v) : key(k), value(v) {}
    };
    
    int capacity;
    list<Node> cacheList;  // Doubly linked list: front = most recent
    unordered_map<K, typename list<Node>::iterator> cacheMap;  // Key -> Iterator
    
    // Move node to front (most recently used position)
    void moveToFront(typename list<Node>::iterator it) {
        cacheList.splice(cacheList.begin(), cacheList, it);
    }
    
    // Remove least recently used item (from back)
    void evictLRU() {
        if (cacheList.empty()) return;
        
        K keyToRemove = cacheList.back().key;
        cacheList.pop_back();
        cacheMap.erase(keyToRemove);
        
        cout << "[EVICTED] Key: " << keyToRemove << endl;
    }
    
public:
    LRUCache(int cap) : capacity(cap) {
        if (capacity <= 0) {
            throw invalid_argument("Capacity must be positive");
        }
    }
    
    // Get value by key
    V get(const K& key) {
        auto it = cacheMap.find(key);
        
        if (it == cacheMap.end()) {
            throw runtime_error("Key not found");
        }
        
        // Move to front (most recently used)
        moveToFront(it->second);
        
        return it->second->value;
    }
    
    // Check if key exists
    bool contains(const K& key) const {
        return cacheMap.find(key) != cacheMap.end();
    }
    
    // Put key-value pair
    void put(const K& key, const V& value) {
        auto it = cacheMap.find(key);
        
        if (it != cacheMap.end()) {
            // Key exists - update value and move to front
            it->second->value = value;
            moveToFront(it->second);
            cout << "[UPDATED] Key: " << key << " Value: " << value << endl;
        } else {
            // Key doesn't exist - add new node
            if (cacheList.size() >= capacity) {
                evictLRU();
            }
            
            cacheList.emplace_front(key, value);
            cacheMap[key] = cacheList.begin();
            cout << "[ADDED] Key: " << key << " Value: " << value << endl;
        }
    }
    
    // Remove key
    void remove(const K& key) {
        auto it = cacheMap.find(key);
        
        if (it != cacheMap.end()) {
            cacheList.erase(it->second);
            cacheMap.erase(it);
            cout << "[REMOVED] Key: " << key << endl;
        }
    }
    
    // Get current size
    int size() const {
        return cacheList.size();
    }
    
    // Get capacity
    int getCapacity() const {
        return capacity;
    }
    
    // Clear cache
    void clear() {
        cacheList.clear();
        cacheMap.clear();
        cout << "[CLEARED] Cache emptied" << endl;
    }
    
    // Display cache contents (most recent first)
    void display() const {
        cout << "\n========== LRU Cache ==========" << endl;
        cout << "Capacity: " << capacity << " | Size: " << cacheList.size() << endl;
        cout << "Contents (Most → Least Recent):" << endl;
        
        int index = 0;
        for (const auto& node : cacheList) {
            cout << "[" << index++ << "] Key: " << node.key 
                 << " Value: " << node.value << endl;
        }
        cout << "==============================\n" << endl;
    }
};

// ============== Thread-Safe LRU Cache ==============

template<typename K, typename V>
class ThreadSafeLRUCache {
private:
    LRUCache<K, V> cache;
    mutable mutex mtx;
    
public:
    ThreadSafeLRUCache(int capacity) : cache(capacity) {}
    
    V get(const K& key) {
        lock_guard<mutex> lock(mtx);
        return cache.get(key);
    }
    
    bool contains(const K& key) const {
        lock_guard<mutex> lock(mtx);
        return cache.contains(key);
    }
    
    void put(const K& key, const V& value) {
        lock_guard<mutex> lock(mtx);
        cache.put(key, value);
    }
    
    void remove(const K& key) {
        lock_guard<mutex> lock(mtx);
        cache.remove(key);
    }
    
    void display() const {
        lock_guard<mutex> lock(mtx);
        cache.display();
    }
    
    int size() const {
        lock_guard<mutex> lock(mtx);
        return cache.size();
    }
};

// ============== LRU Cache with Expiration (Advanced) ==============

template<typename K, typename V>
class ExpiringLRUCache {
private:
    struct TimedNode {
        K key;
        V value;
        time_t expirationTime;
        
        TimedNode(const K& k, const V& v, time_t exp) 
            : key(k), value(v), expirationTime(exp) {}
        
        bool isExpired() const {
            return time(nullptr) >= expirationTime;
        }
    };
    
    int capacity;
    int ttlSeconds;
    list<TimedNode> cacheList;
    unordered_map<K, typename list<TimedNode>::iterator> cacheMap;
    
    void removeExpired() {
        time_t now = time(nullptr);
        
        auto it = cacheList.rbegin();
        while (it != cacheList.rend()) {
            if (it->expirationTime <= now) {
                cout << "[EXPIRED] Key: " << it->key << endl;
                cacheMap.erase(it->key);
                // Convert reverse iterator to forward iterator for erase
                it = decltype(it)(cacheList.erase(next(it).base()));
            } else {
                ++it;
            }
        }
    }
    
    void moveToFront(typename list<TimedNode>::iterator it) {
        cacheList.splice(cacheList.begin(), cacheList, it);
    }
    
    void evictLRU() {
        if (cacheList.empty()) return;
        
        K keyToRemove = cacheList.back().key;
        cacheList.pop_back();
        cacheMap.erase(keyToRemove);
        
        cout << "[EVICTED] Key: " << keyToRemove << endl;
    }
    
public:
    ExpiringLRUCache(int cap, int ttl) 
        : capacity(cap), ttlSeconds(ttl) {}
    
    V get(const K& key) {
        removeExpired();
        
        auto it = cacheMap.find(key);
        
        if (it == cacheMap.end()) {
            throw runtime_error("Key not found");
        }
        
        if (it->second->isExpired()) {
            cacheList.erase(it->second);
            cacheMap.erase(it);
            throw runtime_error("Key expired");
        }
        
        moveToFront(it->second);
        return it->second->value;
    }
    
    void put(const K& key, const V& value) {
        removeExpired();
        
        time_t expiration = time(nullptr) + ttlSeconds;
        auto it = cacheMap.find(key);
        
        if (it != cacheMap.end()) {
            it->second->value = value;
            it->second->expirationTime = expiration;
            moveToFront(it->second);
        } else {
            if (cacheList.size() >= capacity) {
                evictLRU();
            }
            
            cacheList.emplace_front(key, value, expiration);
            cacheMap[key] = cacheList.begin();
        }
    }
    
    void display() const {
        cout << "\n========== Expiring LRU Cache ==========" << endl;
        cout << "Capacity: " << capacity << " | TTL: " << ttlSeconds << "s" << endl;
        cout << "Size: " << cacheList.size() << endl;
        
        time_t now = time(nullptr);
        int index = 0;
        for (const auto& node : cacheList) {
            cout << "[" << index++ << "] Key: " << node.key 
                 << " Value: " << node.value 
                 << " Expires in: " << (node.expirationTime - now) << "s" << endl;
        }
        cout << "=======================================\n" << endl;
    }
};

// ============== Usage Statistics Decorator ==============

template<typename K, typename V>
class StatisticalLRUCache {
private:
    LRUCache<K, V> cache;
    int hits;
    int misses;
    
public:
    StatisticalLRUCache(int capacity) : cache(capacity), hits(0), misses(0) {}
    
    V get(const K& key) {
        try {
            V value = cache.get(key);
            hits++;
            return value;
        } catch (const runtime_error&) {
            misses++;
            throw;
        }
    }
    
    void put(const K& key, const V& value) {
        cache.put(key, value);
    }
    
    double getHitRate() const {
        int total = hits + misses;
        return total == 0 ? 0.0 : static_cast<double>(hits) / total;
    }
    
    void displayStatistics() const {
        cout << "\n========== Cache Statistics ==========" << endl;
        cout << "Hits: " << hits << endl;
        cout << "Misses: " << misses << endl;
        cout << "Hit Rate: " << (getHitRate() * 100) << "%" << endl;
        cout << "======================================\n" << endl;
    }
    
    void display() const {
        cache.display();
    }
};

// ============== Demo ==============

void testBasicLRUCache() {
    cout << "\n===== TEST 1: Basic LRU Cache =====\n" << endl;
    
    LRUCache<int, string> cache(3);
    
    cache.put(1, "one");
    cache.put(2, "two");
    cache.put(3, "three");
    cache.display();
    
    // Access key 1 (makes it most recent)
    cout << "Getting key 1: " << cache.get(1) << endl;
    cache.display();
    
    // Add key 4 (should evict key 2, the LRU)
    cache.put(4, "four");
    cache.display();
    
    // Try to access evicted key 2
    try {
        cache.get(2);
    } catch (const runtime_error& e) {
        cout << "[ERROR] " << e.what() << endl;
    }
    
    // Update existing key
    cache.put(1, "ONE");
    cache.display();
}

void testThreadSafeCache() {
    cout << "\n===== TEST 2: Thread-Safe Cache =====\n" << endl;
    
    ThreadSafeLRUCache<string, int> cache(5);
    
    cache.put("apple", 1);
    cache.put("banana", 2);
    cache.put("cherry", 3);
    
    cout << "Contains 'apple': " << (cache.contains("apple") ? "Yes" : "No") << endl;
    cout << "Value of 'banana': " << cache.get("banana") << endl;
    
    cache.display();
}

void testExpiringCache() {
    cout << "\n===== TEST 3: Expiring LRU Cache =====\n" << endl;
    
    ExpiringLRUCache<string, string> cache(3, 5); // 3 capacity, 5 sec TTL
    
    cache.put("session1", "user1");
    cache.put("session2", "user2");
    cache.display();
    
    // Wait for expiration
    cout << "Waiting 6 seconds for expiration..." << endl;
    this_thread::sleep_for(chrono::seconds(6));
    
    try {
        cache.get("session1");
    } catch (const runtime_error& e) {
        cout << "[ERROR] " << e.what() << endl;
    }
    
    cache.display();
}

void testStatisticalCache() {
    cout << "\n===== TEST 4: Statistical Cache =====\n" << endl;
    
    StatisticalLRUCache<int, string> cache(3);
    
    cache.put(1, "one");
    cache.put(2, "two");
    cache.put(3, "three");
    
    // Generate hits and misses
    for (int i = 0; i < 10; i++) {
        try {
            if (i % 3 == 0) {
                cache.get(1);  // Hit
            } else if (i % 3 == 1) {
                cache.get(2);  // Hit
            } else {
                cache.get(99); // Miss
            }
        } catch (const runtime_error&) {
            // Expected for misses
        }
    }
    
    cache.display();
    cache.displayStatistics();
}

int main() {
    testBasicLRUCache();
    testThreadSafeCache();
    testExpiringCache();
    testStatisticalCache();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Data Structure Choice**
- **HashMap**: O(1) key lookup
- **Doubly Linked List**: O(1) insertion/deletion at any position
- **Combined**: O(1) for both get and put operations

### 2. **Order Maintenance**
- Most recent at front (head)
- Least recent at back (tail)
- `splice()` for efficient reordering

### 3. **Eviction Policy**
- Remove from tail (least recently used)
- Called automatically when capacity reached

---

## Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| get(key)  | O(1)           | -                |
| put(key, value) | O(1)     | -                |
| remove(key) | O(1)         | -                |
| Space     | -              | O(capacity)      |

**Why O(1)?**
- HashMap lookup: O(1)
- List operations (with iterator): O(1)
- `splice()` is O(1) as it just updates pointers

---

## Interview Follow-up Questions

### Q1: How to implement LFU (Least Frequently Used) Cache?

**Answer**: Use two data structures:
- HashMap: key → (value, frequency, iterator)
- Map<frequency, list<key>>: frequency → list of keys with that frequency

```cpp
class LFUCache {
private:
    struct Node {
        int value;
        int freq;
    };
    
    unordered_map<int, Node> cache;
    map<int, list<int>> freqMap;  // freq -> list of keys
    int minFreq;
    int capacity;
};
```

### Q2: How to support multiple eviction policies?

**Answer**: Use Strategy Pattern:

```cpp
class EvictionPolicy {
public:
    virtual int selectVictim() = 0;
};

class LRUEviction : public EvictionPolicy {
    // LRU logic
};

class LFUEviction : public EvictionPolicy {
    // LFU logic
};

class Cache {
private:
    EvictionPolicy* policy;
};
```

### Q3: How to make it distributed?

**Answer**:
- Consistent hashing for key distribution
- Redis/Memcached architecture
- Handle cache coherency
- Replication for availability

### Q4: How to handle cache stampede?

**Answer**:
- Use locks per key
- Exponential backoff
- Probabilistic early expiration
- Request coalescing

```cpp
class StampedeProtectedCache {
private:
    unordered_map<K, mutex> keyLocks;
    
public:
    V get(K key) {
        lock_guard<mutex> lock(keyLocks[key]);
        
        if (!cache.contains(key)) {
            V value = loadFromDB(key);
            cache.put(key, value);
            return value;
        }
        return cache.get(key);
    }
};
```

### Q5: How to implement cache warming?

**Answer**:
- Pre-load frequently accessed data at startup
- Use historical access patterns
- Background thread to refresh expiring entries

---

## Real-World Applications

1. **Web Browsers**: Page caching
2. **Databases**: Query result caching
3. **CDNs**: Content caching
4. **Operating Systems**: Page replacement
5. **APIs**: Rate limiting, response caching
6. **Microservices**: Service discovery cache

---

## Variations & Extensions

### Write-Through Cache
```cpp
void put(K key, V value) {
    cache.put(key, value);
    database.write(key, value); // Write immediately
}
```

### Write-Back Cache
```cpp
void put(K key, V value) {
    cache.put(key, value);
    dirtyKeys.insert(key); // Mark as dirty
    // Flush to DB asynchronously
}
```

### Multi-Level Cache
```cpp
class L1Cache : public LRUCache<K, V> { /* Fast, small */ };
class L2Cache : public LRUCache<K, V> { /* Slower, larger */ };

V get(K key) {
    if (L1.contains(key)) return L1.get(key);
    if (L2.contains(key)) {
        V value = L2.get(key);
        L1.put(key, value); // Promote to L1
        return value;
    }
    // Load from database
}
```

---

## Compilation & Execution

```bash
g++ -std=c++17 -pthread lru_cache.cpp -o lru_cache
./lru_cache
```

---

## Sample Output

```
===== TEST 1: Basic LRU Cache =====

[ADDED] Key: 1 Value: one
[ADDED] Key: 2 Value: two
[ADDED] Key: 3 Value: three

========== LRU Cache ==========
Capacity: 3 | Size: 3
Contents (Most → Least Recent):
[0] Key: 3 Value: three
[1] Key: 2 Value: two
[2] Key: 1 Value: one
==============================

Getting key 1: one

========== LRU Cache ==========
Capacity: 3 | Size: 3
Contents (Most → Least Recent):
[0] Key: 1 Value: one
[1] Key: 3 Value: three
[2] Key: 2 Value: two
==============================

[EVICTED] Key: 2
[ADDED] Key: 4 Value: four

========== LRU Cache ==========
Capacity: 3 | Size: 3
Contents (Most → Least Recent):
[0] Key: 4 Value: four
[1] Key: 1 Value: one
[2] Key: 3 Value: three
==============================

[ERROR] Key not found

[UPDATED] Key: 1 Value: ONE

========== LRU Cache ==========
Capacity: 3 | Size: 3
Contents (Most → Least Recent):
[0] Key: 1 Value: ONE
[1] Key: 4 Value: four
[2] Key: 3 Value: three
==============================
```

---

**This is one of the most frequently asked LLD problems! Master this thoroughly!** 🚀

