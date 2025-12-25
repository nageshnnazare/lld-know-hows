# Problem 6: Restaurant Management System

**Difficulty**: Medium  
**Time to Solve**: 45-55 minutes  
**Companies**: OpenTable, Resy, Yelp

## Problem Statement

Design a restaurant management system that supports:
1. Table management and reservations
2. Order placement and tracking
3. Menu management
4. Kitchen display system
5. Bill generation
6. Table status tracking

---

## Class Diagram

```
┌────────────────┐
│  Restaurant    │
├────────────────┤
│ - tables       │
│ - menu         │
│ - orders       │
├────────────────┤
│ + bookTable()  │
│ + placeOrder() │
│ +generateBill()│
└───────┬────────┘
        │
    ┌───┴────┬────────┬────────┐
    ▼        ▼        ▼        ▼
┌───────┐┌────────┐┌──────┐┌──────┐
│ Table ││MenuItem││Order ││ Bill │
└───────┘└────────┘└──────┘└──────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <map>
#include <memory>
#include <string>

using namespace std;

enum class TableStatus { AVAILABLE, RESERVED, OCCUPIED };
enum class OrderStatus { PLACED, PREPARING, READY, SERVED };

class MenuItem {
private:
    string id, name;
    double price;
    string category;
public:
    MenuItem(const string& i, const string& n, double p, const string& cat)
        : id(i), name(n), price(p), category(cat) {}
    string getId() const { return id; }
    string getName() const { return name; }
    double getPrice() const { return price; }
};

class Table {
private:
    int tableNumber;
    int capacity;
    TableStatus status;
public:
    Table(int num, int cap) : tableNumber(num), capacity(cap), status(TableStatus::AVAILABLE) {}
    int getNumber() const { return tableNumber; }
    int getCapacity() const { return capacity; }
    TableStatus getStatus() const { return status; }
    void setStatus(TableStatus s) { status = s; }
    bool isAvailable() const { return status == TableStatus::AVAILABLE; }
};

class Order {
private:
    string orderId;
    Table* table;
    vector<MenuItem*> items;
    OrderStatus status;
    double total;
    static int orderCounter;
public:
    Order(Table* t) : table(t), status(OrderStatus::PLACED), total(0) {
        orderId = "ORD" + to_string(++orderCounter);
    }
    void addItem(MenuItem* item) {
        items.push_back(item);
        total += item->getPrice();
    }
    string getOrderId() const { return orderId; }
    double getTotal() const { return total; }
    OrderStatus getStatus() const { return status; }
    void setStatus(OrderStatus s) { status = s; }
    void display() const {
        cout << "\nOrder " << orderId << " - Table " << table->getNumber() << endl;
        for (auto* item : items) {
            cout << "  " << item->getName() << " - $" << item->getPrice() << endl;
        }
        cout << "Total: $" << total << endl;
    }
};

int Order::orderCounter = 0;

class Restaurant {
private:
    string name;
    vector<unique_ptr<Table>> tables;
    vector<unique_ptr<MenuItem>> menu;
    map<string, unique_ptr<Order>> orders;
public:
    Restaurant(const string& n) : name(n) {
        // Initialize tables
        for (int i = 1; i <= 10; i++) {
            tables.push_back(make_unique<Table>(i, i <= 5 ? 2 : 4));
        }
        // Initialize menu
        menu.push_back(make_unique<MenuItem>("M1", "Burger", 12.99, "Main"));
        menu.push_back(make_unique<MenuItem>("M2", "Pizza", 15.99, "Main"));
        menu.push_back(make_unique<MenuItem>("M3", "Salad", 8.99, "Appetizer"));
    }
    
    Table* findAvailableTable(int partySize) {
        for (auto& table : tables) {
            if (table->isAvailable() && table->getCapacity() >= partySize) {
                return table.get();
            }
        }
        return nullptr;
    }
    
    Order* placeOrder(Table* table, const vector<string>& itemIds) {
        auto order = make_unique<Order>(table);
        for (const auto& id : itemIds) {
            for (auto& item : menu) {
                if (item->getId() == id) {
                    order->addItem(item.get());
                }
            }
        }
        Order* orderPtr = order.get();
        orders[order->getOrderId()] = move(order);
        return orderPtr;
    }
    
    void displayMenu() {
        cout << "\n===== MENU =====" << endl;
        for (auto& item : menu) {
            cout << item->getId() << ": " << item->getName() << " - $" << item->getPrice() << endl;
        }
        cout << "================\n" << endl;
    }
};

int main() {
    Restaurant restaurant("The Grand Bistro");
    cout << "Restaurant Management System" << endl;
    restaurant.displayMenu();
    
    Table* table = restaurant.findAvailableTable(2);
    if (table) {
        cout << "Table " << table->getNumber() << " assigned" << endl;
        table->setStatus(TableStatus::OCCUPIED);
        
        Order* order = restaurant.placeOrder(table, {"M1", "M3"});
        order->display();
    }
    
    return 0;
}
```

---

**Next**: `medium/07-online-shopping-system.md`

