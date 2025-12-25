# Problem 2: Hotel Booking System

**Difficulty**: Medium  
**Time to Solve**: 40-50 minutes  
**Companies**: Booking.com, Airbnb, Expedia, OYO

## Problem Statement

Design a hotel booking system that can:
1. Search available rooms by date range and type
2. Make, modify, and cancel reservations
3. Handle multiple room types with different pricing
4. Process payments
5. Manage room inventory
6. Support guest check-in/check-out

### Requirements

**Functional Requirements**:
- Search rooms by criteria (dates, type, guests)
- Book rooms with guest details
- Modify/cancel bookings
- Dynamic pricing (weekday, weekend, season)
- Check-in and check-out process
- Payment processing
- Room service orders

**Non-Functional Requirements**:
- Handle concurrent bookings
- Prevent double booking
- Data consistency
- Scalable architecture

---

## Concepts Involved

1. **Design Patterns**:
   - **Factory** (Room creation)
   - **Builder** (Booking creation)
   - **Strategy** (Pricing strategies)
   - **Observer** (Booking notifications)
2. **Concurrency**: Lock rooms during booking
3. **SOLID**: All principles

---

## Class Diagram

```
┌────────────────────┐
│    Hotel           │
├────────────────────┤
│ - rooms: vector    │
│ - bookings: map    │
├────────────────────┤
│ + searchRooms()    │
│ + makeBooking()    │
│ + cancelBooking()  │
└────────┬───────────┘
         │
         ├──────────┐
         ▼          ▼
┌─────────────┐ ┌──────────┐
│    Room     │ │  Booking │
├─────────────┤ ├──────────┤
│ - roomNum   │ │ - id     │
│ - type      │ │ - room   │
│ - price     │ │ - guest  │
│ - status    │ │ - dates  │
└─────────────┘ └──────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <ctime>
#include <algorithm>
#include <mutex>

using namespace std;

// ============== Enums ==============

enum class RoomType {
    SINGLE,
    DOUBLE,
    DELUXE,
    SUITE
};

enum class RoomStatus {
    AVAILABLE,
    BOOKED,
    OCCUPIED,
    MAINTENANCE
};

enum class BookingStatus {
    PENDING,
    CONFIRMED,
    CHECKED_IN,
    CHECKED_OUT,
    CANCELLED
};

// ============== Date Helper ==============

struct Date {
    int year, month, day;
    
    Date(int y = 2024, int m = 1, int d = 1) : year(y), month(m), day(d) {}
    
    bool operator<(const Date& other) const {
        if (year != other.year) return year < other.year;
        if (month != other.month) return month < other.month;
        return day < other.day;
    }
    
    bool operator==(const Date& other) const {
        return year == other.year && month == other.month && day == other.day;
    }
    
    bool operator<=(const Date& other) const {
        return *this < other || *this == other;
    }
    
    Date nextDay() const {
        Date next = *this;
        next.day++;
        if (next.day > 30) { // Simplified
            next.day = 1;
            next.month++;
            if (next.month > 12) {
                next.month = 1;
                next.year++;
            }
        }
        return next;
    }
    
    int daysBetween(const Date& other) const {
        int days = 0;
        Date current = *this;
        while (current < other) {
            days++;
            current = current.nextDay();
        }
        return days;
    }
    
    string toString() const {
        return to_string(year) + "-" + 
               (month < 10 ? "0" : "") + to_string(month) + "-" +
               (day < 10 ? "0" : "") + to_string(day);
    }
};

// ============== Guest ==============

class Guest {
private:
    string id;
    string name;
    string email;
    string phone;
    
public:
    Guest(const string& i, const string& n, const string& e, const string& p)
        : id(i), name(n), email(e), phone(p) {}
    
    string getId() const { return id; }
    string getName() const { return name; }
    string getEmail() const { return email; }
};

// ============== Pricing Strategy ==============

class PricingStrategy {
public:
    virtual ~PricingStrategy() = default;
    virtual double calculatePrice(RoomType type, const Date& date, int nights) = 0;
};

class StandardPricing : public PricingStrategy {
private:
    map<RoomType, double> basePrice = {
        {RoomType::SINGLE, 100.0},
        {RoomType::DOUBLE, 150.0},
        {RoomType::DELUXE, 250.0},
        {RoomType::SUITE, 500.0}
    };
    
public:
    double calculatePrice(RoomType type, const Date& date, int nights) override {
        double price = basePrice[type] * nights;
        
        // Weekend pricing (simplified: day 6,7 of month)
        if (date.day % 7 >= 5) {
            price *= 1.5;
        }
        
        return price;
    }
};

// ============== Room ==============

class Room {
private:
    string roomNumber;
    RoomType type;
    int capacity;
    double basePrice;
    RoomStatus status;
    map<Date, bool> availability; // date -> isAvailable
    mutex roomMutex;
    
public:
    Room(const string& num, RoomType t, int cap, double price)
        : roomNumber(num), type(t), capacity(cap), 
          basePrice(price), status(RoomStatus::AVAILABLE) {}
    
    string getRoomNumber() const { return roomNumber; }
    RoomType getType() const { return type; }
    int getCapacity() const { return capacity; }
    double getBasePrice() const { return basePrice; }
    RoomStatus getStatus() const { return status; }
    
    bool isAvailableForDateRange(const Date& checkIn, const Date& checkOut) {
        lock_guard<mutex> lock(roomMutex);
        
        Date current = checkIn;
        while (current < checkOut) {
            if (availability.count(current) && !availability[current]) {
                return false;
            }
            current = current.nextDay();
        }
        return true;
    }
    
    bool blockDates(const Date& checkIn, const Date& checkOut) {
        lock_guard<mutex> lock(roomMutex);
        
        if (!isAvailableForDateRange(checkIn, checkOut)) {
            return false;
        }
        
        Date current = checkIn;
        while (current < checkOut) {
            availability[current] = false;
            current = current.nextDay();
        }
        
        status = RoomStatus::BOOKED;
        return true;
    }
    
    void releaseDates(const Date& checkIn, const Date& checkOut) {
        lock_guard<mutex> lock(roomMutex);
        
        Date current = checkIn;
        while (current < checkOut) {
            availability[current] = true;
            current = current.nextDay();
        }
        
        status = RoomStatus::AVAILABLE;
    }
    
    void setStatus(RoomStatus s) {
        status = s;
    }
    
    string getTypeString() const {
        switch(type) {
            case RoomType::SINGLE: return "Single";
            case RoomType::DOUBLE: return "Double";
            case RoomType::DELUXE: return "Deluxe";
            case RoomType::SUITE: return "Suite";
            default: return "Unknown";
        }
    }
};

// ============== Booking ==============

class Booking {
private:
    string bookingId;
    Guest* guest;
    Room* room;
    Date checkInDate;
    Date checkOutDate;
    BookingStatus status;
    double totalAmount;
    time_t bookingTime;
    
    static int bookingCounter;
    
public:
    Booking(Guest* g, Room* r, const Date& in, const Date& out, double amount)
        : guest(g), room(r), checkInDate(in), checkOutDate(out),
          status(BookingStatus::PENDING), totalAmount(amount) {
        
        bookingId = "BK" + to_string(++bookingCounter);
        bookingTime = time(nullptr);
    }
    
    string getBookingId() const { return bookingId; }
    Guest* getGuest() const { return guest; }
    Room* getRoom() const { return room; }
    Date getCheckInDate() const { return checkInDate; }
    Date getCheckOutDate() const { return checkOutDate; }
    BookingStatus getStatus() const { return status; }
    double getTotalAmount() const { return totalAmount; }
    
    void confirm() {
        status = BookingStatus::CONFIRMED;
    }
    
    void checkIn() {
        if (status == BookingStatus::CONFIRMED) {
            status = BookingStatus::CHECKED_IN;
            room->setStatus(RoomStatus::OCCUPIED);
        }
    }
    
    void checkOut() {
        if (status == BookingStatus::CHECKED_IN) {
            status = BookingStatus::CHECKED_OUT;
            room->setStatus(RoomStatus::AVAILABLE);
        }
    }
    
    void cancel() {
        status = BookingStatus::CANCELLED;
        room->releaseDates(checkInDate, checkOutDate);
    }
    
    void display() const {
        cout << "\n========== BOOKING DETAILS ==========" << endl;
        cout << "Booking ID: " << bookingId << endl;
        cout << "Guest: " << guest->getName() << endl;
        cout << "Room: " << room->getRoomNumber() 
             << " (" << room->getTypeString() << ")" << endl;
        cout << "Check-in: " << checkInDate.toString() << endl;
        cout << "Check-out: " << checkOutDate.toString() << endl;
        cout << "Nights: " << checkInDate.daysBetween(checkOutDate) << endl;
        cout << "Total: $" << totalAmount << endl;
        cout << "Status: " << (int)status << endl;
        cout << "====================================\n" << endl;
    }
};

int Booking::bookingCounter = 0;

// ============== Hotel ==============

class Hotel {
private:
    string name;
    vector<unique_ptr<Room>> rooms;
    map<string, unique_ptr<Guest>> guests;
    map<string, unique_ptr<Booking>> bookings;
    unique_ptr<PricingStrategy> pricingStrategy;
    mutex hotelMutex;
    
public:
    Hotel(const string& n) : name(n) {
        pricingStrategy = make_unique<StandardPricing>();
        initializeRooms();
    }
    
    void initializeRooms() {
        // Add some rooms
        rooms.push_back(make_unique<Room>("101", RoomType::SINGLE, 1, 100));
        rooms.push_back(make_unique<Room>("102", RoomType::SINGLE, 1, 100));
        rooms.push_back(make_unique<Room>("201", RoomType::DOUBLE, 2, 150));
        rooms.push_back(make_unique<Room>("202", RoomType::DOUBLE, 2, 150));
        rooms.push_back(make_unique<Room>("301", RoomType::DELUXE, 2, 250));
        rooms.push_back(make_unique<Room>("401", RoomType::SUITE, 4, 500));
    }
    
    Guest* registerGuest(const string& id, const string& name, 
                        const string& email, const string& phone) {
        lock_guard<mutex> lock(hotelMutex);
        
        if (guests.find(id) != guests.end()) {
            return guests[id].get();
        }
        
        auto guest = make_unique<Guest>(id, name, email, phone);
        Guest* guestPtr = guest.get();
        guests[id] = move(guest);
        
        return guestPtr;
    }
    
    vector<Room*> searchAvailableRooms(const Date& checkIn, const Date& checkOut,
                                       RoomType type, int guests) {
        vector<Room*> available;
        
        for (auto& room : rooms) {
            if (room->getType() == type && 
                room->getCapacity() >= guests &&
                room->isAvailableForDateRange(checkIn, checkOut)) {
                available.push_back(room.get());
            }
        }
        
        return available;
    }
    
    Booking* makeBooking(Guest* guest, Room* room, 
                        const Date& checkIn, const Date& checkOut) {
        lock_guard<mutex> lock(hotelMutex);
        
        // Calculate price
        int nights = checkIn.daysBetween(checkOut);
        double price = pricingStrategy->calculatePrice(room->getType(), checkIn, nights);
        
        // Block room dates
        if (!room->blockDates(checkIn, checkOut)) {
            cout << "Failed to book room - not available!" << endl;
            return nullptr;
        }
        
        // Create booking
        auto booking = make_unique<Booking>(guest, room, checkIn, checkOut, price);
        booking->confirm();
        
        Booking* bookingPtr = booking.get();
        bookings[booking->getBookingId()] = move(booking);
        
        cout << "✓ Booking successful!" << endl;
        return bookingPtr;
    }
    
    bool cancelBooking(const string& bookingId) {
        lock_guard<mutex> lock(hotelMutex);
        
        auto it = bookings.find(bookingId);
        if (it == bookings.end()) {
            return false;
        }
        
        it->second->cancel();
        cout << "✓ Booking cancelled" << endl;
        return true;
    }
    
    bool checkIn(const string& bookingId) {
        lock_guard<mutex> lock(hotelMutex);
        
        auto it = bookings.find(bookingId);
        if (it == bookings.end()) {
            return false;
        }
        
        it->second->checkIn();
        cout << "✓ Checked in successfully" << endl;
        return true;
    }
    
    bool checkOut(const string& bookingId) {
        lock_guard<mutex> lock(hotelMutex);
        
        auto it = bookings.find(bookingId);
        if (it == bookings.end()) {
            return false;
        }
        
        it->second->checkOut();
        cout << "✓ Checked out successfully" << endl;
        return true;
    }
    
    void displayAvailableRooms(const Date& checkIn, const Date& checkOut) {
        cout << "\n========== AVAILABLE ROOMS ==========" << endl;
        cout << "Check-in: " << checkIn.toString() << endl;
        cout << "Check-out: " << checkOut.toString() << endl;
        cout << "-------------------------------------" << endl;
        
        for (auto& room : rooms) {
            if (room->isAvailableForDateRange(checkIn, checkOut)) {
                cout << room->getRoomNumber() << " - " 
                     << room->getTypeString() << " - $" 
                     << room->getBasePrice() << "/night" << endl;
            }
        }
        cout << "====================================\n" << endl;
    }
};

// ============== Demo ==============

int main() {
    Hotel hotel("Grand Plaza Hotel");
    
    cout << "========== Hotel Booking System Demo ==========\n" << endl;
    
    // Register guests
    Guest* guest1 = hotel.registerGuest("G001", "John Doe", "john@email.com", "1234567890");
    Guest* guest2 = hotel.registerGuest("G002", "Jane Smith", "jane@email.com", "0987654321");
    
    // Define dates
    Date checkIn(2024, 3, 15);
    Date checkOut(2024, 3, 18);
    
    // Display available rooms
    hotel.displayAvailableRooms(checkIn, checkOut);
    
    // Search for specific room type
    cout << "=== Searching for Double Rooms ===" << endl;
    auto doubleRooms = hotel.searchAvailableRooms(checkIn, checkOut, RoomType::DOUBLE, 2);
    cout << "Found " << doubleRooms.size() << " available double rooms\n" << endl;
    
    // Make booking
    cout << "=== Making Booking ===" << endl;
    if (!doubleRooms.empty()) {
        Booking* booking1 = hotel.makeBooking(guest1, doubleRooms[0], checkIn, checkOut);
        if (booking1) {
            booking1->display();
            
            // Check-in
            cout << "=== Check-in Process ===" << endl;
            hotel.checkIn(booking1->getBookingId());
            
            // Check-out
            cout << "\n=== Check-out Process ===" << endl;
            hotel.checkOut(booking1->getBookingId());
        }
    }
    
    // Make another booking
    cout << "\n=== Another Booking ===" << endl;
    auto suiteRooms = hotel.searchAvailableRooms(checkIn, checkOut, RoomType::SUITE, 4);
    if (!suiteRooms.empty()) {
        Booking* booking2 = hotel.makeBooking(guest2, suiteRooms[0], checkIn, checkOut);
        if (booking2) {
            booking2->display();
            
            // Cancel booking
            cout << "=== Cancelling Booking ===" << endl;
            hotel.cancelBooking(booking2->getBookingId());
        }
    }
    
    // Display final availability
    hotel.displayAvailableRooms(checkIn, checkOut);
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Date-based Availability**
- Track availability per date
- Prevent double booking
- Thread-safe blocking

### 2. **Pricing Strategy**
- Dynamic pricing (weekends, seasons)
- Easy to add new strategies
- Per-night calculation

### 3. **Booking Lifecycle**
- Pending → Confirmed → Checked-in → Checked-out
- Proper state transitions
- Room status sync

---

## Follow-up Questions

**Q1: How to handle overbooking?**
```cpp
class OverbookingStrategy {
    bool allowOverbooking(RoomType type, Date date) {
        // Allow 10% overbooking for certain types
        return type != RoomType::SUITE;
    }
};
```

**Q2: How to add discounts/promotions?**
```cpp
class PromotionPricing : public PricingStrategy {
    double applyDiscount(double price, string promoCode) {
        if (promoCode == "SUMMER20") return price * 0.8;
        return price;
    }
};
```

**Q3: How to scale to multiple hotels?**
- Hotel chain management
- Centralized booking system
- Distributed database per region

---

## Compilation

```bash
g++ -std=c++17 -pthread hotel_booking.cpp -o hotel
./hotel
```

---

**Next Problem**: `medium/03-movie-ticket-booking.md`

