# Problem 3: Movie Ticket Booking System

**Difficulty**: Medium  
**Time to Solve**: 45-55 minutes  
**Companies**: BookMyShow, Fandango, AMC

## Problem Statement

Design a movie ticket booking system that can:
1. Browse movies and showtimes
2. Select seats from seat map
3. Temporarily lock seats during booking
4. Process payment and confirm booking
5. Handle concurrent bookings
6. Support different seat types and pricing

### Requirements

**Functional Requirements**:
- List movies and shows
- Display available seats
- Lock seats temporarily (10 min)
- Book and confirm tickets
- Cancel bookings
- Different seat types (Regular, Premium, VIP)
- Multiple theaters and screens

**Non-Functional Requirements**:
- Handle concurrent seat selection
- Prevent double booking
- Seat lock expiration
- Transaction consistency

---

## Concepts Involved

1. **Design Patterns**: Factory, State, Strategy
2. **Concurrency**: Seat locking mechanism
3. **Real-time Updates**: Seat availability

---

## Class Diagram

```
┌────────────────────┐
│     Cinema         │
├────────────────────┤
│ - movies: vector   │
│ - shows: vector    │
│ - bookings: map    │
├────────────────────┤
│ + listMovies()     │
│ + listShows()      │
│ + bookTickets()    │
│ + confirmBooking() │
└────────┬───────────┘
         │
         │ contains
         ├──────────┬──────────┐
         ▼          ▼          ▼
┌─────────────┐ ┌─────────┐ ┌──────────┐
│    Movie    │ │  Show   │ │ Booking  │
├─────────────┤ ├─────────┤ ├──────────┤
│ - id        │ │ - id    │ │ - id     │
│ - title     │ │ - movie │ │ - show   │
│ - genre     │ │ - date  │ │ - seats  │
│ - duration  │ │ - time  │ │ - status │
└─────────────┘ │ - seats │ │ - amount │
                └────┬────┘ └──────────┘
                     │
                     │ has
                     ▼
                ┌─────────┐
                │  Seat   │
                ├─────────┤
                │ - number│
                │ - type  │
                │ - status│
                │ - price │
                ├─────────┤
                │ + lock()│
                │ + book()│
                └─────────┘

Seat State Machine:
  AVAILABLE → LOCKED → BOOKED
       ↑        │
       └────────┘ (expiry/unlock)
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <memory>
#include <mutex>
#include <chrono>

using namespace std;

enum class SeatType { REGULAR, PREMIUM, VIP };
enum class SeatStatus { AVAILABLE, LOCKED, BOOKED };
enum class BookingStatus { PENDING, CONFIRMED, CANCELLED };

// ============== Seat ==============

class Seat {
private:
    string seatNumber;
    SeatType type;
    SeatStatus status;
    double price;
    chrono::system_clock::time_point lockExpiry;
    mutex seatMutex;
    
public:
    Seat(const string& num, SeatType t, double p)
        : seatNumber(num), type(t), status(SeatStatus::AVAILABLE), price(p) {}
    
    string getSeatNumber() const { return seatNumber; }
    SeatType getType() const { return type; }
    SeatStatus getStatus() { 
        lock_guard<mutex> lock(seatMutex);
        
        // Check if lock expired
        if (status == SeatStatus::LOCKED) {
            if (chrono::system_clock::now() > lockExpiry) {
                status = SeatStatus::AVAILABLE;
            }
        }
        return status;
    }
    double getPrice() const { return price; }
    
    bool lock(int minutes = 10) {
        lock_guard<mutex> lock(seatMutex);
        
        if (status != SeatStatus::AVAILABLE) {
            return false;
        }
        
        status = SeatStatus::LOCKED;
        lockExpiry = chrono::system_clock::now() + chrono::minutes(minutes);
        return true;
    }
    
    bool unlock() {
        lock_guard<mutex> lock(seatMutex);
        
        if (status == SeatStatus::LOCKED) {
            status = SeatStatus::AVAILABLE;
            return true;
        }
        return false;
    }
    
    bool book() {
        lock_guard<mutex> lock(seatMutex);
        
        if (status != SeatStatus::LOCKED) {
            return false;
        }
        
        status = SeatStatus::BOOKED;
        return true;
    }
    
    bool release() {
        lock_guard<mutex> lock(seatMutex);
        
        if (status == SeatStatus::BOOKED) {
            status = SeatStatus::AVAILABLE;
            return true;
        }
        return false;
    }
    
    char getDisplayChar() {
        switch(getStatus()) {
            case SeatStatus::AVAILABLE: return 'O';
            case SeatStatus::LOCKED: return 'L';
            case SeatStatus::BOOKED: return 'X';
            default: return '?';
        }
    }
};

// ============== Movie ==============

class Movie {
private:
    string id;
    string title;
    string genre;
    int duration; // minutes
    
public:
    Movie(const string& i, const string& t, const string& g, int d)
        : id(i), title(t), genre(g), duration(d) {}
    
    string getId() const { return id; }
    string getTitle() const { return title; }
    string getGenre() const { return genre; }
    int getDuration() const { return duration; }
};

// ============== Show ==============

class Show {
private:
    string showId;
    Movie* movie;
    string date;
    string time;
    vector<vector<unique_ptr<Seat>>> seats; // 2D seat layout
    int rows, cols;
    
public:
    Show(const string& id, Movie* m, const string& d, const string& t, int r, int c)
        : showId(id), movie(m), date(d), time(t), rows(r), cols(c) {
        
        initializeSeats();
    }
    
    void initializeSeats() {
        for (int i = 0; i < rows; i++) {
            vector<unique_ptr<Seat>> row;
            for (int j = 0; j < cols; j++) {
                string seatNum = string(1, 'A' + i) + to_string(j + 1);
                
                SeatType type;
                double price;
                
                if (i < 2) { // Front rows - Regular
                    type = SeatType::REGULAR;
                    price = 10.0;
                } else if (i < 5) { // Middle rows - Premium
                    type = SeatType::PREMIUM;
                    price = 15.0;
                } else { // Back rows - VIP
                    type = SeatType::VIP;
                    price = 20.0;
                }
                
                row.push_back(make_unique<Seat>(seatNum, type, price));
            }
            seats.push_back(move(row));
        }
    }
    
    string getShowId() const { return showId; }
    Movie* getMovie() const { return movie; }
    string getDate() const { return date; }
    string getTime() const { return time; }
    
    Seat* getSeat(int row, int col) {
        if (row >= 0 && row < rows && col >= 0 && col < cols) {
            return seats[row][col].get();
        }
        return nullptr;
    }
    
    vector<Seat*> getSeats(const vector<pair<int,int>>& positions) {
        vector<Seat*> result;
        for (auto [r, c] : positions) {
            Seat* seat = getSeat(r, c);
            if (seat) result.push_back(seat);
        }
        return result;
    }
    
    void displaySeats() {
        cout << "\n========== SEAT MAP ==========" << endl;
        cout << "Movie: " << movie->getTitle() << endl;
        cout << "Show: " << date << " " << time << endl;
        cout << "O=Available, L=Locked, X=Booked\n" << endl;
        
        cout << "  ";
        for (int j = 0; j < cols; j++) {
            cout << (j + 1) << " ";
        }
        cout << endl;
        
        for (int i = 0; i < rows; i++) {
            cout << (char)('A' + i) << " ";
            for (int j = 0; j < cols; j++) {
                cout << seats[i][j]->getDisplayChar() << " ";
            }
            cout << endl;
        }
        cout << "==============================\n" << endl;
    }
    
    int getAvailableSeatsCount() {
        int count = 0;
        for (auto& row : seats) {
            for (auto& seat : row) {
                if (seat->getStatus() == SeatStatus::AVAILABLE) {
                    count++;
                }
            }
        }
        return count;
    }
};

// ============== Booking ==============

class Booking {
private:
    string bookingId;
    Show* show;
    vector<Seat*> seats;
    string customerName;
    string customerEmail;
    BookingStatus status;
    double totalAmount;
    
    static int bookingCounter;
    
public:
    Booking(Show* s, const vector<Seat*>& sts, const string& name, const string& email)
        : show(s), seats(sts), customerName(name), customerEmail(email),
          status(BookingStatus::PENDING), totalAmount(0) {
        
        bookingId = "BK" + to_string(++bookingCounter);
        
        for (auto* seat : seats) {
            totalAmount += seat->getPrice();
        }
    }
    
    string getBookingId() const { return bookingId; }
    BookingStatus getStatus() const { return status; }
    double getTotalAmount() const { return totalAmount; }
    
    bool confirm() {
        // Book all seats
        for (auto* seat : seats) {
            if (!seat->book()) {
                // Rollback if any seat fails
                for (auto* s : seats) {
                    s->unlock();
                }
                return false;
            }
        }
        
        status = BookingStatus::CONFIRMED;
        return true;
    }
    
    void cancel() {
        for (auto* seat : seats) {
            seat->release();
        }
        status = BookingStatus::CANCELLED;
    }
    
    void display() {
        cout << "\n========== BOOKING DETAILS ==========" << endl;
        cout << "Booking ID: " << bookingId << endl;
        cout << "Customer: " << customerName << endl;
        cout << "Movie: " << show->getMovie()->getTitle() << endl;
        cout << "Show: " << show->getDate() << " " << show->getTime() << endl;
        cout << "Seats: ";
        for (auto* seat : seats) {
            cout << seat->getSeatNumber() << " ";
        }
        cout << endl;
        cout << "Total: $" << totalAmount << endl;
        cout << "Status: " << (status == BookingStatus::CONFIRMED ? "CONFIRMED" : 
                              status == BookingStatus::CANCELLED ? "CANCELLED" : "PENDING") 
             << endl;
        cout << "=====================================\n" << endl;
    }
};

int Booking::bookingCounter = 0;

// ============== Cinema ==============

class Cinema {
private:
    string name;
    vector<unique_ptr<Movie>> movies;
    vector<unique_ptr<Show>> shows;
    map<string, unique_ptr<Booking>> bookings;
    mutex cinemaMutex;
    
public:
    Cinema(const string& n) : name(n) {
        initializeMoviesAndShows();
    }
    
    void initializeMoviesAndShows() {
        // Add movies
        movies.push_back(make_unique<Movie>("M1", "Inception", "Sci-Fi", 148));
        movies.push_back(make_unique<Movie>("M2", "The Matrix", "Action", 136));
        movies.push_back(make_unique<Movie>("M3", "Interstellar", "Sci-Fi", 169));
        
        // Add shows
        shows.push_back(make_unique<Show>("S1", movies[0].get(), "2024-03-15", "10:00 AM", 8, 10));
        shows.push_back(make_unique<Show>("S2", movies[0].get(), "2024-03-15", "02:00 PM", 8, 10));
        shows.push_back(make_unique<Show>("S3", movies[1].get(), "2024-03-15", "11:00 AM", 8, 10));
        shows.push_back(make_unique<Show>("S4", movies[2].get(), "2024-03-15", "03:00 PM", 8, 10));
    }
    
    void listMovies() {
        cout << "\n========== NOW SHOWING ==========" << endl;
        for (auto& movie : movies) {
            cout << movie->getTitle() << " (" << movie->getGenre() << ") - " 
                 << movie->getDuration() << " mins" << endl;
        }
        cout << "=================================\n" << endl;
    }
    
    void listShows() {
        cout << "\n========== SHOWTIMES ==========" << endl;
        for (auto& show : shows) {
            cout << show->getShowId() << " - " << show->getMovie()->getTitle() 
                 << " - " << show->getDate() << " " << show->getTime()
                 << " (Available: " << show->getAvailableSeatsCount() << ")" << endl;
        }
        cout << "==============================\n" << endl;
    }
    
    Show* getShow(const string& showId) {
        for (auto& show : shows) {
            if (show->getShowId() == showId) {
                return show.get();
            }
        }
        return nullptr;
    }
    
    Booking* bookTickets(const string& showId, const vector<pair<int,int>>& seatPositions,
                        const string& customerName, const string& customerEmail) {
        lock_guard<mutex> lock(cinemaMutex);
        
        Show* show = getShow(showId);
        if (!show) {
            cout << "Show not found!" << endl;
            return nullptr;
        }
        
        // Get seats
        vector<Seat*> seats = show->getSeats(seatPositions);
        
        if (seats.size() != seatPositions.size()) {
            cout << "Invalid seat selection!" << endl;
            return nullptr;
        }
        
        // Try to lock all seats
        for (auto* seat : seats) {
            if (!seat->lock()) {
                cout << "Seat " << seat->getSeatNumber() << " not available!" << endl;
                // Unlock previously locked seats
                for (auto* s : seats) {
                    s->unlock();
                }
                return nullptr;
            }
        }
        
        // Create booking
        auto booking = make_unique<Booking>(show, seats, customerName, customerEmail);
        Booking* bookingPtr = booking.get();
        
        cout << "\n✓ Seats locked! Please complete payment within 10 minutes." << endl;
        bookingPtr->display();
        
        bookings[booking->getBookingId()] = move(booking);
        
        return bookingPtr;
    }
    
    bool confirmBooking(const string& bookingId) {
        lock_guard<mutex> lock(cinemaMutex);
        
        auto it = bookings.find(bookingId);
        if (it == bookings.end()) {
            return false;
        }
        
        if (it->second->confirm()) {
            cout << "\n✓ Booking confirmed!" << endl;
            it->second->display();
            return true;
        }
        
        cout << "Failed to confirm booking!" << endl;
        return false;
    }
    
    bool cancelBooking(const string& bookingId) {
        lock_guard<mutex> lock(cinemaMutex);
        
        auto it = bookings.find(bookingId);
        if (it == bookings.end()) {
            return false;
        }
        
        it->second->cancel();
        cout << "✓ Booking cancelled and seats released" << endl;
        return true;
    }
};

// ============== Demo ==============

int main() {
    Cinema cinema("Cineplex Downtown");
    
    cout << "========== Movie Ticket Booking System ==========\n" << endl;
    
    // List movies
    cinema.listMovies();
    
    // List shows
    cinema.listShows();
    
    // View seat map
    Show* show1 = cinema.getShow("S1");
    if (show1) {
        show1->displaySeats();
    }
    
    // Book tickets
    cout << "=== Booking Tickets ===" << endl;
    vector<pair<int,int>> seats1 = {{3, 4}, {3, 5}, {3, 6}}; // Row D, seats 5,6,7
    Booking* booking1 = cinema.bookTickets("S1", seats1, "John Doe", "john@email.com");
    
    if (booking1) {
        // Display updated seat map
        show1->displaySeats();
        
        // Simulate payment
        cout << "\n=== Processing Payment ===" << endl;
        this_thread::sleep_for(chrono::seconds(2));
        cinema.confirmBooking(booking1->getBookingId());
        
        // Display final seat map
        show1->displaySeats();
    }
    
    // Another booking
    cout << "\n=== Another Booking ===" << endl;
    vector<pair<int,int>> seats2 = {{5, 5}, {5, 6}}; // Row F, seats 6,7
    Booking* booking2 = cinema.bookTickets("S1", seats2, "Jane Smith", "jane@email.com");
    
    if (booking2) {
        show1->displaySeats();
        
        // Cancel this booking
        cout << "\n=== Cancelling Booking ===" << endl;
        cinema.cancelBooking(booking2->getBookingId());
        
        show1->displaySeats();
    }
    
    // Try to book already booked seat
    cout << "\n=== Trying to Book Already Booked Seat ===" << endl;
    vector<pair<int,int>> seats3 = {{3, 5}}; // Already booked
    cinema.bookTickets("S1", seats3, "Bob Wilson", "bob@email.com");
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Seat Locking Mechanism**
- Temporary lock (10 min) prevents double booking
- Automatic expiry releases seats
- Thread-safe with mutex

### 2. **2D Seat Layout**
- Visual seat map representation
- Different pricing by row
- Easy seat selection

### 3. **Transaction Flow**
- Lock → Payment → Confirm
- Rollback on failure
- Clean state management

---

## Follow-up Questions

**Q1: How to handle payment failure?**
- Release locked seats
- Create failed booking record
- Notify user

**Q2: How to add seat recommendations?**
```cpp
vector<pair<int,int>> recommendSeats(int count) {
    // Find best available seats (center, middle rows)
}
```

**Q3: How to support multiple theaters?**
- Theater class with multiple screens
- Location-based search
- Different pricing per theater

---

## Compilation

```bash
g++ -std=c++17 -pthread movie_booking.cpp -o movie
./movie
```

---

**Next**: `medium/04-car-rental-system.md`

