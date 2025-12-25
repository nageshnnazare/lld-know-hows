# Problem 5: Notification System

**Difficulty**: Hard  
**Time to Solve**: 70-90 minutes  
**Companies**: Amazon, Google, Facebook, Airbnb

## Problem Statement

Design a scalable notification system that supports:
1. Multiple notification channels (Email, SMS, Push, In-App)
2. User preferences and opt-out
3. Priority-based delivery
4. Rate limiting
5. Notification templates
6. Retry mechanism with exponential backoff

---

## Class Diagram

```
┌────────────────────────┐
│  NotificationSystem    │
├────────────────────────┤
│ - users                │
│ - templates            │
│ - channels             │
│ - queue                │
│ - rateLimiter          │
├────────────────────────┤
│ + sendNotification()   │
│ + scheduleNotification()│
│ + setPreferences()     │
│ + processQueue()       │
└──────┬─────────────────┘
       │
   ┌───┴────┬─────────┬───────────┬──────────┐
   ▼        ▼         ▼           ▼          ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐
│  User  │ │  Notif   │ │ Channel  │ │ RateLimit  │
├────────┤ ├──────────┤ ├──────────┤ ├────────────┤
│- id    │ │- type    │ │- send()  │ │- check()   │
│- prefs │ │- priority│ │          │ │- tokens    │
└────────┘ └──────────┘ └──────────┘ └────────────┘
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
#include <thread>
#include <mutex>
#include <chrono>

using namespace std;

// ============== Enums ==============

enum class NotificationType { EMAIL, SMS, PUSH, IN_APP };
enum class Priority { LOW, MEDIUM, HIGH, URGENT };
enum class NotificationStatus { PENDING, SENT, FAILED, RETRYING };

// ============== User Preferences ==============

class NotificationPreferences {
private:
    set<NotificationType> enabledChannels;
    map<NotificationType, pair<int, int>> quietHours; // start hour, end hour
    bool doNotDisturb;
    
public:
    NotificationPreferences() : doNotDisturb(false) {
        // Enable all channels by default
        enabledChannels = {NotificationType::EMAIL, NotificationType::SMS,
                          NotificationType::PUSH, NotificationType::IN_APP};
    }
    
    bool isChannelEnabled(NotificationType type) const {
        return enabledChannels.find(type) != enabledChannels.end();
    }
    
    void enableChannel(NotificationType type) {
        enabledChannels.insert(type);
    }
    
    void disableChannel(NotificationType type) {
        enabledChannels.erase(type);
    }
    
    void setDoNotDisturb(bool status) {
        doNotDisturb = status;
    }
    
    bool isInQuietHours(NotificationType type) const {
        if (quietHours.find(type) == quietHours.end()) return false;
        
        time_t now = time(nullptr);
        struct tm* timeinfo = localtime(&now);
        int currentHour = timeinfo->tm_hour;
        
        auto [start, end] = quietHours.at(type);
        return currentHour >= start && currentHour < end;
    }
    
    void setQuietHours(NotificationType type, int startHour, int endHour) {
        quietHours[type] = {startHour, endHour};
    }
    
    bool canReceive(NotificationType type, Priority priority) const {
        if (doNotDisturb && priority != Priority::URGENT) {
            return false;
        }
        
        if (!isChannelEnabled(type)) {
            return false;
        }
        
        if (isInQuietHours(type) && priority != Priority::URGENT) {
            return false;
        }
        
        return true;
    }
};

// ============== User ==============

class User {
private:
    string userId;
    string name;
    string email;
    string phone;
    string deviceToken; // For push notifications
    NotificationPreferences preferences;
    
public:
    User(const string& id, const string& n, const string& e, const string& p)
        : userId(id), name(n), email(e), phone(p) {}
    
    string getUserId() const { return userId; }
    string getName() const { return name; }
    string getEmail() const { return email; }
    string getPhone() const { return phone; }
    string getDeviceToken() const { return deviceToken; }
    
    void setDeviceToken(const string& token) { deviceToken = token; }
    
    NotificationPreferences& getPreferences() { return preferences; }
    const NotificationPreferences& getPreferences() const { return preferences; }
};

// ============== Notification Template ==============

class NotificationTemplate {
private:
    string templateId;
    string name;
    NotificationType type;
    string subject;
    string body;
    
public:
    NotificationTemplate(const string& id, const string& n, NotificationType t,
                        const string& subj, const string& b)
        : templateId(id), name(n), type(t), subject(subj), body(b) {}
    
    string getId() const { return templateId; }
    NotificationType getType() const { return type; }
    
    string render(const map<string, string>& variables) const {
        string result = body;
        
        for (const auto& [key, value] : variables) {
            string placeholder = "{{" + key + "}}";
            size_t pos = 0;
            
            while ((pos = result.find(placeholder, pos)) != string::npos) {
                result.replace(pos, placeholder.length(), value);
                pos += value.length();
            }
        }
        
        return result;
    }
    
    string getSubject() const { return subject; }
};

// ============== Notification ==============

class Notification {
private:
    string notificationId;
    string userId;
    NotificationType type;
    Priority priority;
    string subject;
    string message;
    NotificationStatus status;
    time_t timestamp;
    time_t scheduledTime;
    int retryCount;
    static int notificationCounter;
    
public:
    Notification(const string& uid, NotificationType t, Priority p,
                const string& subj, const string& msg, time_t scheduled = 0)
        : userId(uid), type(t), priority(p), subject(subj), message(msg),
          status(NotificationStatus::PENDING), timestamp(time(nullptr)),
          scheduledTime(scheduled == 0 ? time(nullptr) : scheduled),
          retryCount(0) {
        notificationId = "NOTIF" + to_string(++notificationCounter);
    }
    
    string getId() const { return notificationId; }
    string getUserId() const { return userId; }
    NotificationType getType() const { return type; }
    Priority getPriority() const { return priority; }
    string getSubject() const { return subject; }
    string getMessage() const { return message; }
    NotificationStatus getStatus() const { return status; }
    time_t getScheduledTime() const { return scheduledTime; }
    int getRetryCount() const { return retryCount; }
    
    void setStatus(NotificationStatus s) { status = s; }
    void incrementRetry() { retryCount++; }
    
    bool isReady() const {
        return time(nullptr) >= scheduledTime;
    }
    
    int getPriorityValue() const {
        switch (priority) {
            case Priority::URGENT: return 4;
            case Priority::HIGH: return 3;
            case Priority::MEDIUM: return 2;
            case Priority::LOW: return 1;
        }
        return 0;
    }
    
    void display() const {
        cout << "\n========== NOTIFICATION ==========" << endl;
        cout << "ID: " << notificationId << endl;
        cout << "Type: " << (int)type << " | Priority: " << (int)priority << endl;
        cout << "Subject: " << subject << endl;
        cout << "Message: " << message << endl;
        cout << "Status: " << (int)status << endl;
        cout << "==================================\n" << endl;
    }
};

int Notification::notificationCounter = 0;

// ============== Notification Channel ==============

class NotificationChannel {
public:
    virtual ~NotificationChannel() = default;
    
    virtual bool send(User* user, Notification* notification) = 0;
    virtual string getChannelName() const = 0;
};

class EmailChannel : public NotificationChannel {
public:
    bool send(User* user, Notification* notification) override {
        cout << "📧 Sending email to " << user->getEmail() << endl;
        cout << "   Subject: " << notification->getSubject() << endl;
        cout << "   Body: " << notification->getMessage() << endl;
        
        // Simulate sending (95% success rate)
        return (rand() % 100) < 95;
    }
    
    string getChannelName() const override { return "Email"; }
};

class SMSChannel : public NotificationChannel {
public:
    bool send(User* user, Notification* notification) override {
        cout << "📱 Sending SMS to " << user->getPhone() << endl;
        cout << "   Message: " << notification->getMessage() << endl;
        
        // Simulate sending (90% success rate)
        return (rand() % 100) < 90;
    }
    
    string getChannelName() const override { return "SMS"; }
};

class PushChannel : public NotificationChannel {
public:
    bool send(User* user, Notification* notification) override {
        cout << "🔔 Sending push notification to device " << user->getDeviceToken() << endl;
        cout << "   Title: " << notification->getSubject() << endl;
        cout << "   Body: " << notification->getMessage() << endl;
        
        // Simulate sending (92% success rate)
        return (rand() % 100) < 92;
    }
    
    string getChannelName() const override { return "Push"; }
};

class InAppChannel : public NotificationChannel {
public:
    bool send(User* user, Notification* notification) override {
        cout << "💬 Creating in-app notification for user " << user->getUserId() << endl;
        cout << "   Message: " << notification->getMessage() << endl;
        
        // In-app notifications are always successful
        return true;
    }
    
    string getChannelName() const override { return "In-App"; }
};

// ============== Rate Limiter ==============

class RateLimiter {
private:
    map<pair<string, NotificationType>, queue<time_t>> userTimestamps;
    int maxPerMinute;
    mutex rateMutex;
    
public:
    RateLimiter(int maxRate = 10) : maxPerMinute(maxRate) {}
    
    bool canSend(const string& userId, NotificationType type) {
        lock_guard<mutex> lock(rateMutex);
        
        time_t now = time(nullptr);
        auto key = make_pair(userId, type);
        auto& timestamps = userTimestamps[key];
        
        // Remove timestamps older than 1 minute
        while (!timestamps.empty() && now - timestamps.front() > 60) {
            timestamps.pop();
        }
        
        if (timestamps.size() >= maxPerMinute) {
            return false;
        }
        
        timestamps.push(now);
        return true;
    }
};

// ============== Notification Queue ==============

struct NotificationComparator {
    bool operator()(Notification* a, Notification* b) const {
        // Higher priority first
        if (a->getPriorityValue() != b->getPriorityValue()) {
            return a->getPriorityValue() < b->getPriorityValue();
        }
        // Earlier scheduled time first
        return a->getScheduledTime() > b->getScheduledTime();
    }
};

// ============== Notification System ==============

class NotificationSystem {
private:
    map<string, unique_ptr<User>> users;
    map<string, unique_ptr<NotificationTemplate>> templates;
    map<NotificationType, unique_ptr<NotificationChannel>> channels;
    priority_queue<Notification*, vector<Notification*>, NotificationComparator> notificationQueue;
    vector<unique_ptr<Notification>> allNotifications;
    RateLimiter rateLimiter;
    mutex queueMutex;
    bool running;
    
public:
    NotificationSystem() : running(false) {
        // Initialize channels
        channels[NotificationType::EMAIL] = make_unique<EmailChannel>();
        channels[NotificationType::SMS] = make_unique<SMSChannel>();
        channels[NotificationType::PUSH] = make_unique<PushChannel>();
        channels[NotificationType::IN_APP] = make_unique<InAppChannel>();
    }
    
    User* registerUser(const string& id, const string& name,
                      const string& email, const string& phone) {
        auto user = make_unique<User>(id, name, email, phone);
        User* ptr = user.get();
        users[id] = move(user);
        
        cout << "✓ User registered: " << name << endl;
        return ptr;
    }
    
    NotificationTemplate* createTemplate(const string& id, const string& name,
                                        NotificationType type, const string& subject,
                                        const string& body) {
        auto templ = make_unique<NotificationTemplate>(id, name, type, subject, body);
        NotificationTemplate* ptr = templ.get();
        templates[id] = move(templ);
        
        cout << "✓ Template created: " << name << endl;
        return ptr;
    }
    
    Notification* sendNotification(const string& userId, NotificationType type,
                                  Priority priority, const string& subject,
                                  const string& message, time_t scheduledTime = 0) {
        User* user = getUser(userId);
        if (!user) {
            cout << "User not found!" << endl;
            return nullptr;
        }
        
        // Check user preferences
        if (!user->getPreferences().canReceive(type, priority)) {
            cout << "User has disabled this notification type or in quiet hours" << endl;
            return nullptr;
        }
        
        // Create notification
        auto notification = make_unique<Notification>(userId, type, priority,
                                                      subject, message, scheduledTime);
        Notification* ptr = notification.get();
        
        // Add to queue
        {
            lock_guard<mutex> lock(queueMutex);
            notificationQueue.push(ptr);
            allNotifications.push_back(move(notification));
        }
        
        cout << "✓ Notification queued: " << ptr->getId() << endl;
        return ptr;
    }
    
    Notification* sendFromTemplate(const string& userId, const string& templateId,
                                  const map<string, string>& variables,
                                  Priority priority = Priority::MEDIUM) {
        
        NotificationTemplate* templ = getTemplate(templateId);
        if (!templ) {
            cout << "Template not found!" << endl;
            return nullptr;
        }
        
        string message = templ->render(variables);
        return sendNotification(userId, templ->getType(), priority,
                               templ->getSubject(), message);
    }
    
    void processQueue() {
        cout << "\n=== Processing Notification Queue ===" << endl;
        
        vector<Notification*> retryQueue;
        
        while (true) {
            Notification* notification = nullptr;
            
            {
                lock_guard<mutex> lock(queueMutex);
                if (notificationQueue.empty()) break;
                
                notification = notificationQueue.top();
                notificationQueue.pop();
            }
            
            if (!notification->isReady()) {
                retryQueue.push_back(notification);
                continue;
            }
            
            User* user = getUser(notification->getUserId());
            if (!user) continue;
            
            NotificationType type = notification->getType();
            
            // Check rate limit
            if (!rateLimiter.canSend(user->getUserId(), type)) {
                cout << "⚠ Rate limit exceeded for user " << user->getUserId() << endl;
                retryQueue.push_back(notification);
                continue;
            }
            
            // Send notification
            NotificationChannel* channel = channels[type].get();
            
            cout << "\n--- Sending Notification ---" << endl;
            notification->display();
            
            if (channel->send(user, notification)) {
                notification->setStatus(NotificationStatus::SENT);
                cout << "✓ Sent successfully via " << channel->getChannelName() << endl;
            } else {
                notification->incrementRetry();
                
                if (notification->getRetryCount() < 3) {
                    notification->setStatus(NotificationStatus::RETRYING);
                    retryQueue.push_back(notification);
                    cout << "⚠ Failed, will retry (attempt " << notification->getRetryCount() << ")" << endl;
                } else {
                    notification->setStatus(NotificationStatus::FAILED);
                    cout << "❌ Failed after 3 attempts" << endl;
                }
            }
        }
        
        // Re-add retry notifications
        {
            lock_guard<mutex> lock(queueMutex);
            for (Notification* notif : retryQueue) {
                notificationQueue.push(notif);
            }
        }
    }
    
    User* getUser(const string& userId) {
        auto it = users.find(userId);
        return (it != users.end()) ? it->second.get() : nullptr;
    }
    
    NotificationTemplate* getTemplate(const string& templateId) {
        auto it = templates.find(templateId);
        return (it != templates.end()) ? it->second.get() : nullptr;
    }
    
    void displayStatistics() const {
        cout << "\n========== NOTIFICATION STATISTICS ==========" << endl;
        
        int sent = 0, failed = 0, pending = 0;
        
        for (const auto& notif : allNotifications) {
            switch (notif->getStatus()) {
                case NotificationStatus::SENT:
                    sent++;
                    break;
                case NotificationStatus::FAILED:
                    failed++;
                    break;
                case NotificationStatus::PENDING:
                case NotificationStatus::RETRYING:
                    pending++;
                    break;
            }
        }
        
        cout << "Total: " << allNotifications.size() << endl;
        cout << "Sent: " << sent << " | Failed: " << failed << " | Pending: " << pending << endl;
        cout << "Success Rate: " << (allNotifications.empty() ? 0 : (sent * 100.0 / allNotifications.size()))
             << "%" << endl;
        cout << "============================================\n" << endl;
    }
};

// ============== Demo ==============

int main() {
    srand(time(nullptr));
    
    NotificationSystem system;
    
    cout << "========== Notification System Demo ==========\n" << endl;
    
    // Register users
    cout << "=== User Registration ===" << endl;
    User* alice = system.registerUser("U001", "Alice", "alice@email.com", "+1234567890");
    User* bob = system.registerUser("U002", "Bob", "bob@email.com", "+0987654321");
    
    alice->setDeviceToken("DEVICE_TOKEN_123");
    bob->setDeviceToken("DEVICE_TOKEN_456");
    
    cout << endl;
    
    // Set preferences
    cout << "=== Setting Preferences ===" << endl;
    bob->getPreferences().disableChannel(NotificationType::SMS);
    cout << "✓ Bob disabled SMS notifications" << endl;
    
    // Create templates
    cout << "\n=== Creating Templates ===" << endl;
    system.createTemplate("T001", "Welcome Email", NotificationType::EMAIL,
                         "Welcome to our platform!",
                         "Hello {{name}}, welcome to our amazing platform! We're glad to have you.");
    
    system.createTemplate("T002", "Order Confirmation", NotificationType::PUSH,
                         "Order Confirmed",
                         "Your order #{{order_id}} has been confirmed. Total: ${{amount}}");
    
    // Send notifications
    cout << "\n=== Sending Notifications ===" << endl;
    
    // Welcome email
    system.sendFromTemplate("U001", "T001", {{"name", "Alice"}}, Priority::MEDIUM);
    
    // Order confirmation
    system.sendFromTemplate("U002", "T002", {{"order_id", "12345"}, {"amount", "99.99"}},
                           Priority::HIGH);
    
    // Direct notification
    system.sendNotification("U001", NotificationType::SMS, Priority::URGENT,
                           "Security Alert", "New login detected from unknown device");
    
    // SMS to Bob (should be blocked by preferences)
    system.sendNotification("U002", NotificationType::SMS, Priority::MEDIUM,
                           "Promotion", "50% off on all items!");
    
    // Process queue
    system.processQueue();
    
    // Statistics
    system.displayStatistics();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Channel Abstraction**
- Base `NotificationChannel` interface
- Independent channel implementations
- Easy to add new channels

### 2. **Priority Queue**
- Priority-based processing
- Scheduled notifications
- URGENT messages bypass restrictions

### 3. **Rate Limiting**
- Per-user, per-channel limits
- Sliding window algorithm
- Prevents spam

---

## Follow-up Questions

**Q1: How to implement exponential backoff?**
```cpp
int getBackoffDelay(int retryCount) {
    return min(60, (int)pow(2, retryCount)); // Max 60 seconds
}
```

**Q2: How to support batching?**
```cpp
class BatchProcessor {
    vector<Notification*> batch;
    
    void addToBatch(Notification* n) {
        batch.push_back(n);
        if (batch.size() >= 100) sendBatch();
    }
};
```

**Q3: How to track delivery status?**
```cpp
class DeliveryTracker {
    map<string, DeliveryStatus> status;
    
    void updateStatus(string notifId, DeliveryStatus s);
    void handleWebhook(string provider, string payload);
};
```

---

## Compilation

```bash
g++ -std=c++17 notification_system.cpp -o notification -pthread
./notification
```

---

**Next**: `hard/06-meeting-scheduler.md`

