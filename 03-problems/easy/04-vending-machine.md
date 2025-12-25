# Problem 4: Vending Machine

**Difficulty**: Easy  
**Time to Solve**: 25-30 minutes  
**Companies**: Amazon, Google

## Problem Statement

Design a vending machine that can:
1. Display available products
2. Accept coins/notes
3. Dispense selected product
4. Return change
5. Handle insufficient balance
6. Maintain inventory
7. Different states (Idle, HasMoney, Dispensing)

### Requirements

**Functional Requirements**:
- Display products with prices
- Accept money (coins, notes)
- Select product
- Dispense product if paid enough
- Return change
- Cancel transaction and refund
- Track inventory

**Non-Functional Requirements**:
- State machine for different states
- Handle edge cases (out of stock, exact change)
- Inventory management

---

## Concepts Involved

1. **Design Patterns**: 
   - **State Pattern** (Machine states)
   - **Factory Pattern** (Product creation)
   - **Singleton** (Vending machine instance)
2. **State Machine**: Complex state transitions
3. **SOLID**: SRP, OCP, LSP

---

## State Diagram

```
     ┌──────────┐
     │   IDLE   │◄──────────────┐
     └────┬─────┘               │
          │ insertMoney()       │
          ▼                     │
  ┌────────────────┐            │
  │  ACCEPTING_    │            │
  │    MONEY       │            │
  └────┬───────────┘            │
       │ selectProduct()        │
       ▼                        │
  ┌────────────────┐            │
  │  DISPENSING    │            │
  │   PRODUCT      │            │
  └────┬───────────┘            │
       │ dispenseComplete()     │
       └────────────────────────┘
```

---

## Class Diagram

```
┌────────────────────┐
│  VendingMachine    │ ◄──── Singleton
├────────────────────┤
│ - state: State*    │
│ - inventory        │
│ - currentBalance   │
├────────────────────┤
│ + insertMoney()    │
│ + selectProduct()  │
│ + dispense()       │
│ + cancel()         │
└────────┬───────────┘
         │
         │ has
         ▼
┌────────────────────┐
│    State           │ ◄──── State Pattern
├────────────────────┤
│ + insertMoney()    │
│ + selectProduct()  │
│ + dispense()       │
│ + cancel()         │
└────────┬───────────┘
         │
    ┌────┴─────┬────────────┬─────────────┐
    ▼          ▼            ▼             ▼
┌─────────┐┌──────────┐┌──────────┐┌──────────┐
│IdleState││  Money   ││Dispensing││ NoChange │
│         ││  State   ││  State   ││  State   │
└─────────┘└──────────┘└──────────┘└──────────┘

┌────────────────────┐
│    Product         │
├────────────────────┤
│ - id: string       │
│ - name: string     │
│ - price: double    │
│ - quantity: int    │
├────────────────────┤
│ + isAvailable()    │
└────────────────────┘

┌────────────────────┐
│   Inventory        │
├────────────────────┤
│ - products: map    │
├────────────────────┤
│ + addProduct()     │
│ + getProduct()     │
│ + updateQuantity() │
└────────────────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <string>
#include <map>
#include <memory>
#include <vector>

using namespace std;

// Forward declarations
class VendingMachineState;
class VendingMachine;

// ============== Product ==============

class Product {
private:
    string id;
    string name;
    double price;
    int quantity;
    
public:
    Product(const string& i, const string& n, double p, int q)
        : id(i), name(n), price(p), quantity(q) {}
    
    string getId() const { return id; }
    string getName() const { return name; }
    double getPrice() const { return price; }
    int getQuantity() const { return quantity; }
    
    bool isAvailable() const { return quantity > 0; }
    
    void decrementQuantity() {
        if (quantity > 0) quantity--;
    }
    
    void incrementQuantity(int count = 1) {
        quantity += count;
    }
    
    void display() const {
        cout << "[" << id << "] " << name << " - $" << price 
             << " (" << quantity << " available)" << endl;
    }
};

// ============== Inventory ==============

class Inventory {
private:
    map<string, unique_ptr<Product>> products;
    
public:
    void addProduct(unique_ptr<Product> product) {
        string id = product->getId();
        products[id] = move(product);
    }
    
    Product* getProduct(const string& id) {
        auto it = products.find(id);
        return (it != products.end()) ? it->second.get() : nullptr;
    }
    
    void updateQuantity(const string& id, int quantity) {
        Product* product = getProduct(id);
        if (product) {
            product->incrementQuantity(quantity);
        }
    }
    
    void displayAll() const {
        cout << "\n========== PRODUCTS ==========" << endl;
        for (const auto& [id, product] : products) {
            product->display();
        }
        cout << "==============================\n" << endl;
    }
};

// ============== Money/Coin ==============

enum class Coin {
    PENNY = 1,
    NICKEL = 5,
    DIME = 10,
    QUARTER = 25
};

enum class Note {
    ONE = 100,
    FIVE = 500,
    TEN = 1000,
    TWENTY = 2000
};

// ============== Vending Machine States ==============

class VendingMachineState {
public:
    virtual ~VendingMachineState() = default;
    virtual void insertMoney(VendingMachine* machine, double amount) = 0;
    virtual void selectProduct(VendingMachine* machine, const string& productId) = 0;
    virtual void dispenseProduct(VendingMachine* machine) = 0;
    virtual void cancelTransaction(VendingMachine* machine) = 0;
    virtual string getStateName() const = 0;
};

// Forward declare states
class IdleState;
class AcceptingMoneyState;
class DispensingState;

// ============== Vending Machine ==============

class VendingMachine {
private:
    static VendingMachine* instance;
    
    VendingMachineState* currentState;
    unique_ptr<IdleState> idleState;
    unique_ptr<AcceptingMoneyState> acceptingMoneyState;
    unique_ptr<DispensingState> dispensingState;
    
    Inventory inventory;
    double currentBalance;
    Product* selectedProduct;
    
    VendingMachine() : currentBalance(0), selectedProduct(nullptr) {
        initializeStates();
        initializeInventory();
    }
    
    void initializeStates();
    
    void initializeInventory() {
        inventory.addProduct(make_unique<Product>("A1", "Coke", 1.50, 10));
        inventory.addProduct(make_unique<Product>("A2", "Pepsi", 1.50, 10));
        inventory.addProduct(make_unique<Product>("B1", "Water", 1.00, 15));
        inventory.addProduct(make_unique<Product>("B2", "Juice", 2.00, 8));
        inventory.addProduct(make_unique<Product>("C1", "Chips", 1.25, 12));
        inventory.addProduct(make_unique<Product>("C2", "Chocolate", 1.75, 10));
    }
    
public:
    static VendingMachine* getInstance() {
        if (instance == nullptr) {
            instance = new VendingMachine();
        }
        return instance;
    }
    
    VendingMachineState* getIdleState() { return idleState.get(); }
    VendingMachineState* getAcceptingMoneyState() { return acceptingMoneyState.get(); }
    VendingMachineState* getDispensingState() { return dispensingState.get(); }
    
    void setState(VendingMachineState* state) {
        cout << "\n[State Change: " << currentState->getStateName() 
             << " -> " << state->getStateName() << "]" << endl;
        currentState = state;
    }
    
    double getCurrentBalance() const { return currentBalance; }
    void addBalance(double amount) { currentBalance += amount; }
    void resetBalance() { currentBalance = 0; }
    
    Product* getSelectedProduct() const { return selectedProduct; }
    void setSelectedProduct(Product* product) { selectedProduct = product; }
    
    Inventory& getInventory() { return inventory; }
    
    // Public interface
    void insertMoney(double amount) {
        currentState->insertMoney(this, amount);
    }
    
    void selectProduct(const string& productId) {
        currentState->selectProduct(this, productId);
    }
    
    void dispenseProduct() {
        currentState->dispenseProduct(this);
    }
    
    void cancelTransaction() {
        currentState->cancelTransaction(this);
    }
    
    void displayProducts() {
        inventory.displayAll();
    }
    
    void displayStatus() {
        cout << "\n========== VENDING MACHINE STATUS ==========" << endl;
        cout << "State: " << currentState->getStateName() << endl;
        cout << "Current Balance: $" << currentBalance << endl;
        if (selectedProduct) {
            cout << "Selected Product: " << selectedProduct->getName() << endl;
        }
        cout << "===========================================\n" << endl;
    }
    
    static void cleanup() {
        delete instance;
        instance = nullptr;
    }
};

VendingMachine* VendingMachine::instance = nullptr;

// ============== Concrete States ==============

class IdleState : public VendingMachineState {
public:
    void insertMoney(VendingMachine* machine, double amount) override {
        cout << "Money inserted: $" << amount << endl;
        machine->addBalance(amount);
        machine->setState(machine->getAcceptingMoneyState());
    }
    
    void selectProduct(VendingMachine* machine, const string& productId) override {
        cout << "Please insert money first!" << endl;
    }
    
    void dispenseProduct(VendingMachine* machine) override {
        cout << "Please insert money and select product first!" << endl;
    }
    
    void cancelTransaction(VendingMachine* machine) override {
        cout << "No transaction to cancel!" << endl;
    }
    
    string getStateName() const override { return "IDLE"; }
};

class AcceptingMoneyState : public VendingMachineState {
public:
    void insertMoney(VendingMachine* machine, double amount) override {
        cout << "Money inserted: $" << amount << endl;
        machine->addBalance(amount);
        cout << "Total balance: $" << machine->getCurrentBalance() << endl;
    }
    
    void selectProduct(VendingMachine* machine, const string& productId) override {
        Product* product = machine->getInventory().getProduct(productId);
        
        if (product == nullptr) {
            cout << "Invalid product code!" << endl;
            return;
        }
        
        if (!product->isAvailable()) {
            cout << "Product out of stock!" << endl;
            return;
        }
        
        if (machine->getCurrentBalance() < product->getPrice()) {
            cout << "Insufficient balance! Need $" << product->getPrice() 
                 << ", have $" << machine->getCurrentBalance() << endl;
            return;
        }
        
        machine->setSelectedProduct(product);
        cout << "Product selected: " << product->getName() << endl;
        machine->setState(machine->getDispensingState());
        machine->dispenseProduct(); // Auto-dispense
    }
    
    void dispenseProduct(VendingMachine* machine) override {
        cout << "Please select a product first!" << endl;
    }
    
    void cancelTransaction(VendingMachine* machine) override {
        double refund = machine->getCurrentBalance();
        cout << "Transaction cancelled. Refunding: $" << refund << endl;
        machine->resetBalance();
        machine->setState(machine->getIdleState());
    }
    
    string getStateName() const override { return "ACCEPTING_MONEY"; }
};

class DispensingState : public VendingMachineState {
public:
    void insertMoney(VendingMachine* machine, double amount) override {
        cout << "Please wait, dispensing product..." << endl;
    }
    
    void selectProduct(VendingMachine* machine, const string& productId) override {
        cout << "Please wait, dispensing product..." << endl;
    }
    
    void dispenseProduct(VendingMachine* machine) override {
        Product* product = machine->getSelectedProduct();
        
        cout << "\n========== DISPENSING ==========" << endl;
        cout << "Dispensing: " << product->getName() << endl;
        
        // Deduct price
        double price = product->getPrice();
        double change = machine->getCurrentBalance() - price;
        
        // Dispense product
        product->decrementQuantity();
        
        // Return change
        if (change > 0) {
            cout << "Returning change: $" << change << endl;
        }
        
        cout << "Thank you! Enjoy your " << product->getName() << endl;
        cout << "================================\n" << endl;
        
        // Reset machine
        machine->resetBalance();
        machine->setSelectedProduct(nullptr);
        machine->setState(machine->getIdleState());
    }
    
    void cancelTransaction(VendingMachine* machine) override {
        cout << "Cannot cancel during dispensing!" << endl;
    }
    
    string getStateName() const override { return "DISPENSING"; }
};

// Initialize states
void VendingMachine::initializeStates() {
    idleState = make_unique<IdleState>();
    acceptingMoneyState = make_unique<AcceptingMoneyState>();
    dispensingState = make_unique<DispensingState>();
    
    currentState = idleState.get();
}

// ============== Demo ==============

int main() {
    VendingMachine* vm = VendingMachine::getInstance();
    
    cout << "Welcome to Vending Machine!" << endl;
    vm->displayProducts();
    vm->displayStatus();
    
    // Scenario 1: Successful purchase
    cout << "\n=== Scenario 1: Buy Coke ===" << endl;
    vm->insertMoney(2.00);
    vm->selectProduct("A1");
    
    vm->displayProducts();
    vm->displayStatus();
    
    // Scenario 2: Insufficient money
    cout << "\n=== Scenario 2: Insufficient Money ===" << endl;
    vm->insertMoney(1.00);
    vm->selectProduct("B2"); // Juice costs $2.00
    vm->cancelTransaction();
    
    // Scenario 3: Add more money and buy
    cout << "\n=== Scenario 3: Add More Money ===" << endl;
    vm->insertMoney(1.00);
    vm->insertMoney(1.00);
    vm->selectProduct("C1"); // Chips $1.25
    
    // Scenario 4: Out of stock (buy all Cokes first)
    cout << "\n=== Scenario 4: Out of Stock ===" << endl;
    // First, let's buy 9 more Cokes to make it out of stock
    for (int i = 0; i < 9; i++) {
        vm->insertMoney(1.50);
        vm->selectProduct("A1");
    }
    
    vm->displayProducts();
    
    // Try to buy when out of stock
    vm->insertMoney(1.50);
    vm->selectProduct("A1");
    vm->cancelTransaction();
    
    vm->displayStatus();
    
    VendingMachine::cleanup();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **State Pattern**
- Clean separation of behavior per state
- Easy to add new states
- Prevents invalid transitions

### 2. **Inventory Management**
- Separate Inventory class (SRP)
- Product quantity tracking
- Easy to extend with restocking

### 3. **Money Handling**
- Accumulate balance
- Calculate change automatically
- Refund on cancel

---

## Extensions & Follow-ups

### Q1: How to handle exact change only?
```cpp
class NoChangeState : public VendingMachineState {
    void selectProduct(...) override {
        if (balance != price) {
            cout << "Exact change only!" << endl;
            return;
        }
        // Proceed
    }
};
```

### Q2: How to add different payment methods?
```cpp
class PaymentStrategy {
public:
    virtual bool processPayment(double amount) = 0;
};

class CashPayment : public PaymentStrategy {
    bool processPayment(double amount) override { ... }
};

class CardPayment : public PaymentStrategy {
    bool processPayment(double amount) override { ... }
};
```

### Q3: How to handle refill/restocking?
```cpp
class AdminMode {
public:
    void refillProduct(string id, int quantity) {
        inventory.updateQuantity(id, quantity);
    }
    
    void collectMoney() {
        // Remove cash from machine
    }
};
```

### Q4: How to add temperature control for cold drinks?
```cpp
class RefrigeratedProduct : public Product {
private:
    double currentTemp;
    double targetTemp;
    
public:
    bool isTemperatureOK() const {
        return currentTemp <= targetTemp;
    }
};
```

---

## Complexity Analysis

- **Insert Money**: O(1)
- **Select Product**: O(1) with hash map
- **Dispense**: O(1)
- **Space**: O(n) where n = number of products

---

## Compilation & Execution

```bash
g++ -std=c++17 vending_machine.cpp -o vending
./vending
```

---

## Sample Output

```
Welcome to Vending Machine!

========== PRODUCTS ==========
[A1] Coke - $1.5 (10 available)
[A2] Pepsi - $1.5 (10 available)
[B1] Water - $1 (15 available)
[B2] Juice - $2 (8 available)
[C1] Chips - $1.25 (12 available)
[C2] Chocolate - $1.75 (10 available)
==============================

=== Scenario 1: Buy Coke ===

[State Change: IDLE -> ACCEPTING_MONEY]
Money inserted: $2
Product selected: Coke

[State Change: ACCEPTING_MONEY -> DISPENSING]

========== DISPENSING ==========
Dispensing: Coke
Returning change: $0.5
Thank you! Enjoy your Coke
================================

[State Change: DISPENSING -> IDLE]
```

---

**Next Problem**: `06-traffic-signal.md`

