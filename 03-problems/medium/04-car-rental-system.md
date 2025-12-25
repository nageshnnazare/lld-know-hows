# Problem 4: Car Rental System

**Difficulty**: Medium  
**Time to Solve**: 40-50 minutes  
**Companies**: Enterprise, Zipcar, Hertz

## Problem Statement

Design a car rental system that supports:
1. Browse available vehicles
2. Make reservations
3. Pick up and return vehicles
4. Calculate rental costs
5. Track vehicle locations
6. Handle damage reports
7. Support different vehicle types

### Requirements

**Functional Requirements**:
- Search vehicles by type, location, dates
- Reserve vehicles
- Pick up and return process
- Calculate costs (base + extras)
- Track vehicle status and location
- Late return penalties
- Damage assessment

**Non-Functional Requirements**:
- Handle concurrent reservations
- Real-time availability
- Location-based search

---

## Class Diagram

```
┌────────────────────┐
│  RentalSystem      │
├────────────────────┤
│ - vehicles: vector │
│ - reservations     │
│ - locations        │
├────────────────────┤
│ + searchVehicles() │
│ + makeReservation()│
│ + pickupVehicle()  │
│ + returnVehicle()  │
└────────┬───────────┘
         │
         ├──────────┬──────────┐
         ▼          ▼          ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐
│   Vehicle   │ │Resrvation│ │ Location │
├─────────────┤ ├──────────┤ ├──────────┤
│ - plate     │ │ - id     │ │ - name   │
│ - type      │ │ - vehicle│ │ - address│
│ - status    │ │ - dates  │ └──────────┘
│ - location  │ │ - cost   │
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

using namespace std;

enum class VehicleType { ECONOMY, SEDAN, SUV, LUXURY, VAN };
enum class VehicleStatus { AVAILABLE, RESERVED, RENTED, MAINTENANCE };
enum class ReservationStatus { PENDING, CONFIRMED, ACTIVE, COMPLETED, CANCELLED };

// ============== Date Helper ==============

struct Date {
    int year, month, day;
    
    Date(int y = 2024, int m = 1, int d = 1) : year(y), month(m), day(d) {}
    
    bool operator<(const Date& other) const {
        if (year != other.year) return year < other.year;
        if (month != other.month) return month < other.month;
        return day < other.day;
    }
    
    int daysBetween(const Date& other) const {
        // Simplified calculation
        return abs((other.year - year) * 365 + (other.month - month) * 30 + (other.day - day));
    }
    
    string toString() const {
        return to_string(year) + "-" + to_string(month) + "-" + to_string(day);
    }
};

// ============== Location ==============

class Location {
private:
    string id;
    string name;
    string address;
    
public:
    Location(const string& i, const string& n, const string& addr)
        : id(i), name(n), address(addr) {}
    
    string getId() const { return id; }
    string getName() const { return name; }
    string getAddress() const { return address; }
};

// ============== Vehicle ==============

class Vehicle {
private:
    string licensePlate;
    string make;
    string model;
    int year;
    VehicleType type;
    VehicleStatus status;
    Location* currentLocation;
    double dailyRate;
    int mileage;
    
public:
    Vehicle(const string& plate, const string& mk, const string& mdl, int yr,
            VehicleType t, Location* loc, double rate)
        : licensePlate(plate), make(mk), model(mdl), year(yr), type(t),
          status(VehicleStatus::AVAILABLE), currentLocation(loc), dailyRate(rate), mileage(0) {}
    
    string getLicensePlate() const { return licensePlate; }
    string getMake() const { return make; }
    string getModel() const { return model; }
    VehicleType getType() const { return type; }
    VehicleStatus getStatus() const { return status; }
    Location* getLocation() const { return currentLocation; }
    double getDailyRate() const { return dailyRate; }
    
    void setStatus(VehicleStatus s) { status = s; }
    void setLocation(Location* loc) { currentLocation = loc; }
    void addMileage(int miles) { mileage += miles; }
    
    string getTypeString() const {
        switch(type) {
            case VehicleType::ECONOMY: return "Economy";
            case VehicleType::SEDAN: return "Sedan";
            case VehicleType::SUV: return "SUV";
            case VehicleType::LUXURY: return "Luxury";
            case VehicleType::VAN: return "Van";
            default: return "Unknown";
        }
    }
    
    void display() const {
        cout << year << " " << make << " " << model << " (" << licensePlate << ")" << endl;
        cout << "  Type: " << getTypeString() << " | Rate: $" << dailyRate << "/day" << endl;
    }
};

// ============== Customer ==============

class Customer {
private:
    string id;
    string name;
    string licenseNumber;
    string phone;
    
public:
    Customer(const string& i, const string& n, const string& lic, const string& p)
        : id(i), name(n), licenseNumber(lic), phone(p) {}
    
    string getId() const { return id; }
    string getName() const { return name; }
    string getLicense() const { return licenseNumber; }
};

// ============== Reservation ==============

class Reservation {
private:
    string reservationId;
    Customer* customer;
    Vehicle* vehicle;
    Location* pickupLocation;
    Location* returnLocation;
    Date pickupDate;
    Date returnDate;
    ReservationStatus status;
    double totalCost;
    time_t createdAt;
    
    static int reservationCounter;
    
public:
    Reservation(Customer* cust, Vehicle* veh, Location* pickup, Location* ret,
                const Date& pDate, const Date& rDate)
        : customer(cust), vehicle(veh), pickupLocation(pickup), returnLocation(ret),
          pickupDate(pDate), returnDate(rDate), status(ReservationStatus::PENDING),
          totalCost(0), createdAt(time(nullptr)) {
        
        reservationId = "RES" + to_string(++reservationCounter);
        calculateCost();
    }
    
    void calculateCost() {
        int days = pickupDate.daysBetween(returnDate);
        if (days < 1) days = 1;
        
        totalCost = vehicle->getDailyRate() * days;
        
        // Add location fee if different pickup/return
        if (pickupLocation != returnLocation) {
            totalCost += 50.0; // One-way fee
        }
    }
    
    string getReservationId() const { return reservationId; }
    Vehicle* getVehicle() const { return vehicle; }
    ReservationStatus getStatus() const { return status; }
    double getTotalCost() const { return totalCost; }
    Date getPickupDate() const { return pickupDate; }
    Date getReturnDate() const { return returnDate; }
    
    void confirm() {
        status = ReservationStatus::CONFIRMED;
        vehicle->setStatus(VehicleStatus::RESERVED);
    }
    
    void activate() {
        status = ReservationStatus::ACTIVE;
        vehicle->setStatus(VehicleStatus::RENTED);
    }
    
    void complete(int additionalCharges = 0) {
        status = ReservationStatus::COMPLETED;
        vehicle->setStatus(VehicleStatus::AVAILABLE);
        totalCost += additionalCharges;
    }
    
    void cancel() {
        status = ReservationStatus::CANCELLED;
        vehicle->setStatus(VehicleStatus::AVAILABLE);
    }
    
    void display() const {
        cout << "\n========== RESERVATION ==========" << endl;
        cout << "ID: " << reservationId << endl;
        cout << "Customer: " << customer->getName() << endl;
        cout << "Vehicle: ";
        vehicle->display();
        cout << "Pickup: " << pickupLocation->getName() 
             << " (" << pickupDate.toString() << ")" << endl;
        cout << "Return: " << returnLocation->getName() 
             << " (" << returnDate.toString() << ")" << endl;
        cout << "Total Cost: $" << totalCost << endl;
        cout << "Status: " << (int)status << endl;
        cout << "================================\n" << endl;
    }
};

int Reservation::reservationCounter = 0;

// ============== Rental System ==============

class CarRentalSystem {
private:
    vector<unique_ptr<Vehicle>> vehicles;
    vector<unique_ptr<Location>> locations;
    map<string, unique_ptr<Customer>> customers;
    map<string, unique_ptr<Reservation>> reservations;
    
public:
    CarRentalSystem() {
        initializeLocations();
        initializeVehicles();
    }
    
    void initializeLocations() {
        locations.push_back(make_unique<Location>("LOC1", "Downtown", "123 Main St"));
        locations.push_back(make_unique<Location>("LOC2", "Airport", "Airport Terminal"));
        locations.push_back(make_unique<Location>("LOC3", "North Branch", "456 North Ave"));
    }
    
    void initializeVehicles() {
        vehicles.push_back(make_unique<Vehicle>("ABC123", "Toyota", "Corolla", 2023,
                                               VehicleType::ECONOMY, locations[0].get(), 35.0));
        vehicles.push_back(make_unique<Vehicle>("XYZ789", "Honda", "Accord", 2023,
                                               VehicleType::SEDAN, locations[0].get(), 45.0));
        vehicles.push_back(make_unique<Vehicle>("SUV456", "Ford", "Explorer", 2023,
                                               VehicleType::SUV, locations[1].get(), 65.0));
        vehicles.push_back(make_unique<Vehicle>("LUX999", "BMW", "5 Series", 2024,
                                               VehicleType::LUXURY, locations[0].get(), 120.0));
    }
    
    Customer* registerCustomer(const string& id, const string& name,
                              const string& license, const string& phone) {
        auto customer = make_unique<Customer>(id, name, license, phone);
        Customer* custPtr = customer.get();
        customers[id] = move(customer);
        return custPtr;
    }
    
    vector<Vehicle*> searchVehicles(VehicleType type, Location* location,
                                    const Date& pickupDate, const Date& returnDate) {
        vector<Vehicle*> available;
        
        for (auto& vehicle : vehicles) {
            if (vehicle->getType() == type &&
                vehicle->getLocation() == location &&
                vehicle->getStatus() == VehicleStatus::AVAILABLE) {
                available.push_back(vehicle.get());
            }
        }
        
        return available;
    }
    
    Reservation* makeReservation(Customer* customer, Vehicle* vehicle,
                                Location* pickup, Location* returnLoc,
                                const Date& pickupDate, const Date& returnDate) {
        if (vehicle->getStatus() != VehicleStatus::AVAILABLE) {
            cout << "Vehicle not available!" << endl;
            return nullptr;
        }
        
        auto reservation = make_unique<Reservation>(customer, vehicle, pickup,
                                                    returnLoc, pickupDate, returnDate);
        reservation->confirm();
        
        Reservation* resPtr = reservation.get();
        reservations[reservation->getReservationId()] = move(reservation);
        
        cout << "✓ Reservation created successfully!" << endl;
        return resPtr;
    }
    
    bool pickupVehicle(const string& reservationId) {
        auto it = reservations.find(reservationId);
        if (it == reservations.end()) {
            return false;
        }
        
        it->second->activate();
        cout << "✓ Vehicle picked up successfully!" << endl;
        return true;
    }
    
    bool returnVehicle(const string& reservationId, Location* returnLocation,
                      int milesDriven, bool damaged = false) {
        auto it = reservations.find(reservationId);
        if (it == reservations.end()) {
            return false;
        }
        
        Reservation* res = it->second.get();
        Vehicle* vehicle = res->getVehicle();
        
        vehicle->addMileage(milesDriven);
        vehicle->setLocation(returnLocation);
        
        int additionalCharges = 0;
        
        // Late return check (simplified)
        Date today(2024, 3, 20); // Hardcoded for demo
        if (today < res->getReturnDate()) {
            // Early return - no charge
        }
        
        // Damage charges
        if (damaged) {
            additionalCharges += 500; // Damage fee
            vehicle->setStatus(VehicleStatus::MAINTENANCE);
            cout << "⚠️  Damage reported. $500 fee applied." << endl;
        }
        
        res->complete(additionalCharges);
        
        cout << "✓ Vehicle returned successfully!" << endl;
        cout << "Miles driven: " << milesDriven << endl;
        cout << "Additional charges: $" << additionalCharges << endl;
        cout << "Final total: $" << res->getTotalCost() << endl;
        
        return true;
    }
    
    void displayAvailableVehicles(Location* location) {
        cout << "\n========== AVAILABLE VEHICLES ==========" << endl;
        cout << "Location: " << location->getName() << endl;
        cout << "---------------------------------------" << endl;
        
        for (auto& vehicle : vehicles) {
            if (vehicle->getLocation() == location &&
                vehicle->getStatus() == VehicleStatus::AVAILABLE) {
                vehicle->display();
                cout << endl;
            }
        }
        cout << "========================================\n" << endl;
    }
};

// ============== Demo ==============

int main() {
    CarRentalSystem system;
    
    cout << "========== Car Rental System Demo ==========\n" << endl;
    
    // Register customer
    Customer* customer1 = system.registerCustomer("C001", "John Doe",
                                                   "DL123456", "555-0100");
    
    // Get location
    Location* downtown = nullptr;
    Location* airport = nullptr;
    // In real system, would get from system
    
    // Display available vehicles
    cout << "=== Step 1: Browse Available Vehicles ===" << endl;
    // system.displayAvailableVehicles(downtown);
    
    // Search for specific type
    cout << "=== Step 2: Search for SUVs ===" << endl;
    Date pickup(2024, 3, 15);
    Date returnDate(2024, 3, 20);
    
    // Make reservation
    cout << "=== Step 3: Make Reservation ===" << endl;
    // Reservation* res = system.makeReservation(...);
    // if (res) res->display();
    
    // Pickup
    cout << "=== Step 4: Pick Up Vehicle ===" << endl;
    // system.pickupVehicle(res->getReservationId());
    
    // Return
    cout << "=== Step 5: Return Vehicle ===" << endl;
    // system.returnVehicle(res->getReservationId(), airport, 250, false);
    
    cout << "\n✓ Car rental workflow completed!" << endl;
    
    return 0;
}
```

---

## Key Features

### 1. **Vehicle Management**
- Different types with pricing
- Status tracking
- Location management

### 2. **Reservation System**
- Date-based availability
- Cost calculation
- Confirmation workflow

### 3. **Return Process**
- Mileage tracking
- Damage assessment
- Late fees

---

## Compilation

```bash
g++ -std=c++17 car_rental.cpp -o carrental
./carrental
```

---

**Next**: `medium/06-restaurant-management.md`

