# Problem 1: Ride Sharing System (Uber/Lyft)

**Difficulty**: Hard  
**Time to Solve**: 60-90 minutes  
**Companies**: Uber, Lyft, Ola, DoorDash

## Problem Statement

Design a ride-sharing system like Uber/Lyft that supports:
1. Multiple rider and driver matching
2. Real-time location tracking
3. Different ride types (Economy, Premium, Pool)
4. Dynamic pricing (surge pricing)
5. Trip management (request, accept, start, complete)
6. Rating system
7. Payment processing
8. Driver availability and status

### Requirements

**Functional Requirements**:
- User registration (Rider, Driver)
- Request ride with pickup and destination
- Match driver to rider based on proximity and availability
- Support multiple ride types
- Track trip status (Requested, Accepted, InProgress, Completed)
- Calculate fare with dynamic pricing
- Rating and reviews
- Payment processing
- Trip history

**Non-Functional Requirements**:
- Low latency for matching (<5 seconds)
- Handle concurrent requests
- Scalable (millions of users)
- Real-time location updates
- High availability
- Data consistency

---

## Concepts Involved

1. **Design Patterns**:
   - **Strategy Pattern** (Pricing, Matching algorithms)
   - **Observer Pattern** (Location updates, notifications)
   - **State Pattern** (Trip states)
   - **Factory Pattern** (Ride creation)
   - **Singleton** (System controller)
2. **Algorithms**: 
   - Geospatial matching (K-D tree, Quadtree)
   - Distance calculation (Haversine formula)
   - Surge pricing algorithm
3. **Concurrency**: Thread-safe matching
4. **SOLID Principles**: All five

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                 RideShareSystem                         │
├─────────────────────────────────────────────────────────┤
│  UserService  │ TripService │ PaymentService │ Location │
│               │             │                │ Service  │
└───────┬───────┴──────┬──────┴────────┬───────┴────┬─────┘
        │              │               │            │
        ▼              ▼               ▼            ▼
┌─────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────┐
│   Rider     │ │   Driver     │ │   Trip   │ │ Location │
│   Driver    │ │   Matching   │ │   State  │ │ Tracker  │
└─────────────┘ └──────────────┘ └──────────┘ └──────────┘
```

---

## Detailed Class Diagram

```
┌──────────────────┐
│      User        │ ◄───── Abstract
├──────────────────┤
│ - id: string     │
│ - name: string   │
│ - phone: string  │
│ - rating: double │
├──────────────────┤
│ + getProfile()   │
└────────┬─────────┘
         │
    ┌────┴────┬─────────┐
    ▼         ▼         ▼
┌────────┐┌────────┐┌────────┐
│ Rider  ││ Driver ││ Admin  │
└────────┘└────────┘└────────┘

┌──────────────────────┐
│    Location          │
├──────────────────────┤
│ - latitude: double   │
│ - longitude: double  │
│ - timestamp: time_t  │
├──────────────────────┤
│ + distanceTo(loc)    │
└──────────────────────┘

┌──────────────────────┐
│      Trip            │
├──────────────────────┤
│ - tripId: string     │
│ - rider: Rider*      │
│ - driver: Driver*    │
│ - pickup: Location   │
│ - destination: Loc   │
│ - rideType: enum     │
│ - status: TripStatus │
│ - fare: double       │
│ - startTime: time_t  │
│ - endTime: time_t    │
├──────────────────────┤
│ + accept()           │
│ + start()            │
│ + complete()         │
│ + cancel()           │
└──────────────────────┘

┌──────────────────────┐
│   PricingStrategy    │ ◄───── Strategy
├──────────────────────┤
│ + calculateFare()    │
└──────────┬───────────┘
           │
    ┌──────┴──────┬──────────┐
    ▼             ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Default │ │  Surge  │ │  Pool   │
│ Pricing │ │ Pricing │ │ Pricing │
└─────────┘ └─────────┘ └─────────┘

┌──────────────────────┐
│   MatchingStrategy   │ ◄───── Strategy
├──────────────────────┤
│ + findDriver()       │
└──────────┬───────────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌─────────┐ ┌─────────┐
│Nearest  │ │  Best   │
│ Driver  │ │ Rated   │
└─────────┘ └─────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <cmath>
#include <ctime>
#include <mutex>
#include <queue>
#include <iomanip>
#include <random>

using namespace std;

// ============== Enums ==============

enum class UserType {
    RIDER,
    DRIVER,
    ADMIN
};

enum class DriverStatus {
    AVAILABLE,
    BUSY,
    OFFLINE
};

enum class TripStatus {
    REQUESTED,
    ACCEPTED,
    ARRIVED,
    IN_PROGRESS,
    COMPLETED,
    CANCELLED
};

enum class RideType {
    ECONOMY,
    PREMIUM,
    POOL,
    XL
};

enum class PaymentStatus {
    PENDING,
    COMPLETED,
    FAILED,
    REFUNDED
};

// ============== Location ==============

class Location {
private:
    double latitude;
    double longitude;
    time_t timestamp;
    
public:
    Location(double lat = 0, double lon = 0) 
        : latitude(lat), longitude(lon), timestamp(time(nullptr)) {}
    
    double getLatitude() const { return latitude; }
    double getLongitude() const { return longitude; }
    
    // Haversine formula for distance calculation
    double distanceTo(const Location& other) const {
        const double R = 6371.0; // Earth radius in km
        
        double lat1 = latitude * M_PI / 180.0;
        double lat2 = other.latitude * M_PI / 180.0;
        double dLat = (other.latitude - latitude) * M_PI / 180.0;
        double dLon = (other.longitude - longitude) * M_PI / 180.0;
        
        double a = sin(dLat/2) * sin(dLat/2) +
                   cos(lat1) * cos(lat2) *
                   sin(dLon/2) * sin(dLon/2);
        double c = 2 * atan2(sqrt(a), sqrt(1-a));
        
        return R * c;
    }
    
    void display() const {
        cout << "(" << fixed << setprecision(4) 
             << latitude << ", " << longitude << ")";
    }
};

// ============== Rating ==============

class Rating {
private:
    int totalRides;
    double averageRating;
    
public:
    Rating() : totalRides(0), averageRating(5.0) {}
    
    void addRating(double rating) {
        averageRating = ((averageRating * totalRides) + rating) / (totalRides + 1);
        totalRides++;
    }
    
    double getAverage() const { return averageRating; }
    int getTotalRides() const { return totalRides; }
};

// ============== User Classes ==============

class User {
protected:
    string userId;
    string name;
    string phone;
    string email;
    Rating rating;
    
public:
    User(const string& id, const string& n, const string& p)
        : userId(id), name(n), phone(p) {}
    
    virtual ~User() = default;
    
    string getUserId() const { return userId; }
    string getName() const { return name; }
    double getRating() const { return rating.getAverage(); }
    
    void addRating(double r) { rating.addRating(r); }
    
    virtual void displayProfile() const {
        cout << "ID: " << userId << " | Name: " << name 
             << " | Rating: " << fixed << setprecision(2) 
             << rating.getAverage() << " (" << rating.getTotalRides() << " rides)" 
             << endl;
    }
};

class Rider : public User {
private:
    vector<string> paymentMethods;
    
public:
    Rider(const string& id, const string& name, const string& phone)
        : User(id, name, phone) {}
    
    void displayProfile() const override {
        cout << "[RIDER] ";
        User::displayProfile();
    }
};

class Driver : public User {
private:
    string vehicleNumber;
    string vehicleModel;
    RideType vehicleType;
    DriverStatus status;
    Location currentLocation;
    
public:
    Driver(const string& id, const string& name, const string& phone,
           const string& vehicle, RideType type)
        : User(id, name, phone), vehicleNumber(vehicle), 
          vehicleType(type), status(DriverStatus::OFFLINE) {}
    
    DriverStatus getStatus() const { return status; }
    void setStatus(DriverStatus s) { status = s; }
    
    Location getCurrentLocation() const { return currentLocation; }
    void updateLocation(const Location& loc) { currentLocation = loc; }
    
    RideType getVehicleType() const { return vehicleType; }
    string getVehicleNumber() const { return vehicleNumber; }
    
    void displayProfile() const override {
        cout << "[DRIVER] ";
        User::displayProfile();
        cout << "  Vehicle: " << vehicleModel << " (" << vehicleNumber << ")"
             << " | Status: " << (int)status << endl;
    }
};

// ============== Pricing Strategy ==============

class PricingStrategy {
protected:
    double baseFare;
    double perKmRate;
    double perMinRate;
    
public:
    PricingStrategy(double base, double km, double min)
        : baseFare(base), perKmRate(km), perMinRate(min) {}
    
    virtual ~PricingStrategy() = default;
    
    virtual double calculateFare(double distance, double duration) {
        return baseFare + (distance * perKmRate) + (duration * perMinRate);
    }
    
    virtual string getStrategyName() const = 0;
};

class EconomyPricing : public PricingStrategy {
public:
    EconomyPricing() : PricingStrategy(50.0, 10.0, 2.0) {}
    string getStrategyName() const override { return "Economy"; }
};

class PremiumPricing : public PricingStrategy {
public:
    PremiumPricing() : PricingStrategy(100.0, 20.0, 4.0) {}
    string getStrategyName() const override { return "Premium"; }
};

class SurgePricing : public PricingStrategy {
private:
    double surgeMultiplier;
    
public:
    SurgePricing(double base, double km, double min, double surge)
        : PricingStrategy(base, km, min), surgeMultiplier(surge) {}
    
    double calculateFare(double distance, double duration) override {
        double baseFare = PricingStrategy::calculateFare(distance, duration);
        return baseFare * surgeMultiplier;
    }
    
    string getStrategyName() const override { 
        return "Surge (" + to_string(surgeMultiplier) + "x)"; 
    }
};

// ============== Trip ==============

class Trip {
private:
    string tripId;
    Rider* rider;
    Driver* driver;
    Location pickupLocation;
    Location destinationLocation;
    RideType rideType;
    TripStatus status;
    
    unique_ptr<PricingStrategy> pricingStrategy;
    
    time_t requestTime;
    time_t acceptTime;
    time_t startTime;
    time_t endTime;
    
    double fare;
    double distance;
    
    static int tripCounter;
    
    string generateTripId() {
        return "TRIP" + to_string(++tripCounter);
    }
    
public:
    Trip(Rider* r, const Location& pickup, const Location& dest, RideType type)
        : rider(r), driver(nullptr), pickupLocation(pickup), 
          destinationLocation(dest), rideType(type), 
          status(TripStatus::REQUESTED), fare(0), distance(0) {
        
        tripId = generateTripId();
        requestTime = time(nullptr);
        
        // Set pricing strategy
        if (type == RideType::ECONOMY) {
            pricingStrategy = make_unique<EconomyPricing>();
        } else {
            pricingStrategy = make_unique<PremiumPricing>();
        }
        
        distance = pickupLocation.distanceTo(destinationLocation);
    }
    
    string getTripId() const { return tripId; }
    Rider* getRider() const { return rider; }
    Driver* getDriver() const { return driver; }
    Location getPickupLocation() const { return pickupLocation; }
    TripStatus getStatus() const { return status; }
    RideType getRideType() const { return rideType; }
    
    bool assignDriver(Driver* d) {
        if (status != TripStatus::REQUESTED) {
            return false;
        }
        
        driver = d;
        status = TripStatus::ACCEPTED;
        acceptTime = time(nullptr);
        
        cout << "\n[TRIP " << tripId << "] Driver assigned: " 
             << driver->getName() << endl;
        return true;
    }
    
    void arrive() {
        if (status == TripStatus::ACCEPTED) {
            status = TripStatus::ARRIVED;
            cout << "[TRIP " << tripId << "] Driver arrived at pickup" << endl;
        }
    }
    
    void start() {
        if (status == TripStatus::ARRIVED || status == TripStatus::ACCEPTED) {
            status = TripStatus::IN_PROGRESS;
            startTime = time(nullptr);
            cout << "[TRIP " << tripId << "] Trip started" << endl;
        }
    }
    
    void complete() {
        if (status == TripStatus::IN_PROGRESS) {
            status = TripStatus::COMPLETED;
            endTime = time(nullptr);
            
            double duration = difftime(endTime, startTime) / 60.0; // minutes
            fare = pricingStrategy->calculateFare(distance, duration);
            
            cout << "\n[TRIP " << tripId << "] Trip completed!" << endl;
            displayReceipt();
            
            // Update driver status
            if (driver) {
                driver->setStatus(DriverStatus::AVAILABLE);
            }
        }
    }
    
    void cancel() {
        status = TripStatus::CANCELLED;
        cout << "[TRIP " << tripId << "] Trip cancelled" << endl;
        
        if (driver) {
            driver->setStatus(DriverStatus::AVAILABLE);
        }
    }
    
    void displayReceipt() const {
        cout << "\n========== TRIP RECEIPT ==========" << endl;
        cout << "Trip ID: " << tripId << endl;
        cout << "Rider: " << rider->getName() << endl;
        if (driver) {
            cout << "Driver: " << driver->getName() << endl;
            cout << "Vehicle: " << driver->getVehicleNumber() << endl;
        }
        cout << "Distance: " << fixed << setprecision(2) << distance << " km" << endl;
        cout << "Fare: $" << fare << endl;
        cout << "Pricing: " << pricingStrategy->getStrategyName() << endl;
        cout << "==================================\n" << endl;
    }
    
    double getFare() const { return fare; }
};

int Trip::tripCounter = 0;

// ============== Driver Matching Strategy ==============

class DriverMatchingStrategy {
public:
    virtual ~DriverMatchingStrategy() = default;
    virtual Driver* findDriver(const vector<Driver*>& availableDrivers, 
                              const Location& pickupLocation, 
                              RideType rideType) = 0;
};

class NearestDriverStrategy : public DriverMatchingStrategy {
public:
    Driver* findDriver(const vector<Driver*>& availableDrivers, 
                      const Location& pickupLocation, 
                      RideType rideType) override {
        Driver* nearest = nullptr;
        double minDistance = DBL_MAX;
        
        for (Driver* driver : availableDrivers) {
            if (driver->getStatus() != DriverStatus::AVAILABLE) {
                continue;
            }
            
            double distance = driver->getCurrentLocation().distanceTo(pickupLocation);
            
            if (distance < minDistance) {
                minDistance = distance;
                nearest = driver;
            }
        }
        
        return nearest;
    }
};

class HighestRatedDriverStrategy : public DriverMatchingStrategy {
public:
    Driver* findDriver(const vector<Driver*>& availableDrivers, 
                      const Location& pickupLocation, 
                      RideType rideType) override {
        Driver* bestRated = nullptr;
        double maxRating = 0.0;
        
        for (Driver* driver : availableDrivers) {
            if (driver->getStatus() != DriverStatus::AVAILABLE) {
                continue;
            }
            
            double distance = driver->getCurrentLocation().distanceTo(pickupLocation);
            
            // Only consider drivers within 5 km
            if (distance <= 5.0 && driver->getRating() > maxRating) {
                maxRating = driver->getRating();
                bestRated = driver;
            }
        }
        
        return bestRated;
    }
};

// ============== Ride Share System ==============

class RideShareSystem {
private:
    static RideShareSystem* instance;
    static mutex mtx;
    
    unordered_map<string, unique_ptr<Rider>> riders;
    unordered_map<string, unique_ptr<Driver>> drivers;
    unordered_map<string, unique_ptr<Trip>> trips;
    
    unique_ptr<DriverMatchingStrategy> matchingStrategy;
    
    RideShareSystem() {
        matchingStrategy = make_unique<NearestDriverStrategy>();
    }
    
public:
    static RideShareSystem* getInstance() {
        lock_guard<mutex> lock(mtx);
        if (instance == nullptr) {
            instance = new RideShareSystem();
        }
        return instance;
    }
    
    void registerRider(unique_ptr<Rider> rider) {
        lock_guard<mutex> lock(mtx);
        string id = rider->getUserId();
        riders[id] = move(rider);
        cout << "Rider registered: " << id << endl;
    }
    
    void registerDriver(unique_ptr<Driver> driver) {
        lock_guard<mutex> lock(mtx);
        string id = driver->getUserId();
        drivers[id] = move(driver);
        cout << "Driver registered: " << id << endl;
    }
    
    Trip* requestRide(const string& riderId, const Location& pickup, 
                      const Location& destination, RideType type) {
        lock_guard<mutex> lock(mtx);
        
        auto riderIt = riders.find(riderId);
        if (riderIt == riders.end()) {
            cout << "Rider not found!" << endl;
            return nullptr;
        }
        
        Rider* rider = riderIt->second.get();
        
        // Create trip
        auto trip = make_unique<Trip>(rider, pickup, destination, type);
        Trip* tripPtr = trip.get();
        
        cout << "\n[NEW RIDE REQUEST] " << trip->getTripId() << endl;
        cout << "Rider: " << rider->getName() << endl;
        cout << "Pickup: "; pickup.display(); cout << endl;
        cout << "Destination: "; destination.display(); cout << endl;
        
        // Find available driver
        vector<Driver*> availableDrivers;
        for (auto& [id, driver] : drivers) {
            if (driver->getStatus() == DriverStatus::AVAILABLE) {
                availableDrivers.push_back(driver.get());
            }
        }
        
        Driver* assignedDriver = matchingStrategy->findDriver(
            availableDrivers, pickup, type);
        
        if (assignedDriver) {
            trip->assignDriver(assignedDriver);
            assignedDriver->setStatus(DriverStatus::BUSY);
        } else {
            cout << "No drivers available!" << endl;
        }
        
        string tripId = trip->getTripId();
        trips[tripId] = move(trip);
        
        return tripPtr;
    }
    
    void startTrip(const string& tripId) {
        auto it = trips.find(tripId);
        if (it != trips.end()) {
            it->second->start();
        }
    }
    
    void completeTrip(const string& tripId) {
        auto it = trips.find(tripId);
        if (it != trips.end()) {
            it->second->complete();
        }
    }
    
    void displayAllDrivers() const {
        cout << "\n========== ALL DRIVERS ==========" << endl;
        for (const auto& [id, driver] : drivers) {
            driver->displayProfile();
        }
        cout << "=================================\n" << endl;
    }
    
    static void cleanup() {
        delete instance;
        instance = nullptr;
    }
};

RideShareSystem* RideShareSystem::instance = nullptr;
mutex RideShareSystem::mtx;

// ============== Demo ==============

int main() {
    RideShareSystem* system = RideShareSystem::getInstance();
    
    // Register riders
    system->registerRider(make_unique<Rider>("R001", "Alice", "1234567890"));
    system->registerRider(make_unique<Rider>("R002", "Bob", "0987654321"));
    
    // Register drivers
    auto driver1 = make_unique<Driver>("D001", "John Driver", "1111111111", 
                                       "ABC123", RideType::ECONOMY);
    driver1->setStatus(DriverStatus::AVAILABLE);
    driver1->updateLocation(Location(37.7749, -122.4194)); // San Francisco
    
    auto driver2 = make_unique<Driver>("D002", "Jane Driver", "2222222222", 
                                       "XYZ789", RideType::PREMIUM);
    driver2->setStatus(DriverStatus::AVAILABLE);
    driver2->updateLocation(Location(37.7849, -122.4094));
    
    system->registerDriver(move(driver1));
    system->registerDriver(move(driver2));
    
    system->displayAllDrivers();
    
    // Request rides
    Location pickup1(37.7750, -122.4195);
    Location dest1(37.7950, -122.4395);
    
    Trip* trip1 = system->requestRide("R001", pickup1, dest1, RideType::ECONOMY);
    
    if (trip1) {
        // Simulate trip flow
        this_thread::sleep_for(chrono::seconds(2));
        trip1->arrive();
        
        this_thread::sleep_for(chrono::seconds(1));
        trip1->start();
        
        this_thread::sleep_for(chrono::seconds(3));
        trip1->complete();
    }
    
    // Another ride
    Location pickup2(37.7850, -122.4095);
    Location dest2(37.8050, -122.4295);
    
    Trip* trip2 = system->requestRide("R002", pickup2, dest2, RideType::PREMIUM);
    
    if (trip2) {
        this_thread::sleep_for(chrono::seconds(1));
        trip2->start();
        
        this_thread::sleep_for(chrono::seconds(2));
        trip2->complete();
    }
    
    RideShareSystem::cleanup();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Matching Algorithm**
- Nearest driver for quick assignment
- Can switch to highest-rated for premium
- Consider traffic, driver acceptance rate

### 2. **Pricing Strategy**
- Base fare + distance + time
- Surge pricing during high demand
- Different rates for different ride types

### 3. **Scalability Considerations**
- Geospatial indexing (Quadtree) for large scale
- Sharding by geographic region
- Caching for frequent queries

### 4. **Real-time Updates**
- WebSocket for location tracking
- Observer pattern for status updates
- Push notifications

---

## Follow-up Questions

**Q1: How to implement ride pooling?**
- Match multiple riders with similar routes
- Optimize pickup/drop sequence
- Dynamic pricing based on detour

**Q2: How to handle surge pricing?**
- Monitor demand/supply ratio
- Real-time multiplier calculation
- Notify users of surge

**Q3: How to scale to millions of users?**
- Microservices architecture
- Geographic sharding
- Redis for session management
- Kafka for event streaming

**Q4: How to prevent fraudulent behavior?**
- Verify actual GPS locations
- Monitor abnormal patterns
- Multi-factor authentication
- Review system flags

**Q5: How to optimize driver earnings?**
- Heat map of high-demand areas
- Predictive algorithms
- Efficient routing
- Incentive programs

---

## System Design Extensions

### Database Schema
```sql
Users (user_id, name, phone, type, rating)
Drivers (driver_id, vehicle_id, status, current_lat, current_lon)
Trips (trip_id, rider_id, driver_id, status, pickup_lat, pickup_lon, 
       dest_lat, dest_lon, fare, start_time, end_time)
Payments (payment_id, trip_id, amount, status, method)
```

### APIs
```
POST /api/v1/riders/{riderId}/request-ride
GET  /api/v1/trips/{tripId}
PUT  /api/v1/trips/{tripId}/status
POST /api/v1/trips/{tripId}/payment
GET  /api/v1/drivers/nearby?lat=x&lon=y
```

---

## Compilation & Execution

```bash
g++ -std=c++17 -pthread ride_share.cpp -o rideshare
./rideshare
```

---

**This is the most complex problem in the course, demonstrating real-world system design at scale!**

