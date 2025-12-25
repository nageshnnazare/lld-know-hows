# Problem 7: Online Shopping System

**Difficulty**: Medium  
**Time to Solve**: 50-60 minutes  
**Companies**: Amazon, Flipkart, eBay

## Problem Statement

Design an e-commerce system that supports:
1. Product catalog browsing
2. Shopping cart management
3. Order placement and tracking
4. Payment processing
5. Inventory management
6. User accounts

---

## Class Diagram

```
┌────────────────────┐
│  ShoppingSystem    │
├────────────────────┤
│ - products         │
│ - users            │
│ - orders           │
│ - inventory        │
├────────────────────┤
│ + searchProducts() │
│ + addToCart()      │
│ + checkout()       │
│ + trackOrder()     │
└────────┬───────────┘
         │
    ┌────┴─────┬──────────┬──────────┐
    ▼          ▼          ▼          ▼
┌─────────┐┌──────┐┌────────┐┌──────────┐
│ Product ││ User ││  Cart  ││  Order   │
├─────────┤├──────┤├────────┤├──────────┤
│- id     ││- id  ││- items ││- id      │
│- name   ││- name││- total ││- items   │
│- price  ││- cart│└────────┘│- status  │
│- stock  │└──────┘          │- payment │
└─────────┘                  └──────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <map>
#include <memory>
#include <string>
#include <algorithm>

using namespace std;

enum class OrderStatus { PENDING, CONFIRMED, SHIPPED, DELIVERED, CANCELLED };
enum class PaymentMethod { CREDIT_CARD, DEBIT_CARD, PAYPAL, COD };

// ============== Product ==============

class Product {
private:
    string productId;
    string name;
    string description;
    double price;
    string category;
    int stockQuantity;
    
public:
    Product(const string& id, const string& n, double p, const string& cat, int stock)
        : productId(id), name(n), price(p), category(cat), stockQuantity(stock) {}
    
    string getId() const { return productId; }
    string getName() const { return name; }
    double getPrice() const { return price; }
    string getCategory() const { return category; }
    int getStock() const { return stockQuantity; }
    
    bool isInStock(int quantity) const {
        return stockQuantity >= quantity;
    }
    
    bool reduceStock(int quantity) {
        if (stockQuantity >= quantity) {
            stockQuantity -= quantity;
            return true;
        }
        return false;
    }
    
    void addStock(int quantity) {
        stockQuantity += quantity;
    }
    
    void display() const {
        cout << name << " - $" << price << " (" << stockQuantity << " in stock)" << endl;
    }
};

// ============== Cart Item ==============

class CartItem {
private:
    Product* product;
    int quantity;
    
public:
    CartItem(Product* p, int qty) : product(p), quantity(qty) {}
    
    Product* getProduct() const { return product; }
    int getQuantity() const { return quantity; }
    void setQuantity(int qty) { quantity = qty; }
    
    double getSubtotal() const {
        return product->getPrice() * quantity;
    }
};

// ============== Shopping Cart ==============

class ShoppingCart {
private:
    map<string, unique_ptr<CartItem>> items; // productId -> CartItem
    
public:
    void addItem(Product* product, int quantity) {
        string productId = product->getId();
        
        if (items.find(productId) != items.end()) {
            // Update quantity
            items[productId]->setQuantity(items[productId]->getQuantity() + quantity);
        } else {
            items[productId] = make_unique<CartItem>(product, quantity);
        }
        
        cout << "✓ Added " << quantity << "x " << product->getName() << " to cart" << endl;
    }
    
    void removeItem(const string& productId) {
        items.erase(productId);
        cout << "✓ Item removed from cart" << endl;
    }
    
    void updateQuantity(const string& productId, int quantity) {
        if (items.find(productId) != items.end()) {
            if (quantity > 0) {
                items[productId]->setQuantity(quantity);
            } else {
                items.erase(productId);
            }
        }
    }
    
    double getTotal() const {
        double total = 0;
        for (const auto& [id, item] : items) {
            total += item->getSubtotal();
        }
        return total;
    }
    
    const map<string, unique_ptr<CartItem>>& getItems() const {
        return items;
    }
    
    void clear() {
        items.clear();
    }
    
    bool isEmpty() const {
        return items.empty();
    }
    
    void display() const {
        cout << "\n========== SHOPPING CART ==========" << endl;
        if (items.empty()) {
            cout << "Cart is empty" << endl;
        } else {
            for (const auto& [id, item] : items) {
                cout << item->getProduct()->getName() << " x" << item->getQuantity()
                     << " - $" << item->getSubtotal() << endl;
            }
            cout << "-----------------------------------" << endl;
            cout << "Total: $" << getTotal() << endl;
        }
        cout << "===================================\n" << endl;
    }
};

// ============== Address ==============

class Address {
private:
    string street;
    string city;
    string state;
    string zipCode;
    
public:
    Address(const string& st, const string& c, const string& s, const string& z)
        : street(st), city(c), state(s), zipCode(z) {}
    
    string getFullAddress() const {
        return street + ", " + city + ", " + state + " " + zipCode;
    }
};

// ============== Payment ==============

class Payment {
private:
    string paymentId;
    PaymentMethod method;
    double amount;
    bool completed;
    static int paymentCounter;
    
public:
    Payment(PaymentMethod m, double amt)
        : method(m), amount(amt), completed(false) {
        paymentId = "PAY" + to_string(++paymentCounter);
    }
    
    bool process() {
        // Simulate payment processing
        cout << "Processing payment of $" << amount << "..." << endl;
        completed = true;
        cout << "✓ Payment successful! ID: " << paymentId << endl;
        return true;
    }
    
    string getPaymentId() const { return paymentId; }
    bool isCompleted() const { return completed; }
};

int Payment::paymentCounter = 0;

// ============== Order ==============

class Order {
private:
    string orderId;
    string userId;
    vector<CartItem> items;
    Address shippingAddress;
    unique_ptr<Payment> payment;
    OrderStatus status;
    double totalAmount;
    time_t orderDate;
    static int orderCounter;
    
public:
    Order(const string& uid, const ShoppingCart& cart, const Address& addr,
          unique_ptr<Payment> pay)
        : userId(uid), shippingAddress(addr), payment(move(pay)),
          status(OrderStatus::PENDING), orderDate(time(nullptr)) {
        
        orderId = "ORD" + to_string(++orderCounter);
        
        // Copy cart items
        for (const auto& [id, item] : cart.getItems()) {
            items.push_back(CartItem(item->getProduct(), item->getQuantity()));
        }
        
        totalAmount = cart.getTotal();
    }
    
    string getOrderId() const { return orderId; }
    OrderStatus getStatus() const { return status; }
    
    void confirm() {
        if (payment->process()) {
            status = OrderStatus::CONFIRMED;
            cout << "✓ Order confirmed!" << endl;
        }
    }
    
    void ship() {
        if (status == OrderStatus::CONFIRMED) {
            status = OrderStatus::SHIPPED;
            cout << "✓ Order shipped!" << endl;
        }
    }
    
    void deliver() {
        if (status == OrderStatus::SHIPPED) {
            status = OrderStatus::DELIVERED;
            cout << "✓ Order delivered!" << endl;
        }
    }
    
    void cancel() {
        if (status == OrderStatus::PENDING || status == OrderStatus::CONFIRMED) {
            status = OrderStatus::CANCELLED;
            cout << "✓ Order cancelled" << endl;
        }
    }
    
    void display() const {
        cout << "\n========== ORDER DETAILS ==========" << endl;
        cout << "Order ID: " << orderId << endl;
        cout << "Status: " << (int)status << endl;
        cout << "-----------------------------------" << endl;
        
        for (const auto& item : items) {
            cout << item.getProduct()->getName() << " x" << item.getQuantity()
                 << " - $" << item.getSubtotal() << endl;
        }
        
        cout << "-----------------------------------" << endl;
        cout << "Total: $" << totalAmount << endl;
        cout << "Shipping to: " << shippingAddress.getFullAddress() << endl;
        cout << "===================================\n" << endl;
    }
};

int Order::orderCounter = 0;

// ============== User ==============

class User {
private:
    string userId;
    string name;
    string email;
    ShoppingCart cart;
    vector<string> orderHistory; // Order IDs
    
public:
    User(const string& id, const string& n, const string& e)
        : userId(id), name(n), email(e) {}
    
    string getUserId() const { return userId; }
    string getName() const { return name; }
    ShoppingCart& getCart() { return cart; }
    
    void addOrderToHistory(const string& orderId) {
        orderHistory.push_back(orderId);
    }
    
    void displayProfile() const {
        cout << "\n========== USER PROFILE ==========" << endl;
        cout << "ID: " << userId << endl;
        cout << "Name: " << name << endl;
        cout << "Email: " << email << endl;
        cout << "Orders: " << orderHistory.size() << endl;
        cout << "==================================\n" << endl;
    }
};

// ============== Shopping System ==============

class ShoppingSystem {
private:
    map<string, unique_ptr<Product>> products;
    map<string, unique_ptr<User>> users;
    map<string, unique_ptr<Order>> orders;
    
public:
    void addProduct(unique_ptr<Product> product) {
        string id = product->getId();
        products[id] = move(product);
    }
    
    User* registerUser(const string& id, const string& name, const string& email) {
        auto user = make_unique<User>(id, name, email);
        User* userPtr = user.get();
        users[id] = move(user);
        cout << "✓ User registered: " << name << endl;
        return userPtr;
    }
    
    vector<Product*> searchProducts(const string& keyword) {
        vector<Product*> results;
        
        for (auto& [id, product] : products) {
            if (product->getName().find(keyword) != string::npos ||
                product->getCategory().find(keyword) != string::npos) {
                results.push_back(product.get());
            }
        }
        
        return results;
    }
    
    vector<Product*> getProductsByCategory(const string& category) {
        vector<Product*> results;
        
        for (auto& [id, product] : products) {
            if (product->getCategory() == category) {
                results.push_back(product.get());
            }
        }
        
        return results;
    }
    
    Product* getProduct(const string& productId) {
        auto it = products.find(productId);
        return (it != products.end()) ? it->second.get() : nullptr;
    }
    
    Order* placeOrder(User* user, const Address& address, PaymentMethod paymentMethod) {
        ShoppingCart& cart = user->getCart();
        
        if (cart.isEmpty()) {
            cout << "Cart is empty!" << endl;
            return nullptr;
        }
        
        // Check stock availability
        for (const auto& [id, item] : cart.getItems()) {
            if (!item->getProduct()->isInStock(item->getQuantity())) {
                cout << "Insufficient stock for " << item->getProduct()->getName() << endl;
                return nullptr;
            }
        }
        
        // Create payment
        auto payment = make_unique<Payment>(paymentMethod, cart.getTotal());
        
        // Create order
        auto order = make_unique<Order>(user->getUserId(), cart, address, move(payment));
        order->confirm();
        
        // Reduce stock
        for (const auto& [id, item] : cart.getItems()) {
            item->getProduct()->reduceStock(item->getQuantity());
        }
        
        // Clear cart
        Order* orderPtr = order.get();
        string orderId = order->getOrderId();
        orders[orderId] = move(order);
        user->addOrderToHistory(orderId);
        cart.clear();
        
        return orderPtr;
    }
    
    void displayAllProducts() const {
        cout << "\n========== PRODUCT CATALOG ==========" << endl;
        for (const auto& [id, product] : products) {
            cout << "[" << id << "] ";
            product->display();
        }
        cout << "=====================================\n" << endl;
    }
};

// ============== Demo ==============

int main() {
    ShoppingSystem system;
    
    cout << "========== Online Shopping System Demo ==========\n" << endl;
    
    // Add products
    system.addProduct(make_unique<Product>("P001", "Laptop", 999.99, "Electronics", 10));
    system.addProduct(make_unique<Product>("P002", "Mouse", 29.99, "Electronics", 50));
    system.addProduct(make_unique<Product>("P003", "Desk Chair", 199.99, "Furniture", 15));
    system.addProduct(make_unique<Product>("P004", "Monitor", 299.99, "Electronics", 20));
    
    // Display catalog
    system.displayAllProducts();
    
    // Register user
    User* user = system.registerUser("U001", "Alice Johnson", "alice@email.com");
    user->displayProfile();
    
    // Browse and add to cart
    cout << "=== Step 1: Browsing Products ===" << endl;
    auto electronics = system.getProductsByCategory("Electronics");
    cout << "Found " << electronics.size() << " electronics" << endl;
    
    // Add items to cart
    cout << "\n=== Step 2: Adding to Cart ===" << endl;
    Product* laptop = system.getProduct("P001");
    Product* mouse = system.getProduct("P002");
    
    if (laptop && mouse) {
        user->getCart().addItem(laptop, 1);
        user->getCart().addItem(mouse, 2);
        user->getCart().display();
    }
    
    // Place order
    cout << "=== Step 3: Placing Order ===" << endl;
    Address address("123 Main St", "New York", "NY", "10001");
    Order* order = system.placeOrder(user, address, PaymentMethod::CREDIT_CARD);
    
    if (order) {
        order->display();
        
        // Track order
        cout << "=== Step 4: Order Tracking ===" << endl;
        order->ship();
        order->deliver();
    }
    
    // Display updated catalog
    cout << "\n=== Updated Inventory ===" << endl;
    system.displayAllProducts();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Shopping Cart**
- Session-based cart management
- Real-time total calculation
- Easy item updates

### 2. **Inventory Management**
- Stock validation before order
- Automatic stock reduction
- Stock alerts

### 3. **Order Processing**
- Multi-step workflow
- Payment integration
- Order tracking

---

## Follow-up Questions

**Q1: How to add product reviews?**
```cpp
class Review {
    User* user;
    int rating;
    string comment;
    time_t reviewDate;
};
```

**Q2: How to implement wishlist?**
```cpp
class Wishlist {
    vector<Product*> items;
    void addItem(Product* product);
    void moveToCart(ShoppingCart& cart);
};
```

**Q3: How to handle returns/refunds?**
```cpp
class Return {
    Order* order;
    string reason;
    ReturnStatus status;
    void process();
};
```

---

## Compilation

```bash
g++ -std=c++17 online_shopping.cpp -o shopping
./shopping
```

---

**Next**: `medium/08-file-system.md`

