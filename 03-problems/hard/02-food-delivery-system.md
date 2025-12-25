# Problem 2: Food Delivery System

**Difficulty**: Hard  
**Time to Solve**: 70-90 minutes  
**Companies**: Uber Eats, DoorDash, Zomato, Swiggy

## Problem Statement

Design a food delivery system that supports:
1. Restaurant management with menu
2. Order placement and tracking
3. Delivery partner assignment
4. Real-time location tracking
5. Dynamic pricing and surge
6. Restaurant ratings and reviews

---

## Class Diagram

```
┌────────────────────────┐
│  FoodDeliverySystem    │
├────────────────────────┤
│ - restaurants          │
│ - customers            │
│ - deliveryPartners     │
│ - orders               │
│ - matchingAlgorithm    │
├────────────────────────┤
│ + placeOrder()         │
│ + assignDelivery()     │
│ + trackOrder()         │
│ + updateLocation()     │
│ + calculatePrice()     │
└──────┬─────────────────┘
       │
   ┌───┴────┬────────┬──────────┐
   ▼        ▼        ▼          ▼
┌──────┐┌────────┐┌───────┐┌─────────┐
│ Rest ││Customer││ Order ││Delivery │
│aurant││        ││       ││Partner  │
├──────┤├────────┤├───────┤├─────────┤
│-menu ││-orders ││-items ││-location│
│-rating│-location│-status││-status  │
└──────┘└────────┘└───────┘└─────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <map>
#include <memory>
#include <string>
#include <cmath>
#include <algorithm>
#include <queue>
#include <ctime>

using namespace std;

// ============== Location ==============

struct Location {
    double latitude;
    double longitude;
    
    Location(double lat = 0, double lon = 0) : latitude(lat), longitude(lon) {}
    
    double distanceTo(const Location& other) const {
        // Simplified Euclidean distance (in real system use Haversine)
        double dx = (latitude - other.latitude) * 111; // ~111 km per degree
        double dy = (longitude - other.longitude) * 111;
        return sqrt(dx * dx + dy * dy);
    }
};

// ============== Enums ==============

enum class OrderStatus {
    PENDING,
    ACCEPTED,
    PREPARING,
    READY_FOR_PICKUP,
    PICKED_UP,
    IN_TRANSIT,
    DELIVERED,
    CANCELLED
};

enum class PartnerStatus {
    AVAILABLE,
    BUSY,
    OFFLINE
};

// ============== Menu Item ==============

class MenuItem {
private:
    string itemId;
    string name;
    string description;
    double price;
    bool isAvailable;
    string category;
    
public:
    MenuItem(const string& id, const string& n, double p, const string& cat)
        : itemId(id), name(n), price(p), category(cat), isAvailable(true) {}
    
    string getId() const { return itemId; }
    string getName() const { return name; }
    double getPrice() const { return price; }
    bool available() const { return isAvailable; }
    
    void setAvailable(bool status) { isAvailable = status; }
    
    void display() const {
        cout << "  " << name << " - $" << price;
        if (!isAvailable) cout << " [OUT OF STOCK]";
        cout << endl;
    }
};

// ============== Restaurant ==============

class Restaurant {
private:
    string restaurantId;
    string name;
    Location location;
    map<string, unique_ptr<MenuItem>> menu;
    double rating;
    int totalRatings;
    bool isOpen;
    
public:
    Restaurant(const string& id, const string& n, const Location& loc)
        : restaurantId(id), name(n), location(loc), rating(0), totalRatings(0), isOpen(true) {}
    
    string getId() const { return restaurantId; }
    string getName() const { return name; }
    Location getLocation() const { return location; }
    double getRating() const { return rating; }
    bool open() const { return isOpen; }
    
    void addMenuItem(unique_ptr<MenuItem> item) {
        string id = item->getId();
        menu[id] = move(item);
    }
    
    MenuItem* getMenuItem(const string& itemId) {
        auto it = menu.find(itemId);
        return (it != menu.end()) ? it->second.get() : nullptr;
    }
    
    void addRating(int stars) {
        if (stars >= 1 && stars <= 5) {
            rating = (rating * totalRatings + stars) / (totalRatings + 1.0);
            totalRatings++;
        }
    }
    
    void displayMenu() const {
        cout << "\n========== " << name << " ==========" << endl;
        cout << "⭐ Rating: " << rating << "/5.0 (" << totalRatings << " ratings)" << endl;
        cout << "Location: (" << location.latitude << ", " << location.longitude << ")" << endl;
        cout << "Menu:" << endl;
        
        for (const auto& [id, item] : menu) {
            item->display();
        }
        cout << "==========================================\n" << endl;
    }
};

// ============== Order Item ==============

class OrderItem {
private:
    MenuItem* item;
    int quantity;
    
public:
    OrderItem(MenuItem* i, int q) : item(i), quantity(q) {}
    
    MenuItem* getItem() const { return item; }
    int getQuantity() const { return quantity; }
    
    double getSubtotal() const {
        return item->getPrice() * quantity;
    }
    
    void display() const {
        cout << "  " << item->getName() << " x" << quantity
             << " = $" << getSubtotal() << endl;
    }
};

// ============== Customer ==============

class Customer {
private:
    string customerId;
    string name;
    string phone;
    Location location;
    vector<string> orderHistory;
    
public:
    Customer(const string& id, const string& n, const string& p, const Location& loc)
        : customerId(id), name(n), phone(p), location(loc) {}
    
    string getId() const { return customerId; }
    string getName() const { return name; }
    Location getLocation() const { return location; }
    
    void addOrderToHistory(const string& orderId) {
        orderHistory.push_back(orderId);
    }
};

// ============== Delivery Partner ==============

class DeliveryPartner {
private:
    string partnerId;
    string name;
    string phone;
    Location currentLocation;
    PartnerStatus status;
    int totalDeliveries;
    double rating;
    
public:
    DeliveryPartner(const string& id, const string& n, const string& p, const Location& loc)
        : partnerId(id), name(n), phone(p), currentLocation(loc),
          status(PartnerStatus::AVAILABLE), totalDeliveries(0), rating(5.0) {}
    
    string getId() const { return partnerId; }
    string getName() const { return name; }
    Location getLocation() const { return currentLocation; }
    PartnerStatus getStatus() const { return status; }
    double getRating() const { return rating; }
    
    void setLocation(const Location& loc) {
        currentLocation = loc;
    }
    
    void setStatus(PartnerStatus s) {
        status = s;
    }
    
    void completeDelivery() {
        totalDeliveries++;
        status = PartnerStatus::AVAILABLE;
    }
    
    void displayInfo() const {
        cout << "Partner: " << name << " | Status: "
             << (status == PartnerStatus::AVAILABLE ? "Available" : "Busy")
             << " | Rating: " << rating << endl;
    }
};

// ============== Order ==============

class Order {
private:
    string orderId;
    Customer* customer;
    Restaurant* restaurant;
    vector<OrderItem> items;
    DeliveryPartner* deliveryPartner;
    OrderStatus status;
    double itemTotal;
    double deliveryFee;
    double totalAmount;
    time_t orderTime;
    time_t deliveryTime;
    static int orderCounter;
    
public:
    Order(Customer* c, Restaurant* r)
        : customer(c), restaurant(r), deliveryPartner(nullptr),
          status(OrderStatus::PENDING), itemTotal(0), deliveryFee(0),
          totalAmount(0), orderTime(time(nullptr)), deliveryTime(0) {
        orderId = "ORD" + to_string(++orderCounter);
    }
    
    string getId() const { return orderId; }
    Customer* getCustomer() const { return customer; }
    Restaurant* getRestaurant() const { return restaurant; }
    OrderStatus getStatus() const { return status; }
    Location getDeliveryLocation() const { return customer->getLocation(); }
    
    void addItem(MenuItem* item, int quantity) {
        items.emplace_back(item, quantity);
        itemTotal += item->getPrice() * quantity;
    }
    
    void calculateTotal() {
        // Calculate delivery fee based on distance
        double distance = restaurant->getLocation().distanceTo(customer->getLocation());
        deliveryFee = 2.0 + (distance * 0.5); // Base + per km
        
        // Apply surge pricing during peak hours (simplified)
        struct tm* timeinfo = localtime(&orderTime);
        if (timeinfo->tm_hour >= 18 && timeinfo->tm_hour <= 21) {
            deliveryFee *= 1.5; // 50% surge
        }
        
        totalAmount = itemTotal + deliveryFee;
    }
    
    void setDeliveryPartner(DeliveryPartner* partner) {
        deliveryPartner = partner;
        partner->setStatus(PartnerStatus::BUSY);
    }
    
    void updateStatus(OrderStatus newStatus) {
        status = newStatus;
        
        if (status == OrderStatus::DELIVERED) {
            deliveryTime = time(nullptr);
            if (deliveryPartner) {
                deliveryPartner->completeDelivery();
            }
        }
    }
    
    void display() const {
        cout << "\n========== ORDER " << orderId << " ==========" << endl;
        cout << "Customer: " << customer->getName() << endl;
        cout << "Restaurant: " << restaurant->getName() << endl;
        cout << "Status: " << (int)status << endl;
        cout << "-----------------------------------" << endl;
        cout << "Items:" << endl;
        
        for (const auto& item : items) {
            item.display();
        }
        
        cout << "-----------------------------------" << endl;
        cout << "Item Total: $" << itemTotal << endl;
        cout << "Delivery Fee: $" << deliveryFee << endl;
        cout << "Total Amount: $" << totalAmount << endl;
        
        if (deliveryPartner) {
            cout << "Delivery Partner: " << deliveryPartner->getName() << endl;
        }
        
        cout << "========================================\n" << endl;
    }
};

int Order::orderCounter = 0;

// ============== Delivery Matching ==============

class DeliveryMatcher {
public:
    static DeliveryPartner* findBestPartner(
        const vector<DeliveryPartner*>& partners,
        const Location& restaurantLoc) {
        
        DeliveryPartner* best = nullptr;
        double minDistance = 1e9;
        
        for (DeliveryPartner* partner : partners) {
            if (partner->getStatus() == PartnerStatus::AVAILABLE) {
                double distance = partner->getLocation().distanceTo(restaurantLoc);
                
                if (distance < minDistance) {
                    minDistance = distance;
                    best = partner;
                }
            }
        }
        
        return best;
    }
};

// ============== Food Delivery System ==============

class FoodDeliverySystem {
private:
    map<string, unique_ptr<Restaurant>> restaurants;
    map<string, unique_ptr<Customer>> customers;
    map<string, unique_ptr<DeliveryPartner>> deliveryPartners;
    map<string, unique_ptr<Order>> orders;
    
public:
    Restaurant* addRestaurant(const string& id, const string& name, const Location& loc) {
        auto restaurant = make_unique<Restaurant>(id, name, loc);
        Restaurant* ptr = restaurant.get();
        restaurants[id] = move(restaurant);
        cout << "✓ Restaurant added: " << name << endl;
        return ptr;
    }
    
    Customer* registerCustomer(const string& id, const string& name,
                              const string& phone, const Location& loc) {
        auto customer = make_unique<Customer>(id, name, phone, loc);
        Customer* ptr = customer.get();
        customers[id] = move(customer);
        cout << "✓ Customer registered: " << name << endl;
        return ptr;
    }
    
    DeliveryPartner* registerPartner(const string& id, const string& name,
                                    const string& phone, const Location& loc) {
        auto partner = make_unique<DeliveryPartner>(id, name, phone, loc);
        DeliveryPartner* ptr = partner.get();
        deliveryPartners[id] = move(partner);
        cout << "✓ Delivery partner registered: " << name << endl;
        return ptr;
    }
    
    Order* placeOrder(Customer* customer, Restaurant* restaurant,
                     const vector<pair<string, int>>& items) {
        
        if (!restaurant->open()) {
            cout << "Restaurant is closed!" << endl;
            return nullptr;
        }
        
        auto order = make_unique<Order>(customer, restaurant);
        
        // Add items
        bool allAvailable = true;
        for (const auto& [itemId, quantity] : items) {
            MenuItem* item = restaurant->getMenuItem(itemId);
            if (item && item->available()) {
                order->addItem(item, quantity);
            } else {
                allAvailable = false;
                cout << "Item " << itemId << " not available" << endl;
            }
        }
        
        if (!allAvailable) {
            cout << "Some items unavailable. Order cancelled." << endl;
            return nullptr;
        }
        
        order->calculateTotal();
        
        // Find delivery partner
        vector<DeliveryPartner*> availablePartners;
        for (const auto& [id, partner] : deliveryPartners) {
            availablePartners.push_back(partner.get());
        }
        
        DeliveryPartner* partner = DeliveryMatcher::findBestPartner(
            availablePartners, restaurant->getLocation());
        
        if (!partner) {
            cout << "No delivery partners available!" << endl;
            return nullptr;
        }
        
        order->setDeliveryPartner(partner);
        order->updateStatus(OrderStatus::ACCEPTED);
        
        Order* orderPtr = order.get();
        string orderId = order->getId();
        orders[orderId] = move(order);
        customer->addOrderToHistory(orderId);
        
        cout << "✓ Order placed successfully!" << endl;
        return orderPtr;
    }
    
    void updateOrderStatus(const string& orderId, OrderStatus status) {
        auto it = orders.find(orderId);
        if (it != orders.end()) {
            it->second->updateStatus(status);
            cout << "✓ Order " << orderId << " updated to status " << (int)status << endl;
        }
    }
    
    vector<Restaurant*> findNearbyRestaurants(const Location& customerLoc, double maxDistance) {
        vector<Restaurant*> nearby;
        
        for (const auto& [id, restaurant] : restaurants) {
            double distance = restaurant->getLocation().distanceTo(customerLoc);
            if (distance <= maxDistance && restaurant->open()) {
                nearby.push_back(restaurant.get());
            }
        }
        
        // Sort by rating
        sort(nearby.begin(), nearby.end(), [](Restaurant* a, Restaurant* b) {
            return a->getRating() > b->getRating();
        });
        
        return nearby;
    }
    
    void displayAvailablePartners() const {
        cout << "\n========== Available Delivery Partners ==========" << endl;
        for (const auto& [id, partner] : deliveryPartners) {
            partner->displayInfo();
        }
        cout << "================================================\n" << endl;
    }
};

// ============== Demo ==============

int main() {
    FoodDeliverySystem system;
    
    cout << "========== Food Delivery System Demo ==========\n" << endl;
    
    // Add restaurants
    cout << "=== Setting Up Restaurants ===" << endl;
    Restaurant* pizzaPlace = system.addRestaurant("R001", "Pizza Palace",
                                                   Location(40.7128, -74.0060));
    Restaurant* burgerJoint = system.addRestaurant("R002", "Burger Joint",
                                                    Location(40.7180, -74.0100));
    
    // Add menu items
    pizzaPlace->addMenuItem(make_unique<MenuItem>("I001", "Margherita Pizza", 12.99, "Pizza"));
    pizzaPlace->addMenuItem(make_unique<MenuItem>("I002", "Pepperoni Pizza", 14.99, "Pizza"));
    pizzaPlace->addMenuItem(make_unique<MenuItem>("I003", "Garlic Bread", 5.99, "Sides"));
    
    burgerJoint->addMenuItem(make_unique<MenuItem>("I004", "Classic Burger", 8.99, "Burger"));
    burgerJoint->addMenuItem(make_unique<MenuItem>("I005", "Cheese Burger", 9.99, "Burger"));
    
    pizzaPlace->addRating(5);
    pizzaPlace->addRating(4);
    burgerJoint->addRating(5);
    
    pizzaPlace->displayMenu();
    
    // Register customers
    cout << "=== Registering Customers ===" << endl;
    Customer* alice = system.registerCustomer("C001", "Alice", "555-0001",
                                              Location(40.7200, -74.0080));
    
    // Register delivery partners
    cout << "\n=== Registering Delivery Partners ===" << endl;
    DeliveryPartner* partner1 = system.registerPartner("D001", "John Driver",
                                                       "555-1001",
                                                       Location(40.7150, -74.0070));
    DeliveryPartner* partner2 = system.registerPartner("D002", "Jane Rider",
                                                       "555-1002",
                                                       Location(40.7100, -74.0050));
    
    system.displayAvailablePartners();
    
    // Place order
    cout << "=== Placing Order ===" << endl;
    vector<pair<string, int>> items = {{"I001", 2}, {"I003", 1}};
    Order* order = system.placeOrder(alice, pizzaPlace, items);
    
    if (order) {
        order->display();
        
        // Simulate order lifecycle
        cout << "=== Order Lifecycle ===" << endl;
        system.updateOrderStatus(order->getId(), OrderStatus::PREPARING);
        system.updateOrderStatus(order->getId(), OrderStatus::READY_FOR_PICKUP);
        system.updateOrderStatus(order->getId(), OrderStatus::PICKED_UP);
        system.updateOrderStatus(order->getId(), OrderStatus::IN_TRANSIT);
        system.updateOrderStatus(order->getId(), OrderStatus::DELIVERED);
        
        cout << "\n=== Final Order Status ===" << endl;
        order->display();
    }
    
    system.displayAvailablePartners();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Delivery Matching Algorithm**
- Distance-based partner assignment
- Real-time availability tracking
- Optimized for quick pickup

### 2. **Dynamic Pricing**
- Distance-based delivery fees
- Surge pricing during peak hours
- Restaurant-specific pricing

### 3. **Order Lifecycle**
- Multiple status transitions
- Real-time tracking
- Partner availability management

---

## Follow-up Questions

**Q1: How to handle multiple concurrent orders?**
```cpp
class OrderQueue {
    priority_queue<Order*, vector<Order*>, OrderComparator> pending;
    mutex queueMutex;
    
    void assignOrders();
};
```

**Q2: How to optimize delivery routes?**
```cpp
class RouteOptimizer {
    vector<Order*> batchOrders(DeliveryPartner* partner);
    double calculateOptimalRoute(vector<Location>& stops);
};
```

**Q3: How to implement real-time tracking?**
```cpp
class LocationTracker {
    map<string, Location> partnerLocations;
    void updateLocation(string partnerId, Location loc);
    void notifyCustomer(Order* order);
};
```

---

## Compilation

```bash
g++ -std=c++17 food_delivery.cpp -o delivery
./delivery
```

---

**Next**: `hard/03-stock-trading.md`

