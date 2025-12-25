# Problem 1: Parking Lot System

**Difficulty**: Easy  
**Time to Solve**: 30-40 minutes  
**Companies**: Amazon, Microsoft, Uber, Google

## Problem Statement

Design a parking lot system that can:
1. Park vehicles of different types (Car, Motorcycle, Truck)
2. Multiple floors with multiple spots per floor
3. Different spot sizes (Compact, Large, Motorcycle)
4. Track available spots
5. Calculate parking fees based on time
6. Generate parking tickets

### Requirements

**Functional Requirements**:
- Park a vehicle if space available
- Un-park a vehicle and calculate fee
- Display available spots count by type
- Support multiple floors
- Vehicle types: Motorcycle, Car, Truck
- Spot types: Motorcycle, Compact, Large

**Non-Functional Requirements**:
- System should be scalable
- Thread-safe for concurrent access
- Extensible for new vehicle/spot types

### Constraints
- Max 10 floors
- Max 100 spots per floor
- Different pricing for different vehicle types
- Ticket unique ID generation

---

## Concepts Involved

1. **OOP Principles**: Encapsulation, Inheritance, Polymorphism
2. **Design Patterns**: 
   - Singleton (ParkingLot)
   - Factory (Vehicle creation)
   - Strategy (Pricing strategy)
3. **SOLID Principles**: SRP, OCP, DIP
4. **Concurrency**: Thread-safe operations
5. **Enums**: For types and statuses

---

## Class Diagram

```
┌─────────────────────┐
│   ParkingLot        │ ◄───── Singleton
├─────────────────────┤
│ - floors: vector    │
│ - entrance/exit     │
├─────────────────────┤
│ + parkVehicle()     │
│ + unparkVehicle()   │
│ + getAvailableSpots │
└──────────┬──────────┘
           │ 1
           │ contains
           │ *
┌──────────▼──────────┐
│   ParkingFloor      │
├─────────────────────┤
│ - floorId: int      │
│ - spots: vector     │
├─────────────────────┤
│ + addSpot()         │
│ + findAvailableSpot │
│ + parkVehicle()     │
└──────────┬──────────┘
           │ 1
           │ contains
           │ *
┌──────────▼──────────┐
│   ParkingSpot       │ ◄───── Abstract
├─────────────────────┤
│ - spotId: string    │
│ - spotType: enum    │
│ - vehicle: Vehicle* │
│ - available: bool   │
├─────────────────────┤
│ + assignVehicle()   │
│ + removeVehicle()   │
│ + canFit(Vehicle)   │
└──────────┬──────────┘
           │
     ┌─────┴─────┬──────────┐
     ▼           ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│Compact  │ │  Large  │ │Motorcycle│
│  Spot   │ │  Spot   │ │  Spot   │
└─────────┘ └─────────┘ └─────────┘

┌─────────────────────┐
│      Vehicle        │ ◄───── Abstract
├─────────────────────┤
│ - licensePlate      │
│ - vehicleType: enum │
├─────────────────────┤
│ + getType()         │
└──────────┬──────────┘
           │
     ┌─────┴─────┬──────────┐
     ▼           ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│   Car   │ │  Truck  │ │Motorcycle│
└─────────┘ └─────────┘ └─────────┘

┌─────────────────────┐
│   ParkingTicket     │
├─────────────────────┤
│ - ticketId: string  │
│ - vehicle: Vehicle* │
│ - spot: ParkingSpot*│
│ - entryTime: time_t │
│ - exitTime: time_t  │
├─────────────────────┤
│ + calculateFee()    │
└─────────────────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <unordered_map>
#include <ctime>
#include <mutex>
#include <iomanip>
#include <sstream>

using namespace std;

// ============== Enums ==============

enum class VehicleType {
    MOTORCYCLE,
    CAR,
    TRUCK
};

enum class SpotType {
    MOTORCYCLE,
    COMPACT,
    LARGE
};

enum class ParkingSpotStatus {
    AVAILABLE,
    OCCUPIED
};

// ============== Vehicle Classes ==============

class Vehicle {
protected:
    string licensePlate;
    VehicleType type;
    
public:
    Vehicle(const string& plate, VehicleType t) 
        : licensePlate(plate), type(t) {}
    
    virtual ~Vehicle() = default;
    
    string getLicensePlate() const { return licensePlate; }
    VehicleType getType() const { return type; }
    
    virtual string getTypeName() const = 0;
};

class Motorcycle : public Vehicle {
public:
    Motorcycle(const string& plate) 
        : Vehicle(plate, VehicleType::MOTORCYCLE) {}
    
    string getTypeName() const override { return "Motorcycle"; }
};

class Car : public Vehicle {
public:
    Car(const string& plate) 
        : Vehicle(plate, VehicleType::CAR) {}
    
    string getTypeName() const override { return "Car"; }
};

class Truck : public Vehicle {
public:
    Truck(const string& plate) 
        : Vehicle(plate, VehicleType::TRUCK) {}
    
    string getTypeName() const override { return "Truck"; }
};

// ============== Parking Spot Classes ==============

class ParkingSpot {
protected:
    string spotId;
    SpotType spotType;
    Vehicle* parkedVehicle;
    ParkingSpotStatus status;
    int floorNumber;
    
public:
    ParkingSpot(const string& id, SpotType type, int floor)
        : spotId(id), spotType(type), parkedVehicle(nullptr), 
          status(ParkingSpotStatus::AVAILABLE), floorNumber(floor) {}
    
    virtual ~ParkingSpot() = default;
    
    bool isAvailable() const {
        return status == ParkingSpotStatus::AVAILABLE;
    }
    
    virtual bool canFitVehicle(VehicleType vType) const = 0;
    
    bool assignVehicle(Vehicle* vehicle) {
        if (!isAvailable()) return false;
        if (!canFitVehicle(vehicle->getType())) return false;
        
        parkedVehicle = vehicle;
        status = ParkingSpotStatus::OCCUPIED;
        return true;
    }
    
    Vehicle* removeVehicle() {
        Vehicle* vehicle = parkedVehicle;
        parkedVehicle = nullptr;
        status = ParkingSpotStatus::AVAILABLE;
        return vehicle;
    }
    
    string getSpotId() const { return spotId; }
    SpotType getSpotType() const { return spotType; }
    int getFloor() const { return floorNumber; }
    Vehicle* getParkedVehicle() const { return parkedVehicle; }
};

class MotorcycleSpot : public ParkingSpot {
public:
    MotorcycleSpot(const string& id, int floor)
        : ParkingSpot(id, SpotType::MOTORCYCLE, floor) {}
    
    bool canFitVehicle(VehicleType vType) const override {
        return vType == VehicleType::MOTORCYCLE;
    }
};

class CompactSpot : public ParkingSpot {
public:
    CompactSpot(const string& id, int floor)
        : ParkingSpot(id, SpotType::COMPACT, floor) {}
    
    bool canFitVehicle(VehicleType vType) const override {
        return vType == VehicleType::MOTORCYCLE || vType == VehicleType::CAR;
    }
};

class LargeSpot : public ParkingSpot {
public:
    LargeSpot(const string& id, int floor)
        : ParkingSpot(id, SpotType::LARGE, floor) {}
    
    bool canFitVehicle(VehicleType vType) const override {
        return true; // Can fit any vehicle
    }
};

// ============== Parking Ticket ==============

class ParkingTicket {
private:
    string ticketId;
    Vehicle* vehicle;
    ParkingSpot* spot;
    time_t entryTime;
    time_t exitTime;
    
    static int ticketCounter;
    
    string generateTicketId() {
        return "TKT" + to_string(++ticketCounter);
    }
    
public:
    ParkingTicket(Vehicle* v, ParkingSpot* s)
        : vehicle(v), spot(s), exitTime(0) {
        ticketId = generateTicketId();
        entryTime = time(nullptr);
    }
    
    string getTicketId() const { return ticketId; }
    Vehicle* getVehicle() const { return vehicle; }
    ParkingSpot* getSpot() const { return spot; }
    time_t getEntryTime() const { return entryTime; }
    
    void setExitTime(time_t t) { exitTime = t; }
    
    double calculateFee() const {
        if (exitTime == 0) return 0.0;
        
        double hours = difftime(exitTime, entryTime) / 3600.0;
        
        // Pricing strategy based on vehicle type
        double hourlyRate;
        switch (vehicle->getType()) {
            case VehicleType::MOTORCYCLE:
                hourlyRate = 5.0;
                break;
            case VehicleType::CAR:
                hourlyRate = 10.0;
                break;
            case VehicleType::TRUCK:
                hourlyRate = 20.0;
                break;
        }
        
        // Minimum 1 hour charge
        if (hours < 1.0) hours = 1.0;
        
        return hours * hourlyRate;
    }
    
    void display() const {
        cout << "\n========== PARKING TICKET ==========" << endl;
        cout << "Ticket ID: " << ticketId << endl;
        cout << "License Plate: " << vehicle->getLicensePlate() << endl;
        cout << "Vehicle Type: " << vehicle->getTypeName() << endl;
        cout << "Spot: " << spot->getSpotId() << " (Floor " << spot->getFloor() << ")" << endl;
        
        char timeStr[26];
        ctime_r(&entryTime, timeStr);
        cout << "Entry Time: " << timeStr;
        cout << "====================================" << endl;
    }
};

int ParkingTicket::ticketCounter = 0;

// ============== Parking Floor ==============

class ParkingFloor {
private:
    int floorId;
    vector<unique_ptr<ParkingSpot>> spots;
    
public:
    ParkingFloor(int id) : floorId(id) {}
    
    void addSpot(unique_ptr<ParkingSpot> spot) {
        spots.push_back(move(spot));
    }
    
    ParkingSpot* findAvailableSpot(VehicleType vType) {
        for (auto& spot : spots) {
            if (spot->isAvailable() && spot->canFitVehicle(vType)) {
                return spot.get();
            }
        }
        return nullptr;
    }
    
    int getAvailableSpotsCount(SpotType sType) const {
        int count = 0;
        for (const auto& spot : spots) {
            if (spot->isAvailable() && spot->getSpotType() == sType) {
                count++;
            }
        }
        return count;
    }
    
    int getFloorId() const { return floorId; }
};

// ============== Parking Lot (Singleton) ==============

class ParkingLot {
private:
    static ParkingLot* instance;
    static mutex mtx;
    
    string name;
    vector<unique_ptr<ParkingFloor>> floors;
    unordered_map<string, unique_ptr<ParkingTicket>> activeTickets;
    
    ParkingLot(const string& n) : name(n) {}
    
public:
    static ParkingLot* getInstance(const string& name = "Main Parking Lot") {
        lock_guard<mutex> lock(mtx);
        if (instance == nullptr) {
            instance = new ParkingLot(name);
        }
        return instance;
    }
    
    // Delete copy constructor and assignment
    ParkingLot(const ParkingLot&) = delete;
    ParkingLot& operator=(const ParkingLot&) = delete;
    
    void addFloor(unique_ptr<ParkingFloor> floor) {
        floors.push_back(move(floor));
    }
    
    ParkingTicket* parkVehicle(Vehicle* vehicle) {
        lock_guard<mutex> lock(mtx);
        
        // Check if vehicle already parked
        if (activeTickets.find(vehicle->getLicensePlate()) != activeTickets.end()) {
            cout << "Vehicle already parked!" << endl;
            return nullptr;
        }
        
        // Find available spot across all floors
        for (auto& floor : floors) {
            ParkingSpot* spot = floor->findAvailableSpot(vehicle->getType());
            if (spot != nullptr) {
                if (spot->assignVehicle(vehicle)) {
                    auto ticket = make_unique<ParkingTicket>(vehicle, spot);
                    ParkingTicket* ticketPtr = ticket.get();
                    activeTickets[vehicle->getLicensePlate()] = move(ticket);
                    
                    cout << "\n✓ Vehicle parked successfully!" << endl;
                    ticketPtr->display();
                    return ticketPtr;
                }
            }
        }
        
        cout << "\n✗ No available spot for " << vehicle->getTypeName() << endl;
        return nullptr;
    }
    
    double unparkVehicle(const string& licensePlate) {
        lock_guard<mutex> lock(mtx);
        
        auto it = activeTickets.find(licensePlate);
        if (it == activeTickets.end()) {
            cout << "Ticket not found!" << endl;
            return 0.0;
        }
        
        ParkingTicket* ticket = it->second.get();
        ticket->setExitTime(time(nullptr));
        
        ParkingSpot* spot = ticket->getSpot();
        spot->removeVehicle();
        
        double fee = ticket->calculateFee();
        
        cout << "\n========== EXIT RECEIPT ==========" << endl;
        cout << "Ticket ID: " << ticket->getTicketId() << endl;
        cout << "License Plate: " << licensePlate << endl;
        cout << "Parking Fee: $" << fixed << setprecision(2) << fee << endl;
        cout << "==================================\n" << endl;
        
        activeTickets.erase(it);
        return fee;
    }
    
    void displayAvailability() const {
        cout << "\n========== PARKING AVAILABILITY ==========" << endl;
        for (const auto& floor : floors) {
            cout << "Floor " << floor->getFloorId() << ":" << endl;
            cout << "  Motorcycle spots: " 
                 << floor->getAvailableSpotsCount(SpotType::MOTORCYCLE) << endl;
            cout << "  Compact spots: " 
                 << floor->getAvailableSpotsCount(SpotType::COMPACT) << endl;
            cout << "  Large spots: " 
                 << floor->getAvailableSpotsCount(SpotType::LARGE) << endl;
        }
        cout << "==========================================\n" << endl;
    }
    
    static void cleanup() {
        delete instance;
        instance = nullptr;
    }
};

ParkingLot* ParkingLot::instance = nullptr;
mutex ParkingLot::mtx;

// ============== Demo / Test ==============

int main() {
    // Initialize parking lot
    ParkingLot* parkingLot = ParkingLot::getInstance("Downtown Parking");
    
    // Create 2 floors
    auto floor1 = make_unique<ParkingFloor>(1);
    floor1->addSpot(make_unique<MotorcycleSpot>("F1-M1", 1));
    floor1->addSpot(make_unique<MotorcycleSpot>("F1-M2", 1));
    floor1->addSpot(make_unique<CompactSpot>("F1-C1", 1));
    floor1->addSpot(make_unique<CompactSpot>("F1-C2", 1));
    floor1->addSpot(make_unique<LargeSpot>("F1-L1", 1));
    
    auto floor2 = make_unique<ParkingFloor>(2);
    floor2->addSpot(make_unique<CompactSpot>("F2-C1", 2));
    floor2->addSpot(make_unique<CompactSpot>("F2-C2", 2));
    floor2->addSpot(make_unique<LargeSpot>("F2-L1", 2));
    floor2->addSpot(make_unique<LargeSpot>("F2-L2", 2));
    
    parkingLot->addFloor(move(floor1));
    parkingLot->addFloor(move(floor2));
    
    // Display initial availability
    parkingLot->displayAvailability();
    
    // Create vehicles
    Car car1("ABC123");
    Motorcycle bike1("XYZ789");
    Truck truck1("TRK456");
    Car car2("DEF456");
    
    // Park vehicles
    parkingLot->parkVehicle(&car1);
    parkingLot->parkVehicle(&bike1);
    parkingLot->parkVehicle(&truck1);
    parkingLot->parkVehicle(&car2);
    
    // Display availability after parking
    parkingLot->displayAvailability();
    
    // Unpark a vehicle
    cout << "Unparking car ABC123..." << endl;
    parkingLot->unparkVehicle("ABC123");
    
    // Display final availability
    parkingLot->displayAvailability();
    
    // Cleanup
    ParkingLot::cleanup();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Singleton Pattern for ParkingLot**
- Only one parking lot instance should exist
- Thread-safe using mutex
- Global access point

### 2. **Inheritance for Vehicle and Spot Types**
- Base classes define common interface
- Derived classes implement specific behavior
- Easy to add new types (OCP)

### 3. **Strategy Pattern for Pricing**
- Different rates for different vehicle types
- Easy to modify pricing logic
- Can be extracted to separate PricingStrategy class

### 4. **Encapsulation**
- Private members with public interface
- Controlled access to parking spots
- Ticket generation internal to system

---

## Follow-up Questions (Interview)

### Q1: How would you handle payment processing?
**Answer**: Create a `PaymentProcessor` interface with implementations for different payment methods (Cash, Card, Mobile).

```cpp
class PaymentProcessor {
public:
    virtual bool processPayment(double amount) = 0;
};

class CashPayment : public PaymentProcessor {
    bool processPayment(double amount) override {
        // Cash handling logic
    }
};
```

### Q2: How to add electric vehicle charging spots?
**Answer**: Create `EVChargingSpot` class inheriting from `ParkingSpot`, add charging status and methods.

### Q3: How to handle parking reservations?
**Answer**: Add `ReservationSystem` class with time-based booking, modify spot availability to check reservations.

### Q4: How to optimize spot finding?
**Answer**: Maintain a priority queue or index of available spots by type for O(1) lookup instead of O(n) iteration.

### Q5: How to handle concurrent access?
**Answer**: Already handled with mutex in singleton. For better performance, use read-write locks or fine-grained locking per floor.

---

## Complexity Analysis

- **Park Vehicle**: O(n) where n = total spots (can optimize to O(1))
- **Unpark Vehicle**: O(1) using hash map
- **Check Availability**: O(n) per floor
- **Space Complexity**: O(n) for storing spots and tickets

---

## Compilation & Execution

```bash
g++ -std=c++17 -pthread parking_lot.cpp -o parking_lot
./parking_lot
```

---

**Next Problem**: Move to `02-library-management-system.md`

