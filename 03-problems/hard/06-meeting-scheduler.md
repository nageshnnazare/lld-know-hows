# Problem 6: Meeting Scheduler

**Difficulty**: Hard  
**Time to Solve**: 70-90 minutes  
**Companies**: Google Calendar, Microsoft Outlook, Calendly

## Problem Statement

Design a meeting scheduler system that supports:
1. Create/Update/Cancel meetings
2. Find available time slots
3. Handle recurring meetings
4. Room booking integration
5. Conflict detection
6. Send meeting invites
7. Handle time zones

---

## Class Diagram

```
┌────────────────────────┐
│  MeetingScheduler      │
├────────────────────────┤
│ - users                │
│ - meetings             │
│ - rooms                │
│ - calendar             │
├────────────────────────┤
│ + scheduleMeeting()    │
│ + findAvailableSlots() │
│ + checkConflicts()     │
│ + bookRoom()           │
│ + sendInvites()        │
└──────┬─────────────────┘
       │
   ┌───┴────┬────────┬──────────┬──────────┐
   ▼        ▼        ▼          ▼          ▼
┌────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐
│  User  │ │ Meeting  │ │   Room   │ │ TimeSlot  │
├────────┤ ├──────────┤ ├──────────┤ ├───────────┤
│- cal   │ │- time    │ │- capacity│ │- start    │
│- tz    │ │- attendees││- location│ │- end      │
└────────┘ └──────────┘ └──────────┘ └───────────┘
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
#include <algorithm>
#include <ctime>
#include <iomanip>
#include <sstream>

using namespace std;

// ============== Time Slot ==============

class TimeSlot {
private:
    time_t startTime;
    time_t endTime;
    
public:
    TimeSlot(time_t start, time_t end) : startTime(start), endTime(end) {}
    
    time_t getStartTime() const { return startTime; }
    time_t getEndTime() const { return endTime; }
    
    bool overlaps(const TimeSlot& other) const {
        return !(endTime <= other.startTime || startTime >= other.endTime);
    }
    
    bool contains(time_t t) const {
        return t >= startTime && t < endTime;
    }
    
    int getDurationMinutes() const {
        return (endTime - startTime) / 60;
    }
    
    string toString() const {
        char startStr[20], endStr[20];
        struct tm* startInfo = localtime(&startTime);
        struct tm* endInfo = localtime(&endTime);
        
        strftime(startStr, sizeof(startStr), "%Y-%m-%d %H:%M", startInfo);
        strftime(endStr, sizeof(endStr), "%H:%M", endInfo);
        
        return string(startStr) + " - " + endStr;
    }
    
    bool operator<(const TimeSlot& other) const {
        return startTime < other.startTime;
    }
};

// ============== Room ==============

class Room {
private:
    string roomId;
    string name;
    int capacity;
    string location;
    vector<string> facilities;
    map<time_t, TimeSlot> bookings; // startTime -> TimeSlot
    
public:
    Room(const string& id, const string& n, int cap, const string& loc)
        : roomId(id), name(n), capacity(cap), location(loc) {}
    
    string getId() const { return roomId; }
    string getName() const { return name; }
    int getCapacity() const { return capacity; }
    string getLocation() const { return location; }
    
    void addFacility(const string& facility) {
        facilities.push_back(facility);
    }
    
    bool isAvailable(const TimeSlot& slot) const {
        for (const auto& [start, booking] : bookings) {
            if (booking.overlaps(slot)) {
                return false;
            }
        }
        return true;
    }
    
    bool book(const TimeSlot& slot) {
        if (!isAvailable(slot)) {
            return false;
        }
        
        bookings[slot.getStartTime()] = slot;
        return true;
    }
    
    void cancelBooking(time_t startTime) {
        bookings.erase(startTime);
    }
    
    void displayInfo() const {
        cout << name << " (Capacity: " << capacity << ")" << endl;
        cout << "Location: " << location << endl;
        if (!facilities.empty()) {
            cout << "Facilities: ";
            for (size_t i = 0; i < facilities.size(); i++) {
                cout << facilities[i];
                if (i < facilities.size() - 1) cout << ", ";
            }
            cout << endl;
        }
    }
};

// ============== User ==============

class User {
private:
    string userId;
    string name;
    string email;
    string timezone; // Simplified as string
    map<time_t, string> calendar; // startTime -> meetingId
    
public:
    User(const string& id, const string& n, const string& e, const string& tz = "UTC")
        : userId(id), name(n), email(e), timezone(tz) {}
    
    string getUserId() const { return userId; }
    string getName() const { return name; }
    string getEmail() const { return email; }
    string getTimezone() const { return timezone; }
    
    bool isAvailable(const TimeSlot& slot) const {
        for (const auto& [start, meetingId] : calendar) {
            // Simplified: check if start time falls in slot
            // In real system, need to check full meeting duration
            if (slot.contains(start)) {
                return false;
            }
        }
        return true;
    }
    
    void addToCalendar(const string& meetingId, time_t startTime) {
        calendar[startTime] = meetingId;
    }
    
    void removeFromCalendar(time_t startTime) {
        calendar.erase(startTime);
    }
    
    vector<TimeSlot> getAvailableSlots(time_t dayStart, time_t dayEnd,
                                       int durationMinutes) const {
        vector<TimeSlot> available;
        
        // Generate all possible slots for the day (every 30 minutes)
        time_t current = dayStart;
        while (current + durationMinutes * 60 <= dayEnd) {
            TimeSlot slot(current, current + durationMinutes * 60);
            
            if (isAvailable(slot)) {
                available.push_back(slot);
            }
            
            current += 30 * 60; // Move by 30 minutes
        }
        
        return available;
    }
};

// ============== Meeting ==============

enum class MeetingStatus { SCHEDULED, CANCELLED, COMPLETED };
enum class RecurrenceType { NONE, DAILY, WEEKLY, MONTHLY };

class Meeting {
private:
    string meetingId;
    string title;
    string description;
    User* organizer;
    vector<User*> attendees;
    TimeSlot timeSlot;
    Room* room;
    MeetingStatus status;
    RecurrenceType recurrence;
    time_t recurrenceEndDate;
    static int meetingCounter;
    
public:
    Meeting(const string& t, const string& desc, User* org, const TimeSlot& slot,
           RecurrenceType rec = RecurrenceType::NONE)
        : title(t), description(desc), organizer(org), timeSlot(slot),
          room(nullptr), status(MeetingStatus::SCHEDULED), recurrence(rec),
          recurrenceEndDate(0) {
        
        meetingId = "MTG" + to_string(++meetingCounter);
    }
    
    string getId() const { return meetingId; }
    string getTitle() const { return title; }
    User* getOrganizer() const { return organizer; }
    const vector<User*>& getAttendees() const { return attendees; }
    TimeSlot getTimeSlot() const { return timeSlot; }
    Room* getRoom() const { return room; }
    MeetingStatus getStatus() const { return status; }
    
    void addAttendee(User* user) {
        attendees.push_back(user);
    }
    
    void removeAttendee(User* user) {
        attendees.erase(remove(attendees.begin(), attendees.end(), user), attendees.end());
    }
    
    void setRoom(Room* r) {
        room = r;
    }
    
    void cancel() {
        status = MeetingStatus::CANCELLED;
        
        // Free up room
        if (room) {
            room->cancelBooking(timeSlot.getStartTime());
        }
        
        // Remove from attendees' calendars
        for (User* attendee : attendees) {
            attendee->removeFromCalendar(timeSlot.getStartTime());
        }
        
        organizer->removeFromCalendar(timeSlot.getStartTime());
    }
    
    void updateTime(const TimeSlot& newSlot) {
        // Remove old booking
        if (room) {
            room->cancelBooking(timeSlot.getStartTime());
        }
        
        // Update time
        time_t oldStart = timeSlot.getStartTime();
        timeSlot = newSlot;
        
        // Update in attendees' calendars
        for (User* attendee : attendees) {
            attendee->removeFromCalendar(oldStart);
            attendee->addToCalendar(meetingId, newSlot.getStartTime());
        }
        
        organizer->removeFromCalendar(oldStart);
        organizer->addToCalendar(meetingId, newSlot.getStartTime());
        
        // Rebook room
        if (room) {
            room->book(newSlot);
        }
    }
    
    void display() const {
        cout << "\n========== MEETING ==========" << endl;
        cout << "ID: " << meetingId << endl;
        cout << "Title: " << title << endl;
        cout << "Organizer: " << organizer->getName() << endl;
        cout << "Time: " << timeSlot.toString() << endl;
        cout << "Duration: " << timeSlot.getDurationMinutes() << " minutes" << endl;
        
        if (room) {
            cout << "Room: " << room->getName() << endl;
        }
        
        cout << "Attendees (" << attendees.size() << "):" << endl;
        for (User* attendee : attendees) {
            cout << "  - " << attendee->getName() << " <" << attendee->getEmail() << ">" << endl;
        }
        
        cout << "Status: " << (int)status << endl;
        cout << "============================\n" << endl;
    }
};

int Meeting::meetingCounter = 0;

// ============== Meeting Scheduler ==============

class MeetingScheduler {
private:
    map<string, unique_ptr<User>> users;
    map<string, unique_ptr<Meeting>> meetings;
    map<string, unique_ptr<Room>> rooms;
    
    bool checkConflicts(User* user, const TimeSlot& slot) {
        return user->isAvailable(slot);
    }
    
public:
    User* registerUser(const string& id, const string& name,
                      const string& email, const string& timezone = "UTC") {
        auto user = make_unique<User>(id, name, email, timezone);
        User* ptr = user.get();
        users[id] = move(user);
        
        cout << "✓ User registered: " << name << endl;
        return ptr;
    }
    
    Room* addRoom(const string& id, const string& name, int capacity,
                 const string& location) {
        auto room = make_unique<Room>(id, name, capacity, location);
        Room* ptr = room.get();
        rooms[id] = move(room);
        
        cout << "✓ Room added: " << name << endl;
        return ptr;
    }
    
    Meeting* scheduleMeeting(User* organizer, const string& title,
                            const string& description, const TimeSlot& slot,
                            const vector<User*>& attendees,
                            const string& roomId = "") {
        
        // Check organizer availability
        if (!checkConflicts(organizer, slot)) {
            cout << "Organizer has a conflict at this time!" << endl;
            return nullptr;
        }
        
        // Check all attendees availability
        for (User* attendee : attendees) {
            if (!checkConflicts(attendee, slot)) {
                cout << "Attendee " << attendee->getName() << " has a conflict!" << endl;
                return nullptr;
            }
        }
        
        // Book room if requested
        Room* room = nullptr;
        if (!roomId.empty()) {
            room = getRoom(roomId);
            if (!room) {
                cout << "Room not found!" << endl;
                return nullptr;
            }
            
            if (!room->isAvailable(slot)) {
                cout << "Room is not available at this time!" << endl;
                return nullptr;
            }
            
            if (room->getCapacity() < attendees.size() + 1) {
                cout << "Room capacity insufficient!" << endl;
                return nullptr;
            }
            
            room->book(slot);
        }
        
        // Create meeting
        auto meeting = make_unique<Meeting>(title, description, organizer, slot);
        Meeting* meetingPtr = meeting.get();
        
        if (room) {
            meetingPtr->setRoom(room);
        }
        
        // Add attendees
        for (User* attendee : attendees) {
            meetingPtr->addAttendee(attendee);
            attendee->addToCalendar(meetingPtr->getId(), slot.getStartTime());
        }
        
        // Add to organizer's calendar
        organizer->addToCalendar(meetingPtr->getId(), slot.getStartTime());
        
        string meetingId = meetingPtr->getId();
        meetings[meetingId] = move(meeting);
        
        cout << "✓ Meeting scheduled: " << title << " (" << meetingId << ")" << endl;
        sendInvites(meetingPtr);
        
        return meetingPtr;
    }
    
    vector<TimeSlot> findCommonAvailableSlots(const vector<User*>& users,
                                              time_t dayStart, time_t dayEnd,
                                              int durationMinutes) {
        
        if (users.empty()) return {};
        
        // Get available slots for first user
        vector<TimeSlot> common = users[0]->getAvailableSlots(dayStart, dayEnd, durationMinutes);
        
        // Intersect with other users' available slots
        for (size_t i = 1; i < users.size(); i++) {
            vector<TimeSlot> userSlots = users[i]->getAvailableSlots(dayStart, dayEnd, durationMinutes);
            
            vector<TimeSlot> intersection;
            set_intersection(common.begin(), common.end(),
                           userSlots.begin(), userSlots.end(),
                           back_inserter(intersection));
            
            common = intersection;
        }
        
        return common;
    }
    
    vector<Room*> findAvailableRooms(const TimeSlot& slot, int minCapacity) {
        vector<Room*> available;
        
        for (const auto& [id, room] : rooms) {
            if (room->getCapacity() >= minCapacity && room->isAvailable(slot)) {
                available.push_back(room.get());
            }
        }
        
        return available;
    }
    
    bool cancelMeeting(const string& meetingId) {
        Meeting* meeting = getMeeting(meetingId);
        
        if (!meeting) {
            cout << "Meeting not found!" << endl;
            return false;
        }
        
        meeting->cancel();
        cout << "✓ Meeting cancelled: " << meetingId << endl;
        
        return true;
    }
    
    bool rescheduleMeeting(const string& meetingId, const TimeSlot& newSlot) {
        Meeting* meeting = getMeeting(meetingId);
        
        if (!meeting) {
            cout << "Meeting not found!" << endl;
            return false;
        }
        
        // Check availability of all attendees
        User* organizer = meeting->getOrganizer();
        if (!organizer->isAvailable(newSlot)) {
            cout << "Organizer not available at new time!" << endl;
            return false;
        }
        
        for (User* attendee : meeting->getAttendees()) {
            if (!attendee->isAvailable(newSlot)) {
                cout << "Attendee " << attendee->getName() << " not available!" << endl;
                return false;
            }
        }
        
        // Check room availability
        if (meeting->getRoom() && !meeting->getRoom()->isAvailable(newSlot)) {
            cout << "Room not available at new time!" << endl;
            return false;
        }
        
        meeting->updateTime(newSlot);
        cout << "✓ Meeting rescheduled to " << newSlot.toString() << endl;
        
        return true;
    }
    
    void sendInvites(Meeting* meeting) {
        cout << "\n=== Sending Meeting Invites ===" << endl;
        
        for (User* attendee : meeting->getAttendees()) {
            cout << "📧 Invite sent to " << attendee->getName()
                 << " <" << attendee->getEmail() << ">" << endl;
        }
        
        cout << endl;
    }
    
    User* getUser(const string& userId) {
        auto it = users.find(userId);
        return (it != users.end()) ? it->second.get() : nullptr;
    }
    
    Meeting* getMeeting(const string& meetingId) {
        auto it = meetings.find(meetingId);
        return (it != meetings.end()) ? it->second.get() : nullptr;
    }
    
    Room* getRoom(const string& roomId) {
        auto it = rooms.find(roomId);
        return (it != rooms.end()) ? it->second.get() : nullptr;
    }
    
    void displayAllRooms() const {
        cout << "\n========== AVAILABLE ROOMS ==========" << endl;
        for (const auto& [id, room] : rooms) {
            cout << "[" << id << "] ";
            room->displayInfo();
            cout << "---" << endl;
        }
        cout << "=====================================\n" << endl;
    }
};

// ============== Helper Functions ==============

time_t createTime(int year, int month, int day, int hour, int minute) {
    struct tm timeinfo = {};
    timeinfo.tm_year = year - 1900;
    timeinfo.tm_mon = month - 1;
    timeinfo.tm_mday = day;
    timeinfo.tm_hour = hour;
    timeinfo.tm_min = minute;
    return mktime(&timeinfo);
}

// ============== Demo ==============

int main() {
    MeetingScheduler scheduler;
    
    cout << "========== Meeting Scheduler Demo ==========\n" << endl;
    
    // Register users
    cout << "=== User Registration ===" << endl;
    User* alice = scheduler.registerUser("U001", "Alice", "alice@company.com", "UTC");
    User* bob = scheduler.registerUser("U002", "Bob", "bob@company.com", "UTC");
    User* charlie = scheduler.registerUser("U003", "Charlie", "charlie@company.com", "UTC");
    
    cout << endl;
    
    // Add rooms
    cout << "=== Adding Meeting Rooms ===" << endl;
    Room* room1 = scheduler.addRoom("R001", "Conference Room A", 10, "Building 1, Floor 2");
    Room* room2 = scheduler.addRoom("R002", "Conference Room B", 6, "Building 1, Floor 3");
    
    room1->addFacility("Projector");
    room1->addFacility("Whiteboard");
    room2->addFacility("Video Conference");
    
    scheduler.displayAllRooms();
    
    // Schedule meetings
    cout << "=== Scheduling Meetings ===" << endl;
    
    // Meeting 1: Team Standup
    time_t start1 = createTime(2024, 12, 26, 10, 0);
    time_t end1 = createTime(2024, 12, 26, 10, 30);
    TimeSlot slot1(start1, end1);
    
    Meeting* meeting1 = scheduler.scheduleMeeting(
        alice,
        "Team Standup",
        "Daily team sync",
        slot1,
        {bob, charlie},
        "R002"
    );
    
    if (meeting1) {
        meeting1->display();
    }
    
    // Meeting 2: Project Review (conflict with same room)
    time_t start2 = createTime(2024, 12, 26, 10, 15);
    time_t end2 = createTime(2024, 12, 26, 11, 0);
    TimeSlot slot2(start2, end2);
    
    cout << "\n=== Attempting to Schedule Conflicting Meeting ===" << endl;
    Meeting* meeting2 = scheduler.scheduleMeeting(
        bob,
        "Project Review",
        "Q4 project review",
        slot2,
        {alice},
        "R002"  // Same room, overlapping time
    );
    
    // Meeting 3: Client Call (different time)
    time_t start3 = createTime(2024, 12, 26, 14, 0);
    time_t end3 = createTime(2024, 12, 26, 15, 0);
    TimeSlot slot3(start3, end3);
    
    Meeting* meeting3 = scheduler.scheduleMeeting(
        alice,
        "Client Call",
        "Discuss requirements",
        slot3,
        {bob},
        "R001"
    );
    
    if (meeting3) {
        meeting3->display();
    }
    
    // Find available slots
    cout << "\n=== Finding Available Slots ===" << endl;
    time_t dayStart = createTime(2024, 12, 26, 9, 0);
    time_t dayEnd = createTime(2024, 12, 26, 17, 0);
    
    vector<TimeSlot> commonSlots = scheduler.findCommonAvailableSlots(
        {alice, bob, charlie}, dayStart, dayEnd, 60
    );
    
    cout << "Common available slots (60 min) for Alice, Bob, Charlie:" << endl;
    for (size_t i = 0; i < min(commonSlots.size(), size_t(5)); i++) {
        cout << "  " << commonSlots[i].toString() << endl;
    }
    
    // Reschedule meeting
    if (meeting1) {
        cout << "\n=== Rescheduling Meeting ===" << endl;
        time_t newStart = createTime(2024, 12, 26, 11, 0);
        time_t newEnd = createTime(2024, 12, 26, 11, 30);
        TimeSlot newSlot(newStart, newEnd);
        
        scheduler.rescheduleMeeting(meeting1->getId(), newSlot);
        meeting1->display();
    }
    
    // Cancel meeting
    if (meeting3) {
        cout << "=== Cancelling Meeting ===" << endl;
        scheduler.cancelMeeting(meeting3->getId());
    }
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Conflict Detection**
- Check all attendees' availability
- Room availability validation
- Capacity constraints

### 2. **Time Slot Management**
- Overlap detection
- Duration calculation
- Flexible scheduling

### 3. **Calendar Integration**
- Per-user calendar
- TimeSlot-based bookings
- Easy conflict checking

---

## Follow-up Questions

**Q1: How to handle recurring meetings?**
```cpp
class RecurringMeeting {
    RecurrenceType type;
    int interval;
    time_t endDate;
    
    vector<Meeting*> generateInstances();
};
```

**Q2: How to handle time zones?**
```cpp
class TimeZoneConverter {
    time_t convert(time_t t, string fromTZ, string toTZ);
    string display(time_t t, string timezone);
};
```

**Q3: How to implement reminders?**
```cpp
class MeetingReminder {
    time_t reminderTime;
    NotificationChannel* channel;
    
    void schedule(Meeting* meeting, int minutesBefore);
};
```

---

## Compilation

```bash
g++ -std=c++17 meeting_scheduler.cpp -o scheduler
./scheduler
```

---

**Next**: `hard/07-rate-limiter.md`

