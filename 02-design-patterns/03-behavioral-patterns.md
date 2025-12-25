# Behavioral Design Patterns

Behavioral patterns are concerned with algorithms and the assignment of responsibilities between objects. They describe not just patterns of objects or classes but also the patterns of communication between them.

## Table of Contents
1. [Strategy Pattern](#1-strategy-pattern)
2. [Observer Pattern](#2-observer-pattern)
3. [Command Pattern](#3-command-pattern)
4. [State Pattern](#4-state-pattern)
5. [Template Method Pattern](#5-template-method-pattern)
6. [Iterator Pattern](#6-iterator-pattern)
7. [Chain of Responsibility Pattern](#7-chain-of-responsibility-pattern)

---

## 1. Strategy Pattern

**Intent**: Define a family of algorithms, encapsulate each one, and make them interchangeable. Strategy lets the algorithm vary independently from clients that use it.

**When to Use**:
- Multiple related classes differ only in behavior
- You need different variants of an algorithm
- Algorithm uses data that clients shouldn't know about
- Class has many conditional statements

### Structure

```
┌─────────────┐
│   Context   │
├─────────────┤
│ - strategy  │───────┐
├─────────────┤       │
│ +execute()  │       ▼
└─────────────┘  ┌──────────────┐
                 │   Strategy   │ (interface)
                 ├──────────────┤
                 │+algorithm()  │
                 └──────△───────┘
                        │
          ┌─────────────┼─────────────┬─────────────┐
          │             │             │             │
   ┌──────▼───────┐  ┌──▼──────────┐  ┌──▼──────────┐
   │ConcreteStratA│  │ConcreteStratB│ │ConcreteStratC│
   ├──────────────┤  ├──────────────┤ ├──────────────┤
   │+ algorithm() │  │+ algorithm() │ │+ algorithm() │
   └──────────────┘  └──────────────┘ └──────────────┘
```

### C++ Implementation

```cpp
#include <iostream>
#include <memory>
#include <string>

using namespace std;

// Strategy interface
class PaymentStrategy {
public:
    virtual ~PaymentStrategy() = default;
    virtual void pay(double amount) = 0;
};

// Concrete Strategy A
class CreditCardPayment : public PaymentStrategy {
private:
    string cardNumber;
    string cvv;
    
public:
    CreditCardPayment(const string& num, const string& cvv)
        : cardNumber(num), cvv(cvv) {}
    
    void pay(double amount) override {
        cout << "Paid $" << amount << " using Credit Card ending in "
             << cardNumber.substr(cardNumber.length() - 4) << endl;
    }
};

// Concrete Strategy B
class PayPalPayment : public PaymentStrategy {
private:
    string email;
    
public:
    PayPalPayment(const string& e) : email(e) {}
    
    void pay(double amount) override {
        cout << "Paid $" << amount << " using PayPal account " << email << endl;
    }
};

// Concrete Strategy C
class CryptoPayment : public PaymentStrategy {
private:
    string walletAddress;
    
public:
    CryptoPayment(const string& addr) : walletAddress(addr) {}
    
    void pay(double amount) override {
        cout << "Paid $" << amount << " using Crypto wallet "
             << walletAddress.substr(0, 8) << "..." << endl;
    }
};

// Context
class ShoppingCart {
private:
    unique_ptr<PaymentStrategy> paymentStrategy;
    double totalAmount;
    
public:
    ShoppingCart() : totalAmount(0) {}
    
    void addItem(double price) {
        totalAmount += price;
    }
    
    void setPaymentStrategy(unique_ptr<PaymentStrategy> strategy) {
        paymentStrategy = move(strategy);
    }
    
    void checkout() {
        if (paymentStrategy) {
            paymentStrategy->pay(totalAmount);
        } else {
            cout << "Please select a payment method!" << endl;
        }
    }
};
```

**Usage Example**:
```cpp
ShoppingCart cart;
cart.addItem(50.0);
cart.addItem(30.0);

// Pay with credit card
cart.setPaymentStrategy(make_unique<CreditCardPayment>("1234567890123456", "123"));
cart.checkout();

// Change strategy to PayPal
cart.setPaymentStrategy(make_unique<PayPalPayment>("user@email.com"));
cart.checkout();
```

---

## 2. Observer Pattern

**Intent**: Define a one-to-many dependency between objects so that when one object changes state, all its dependents are notified and updated automatically.

**When to Use**:
- Changes to one object require changing others
- Object should notify others without assumptions about who they are
- Event handling systems
- Publish-subscribe systems

### Structure

```
┌──────────────┐         ┌──────────────┐
│   Subject    │◄────────│   Observer   │
├──────────────┤         │ (interface)  │
│- observers   │         ├──────────────┤
│+ attach()    │         │ + update()   │
│+ detach()    │         └──────△───────┘
│+ notify()    │                │
└──────△───────┘          ┌─────┴─────┐
       │                  │             │
┌──────▼──────┐    ┌──────▼──────┐ ┌─────▼──────┐
│ConcreteSubject│  │ConcreteObsA │ │ConcreteObsB│
├─────────────┤    ├─────────────┤ ├────────────┤
│- state      │    │ + update()  │ │ + update() │
│+ getState() │    └─────────────┘ └────────────┘
│+ setState() │
└─────────────┘
```

### C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>

using namespace std;

// Observer interface
class Observer {
public:
    virtual ~Observer() = default;
    virtual void update(const string& message) = 0;
};

// Subject
class NewsAgency {
private:
    vector<Observer*> observers;
    string latestNews;
    
public:
    void attach(Observer* observer) {
        observers.push_back(observer);
    }
    
    void detach(Observer* observer) {
        observers.erase(remove(observers.begin(), observers.end(), observer), observers.end());
    }
    
    void setNews(const string& news) {
        latestNews = news;
        notify();
    }
    
    void notify() {
        for (Observer* observer : observers) {
            observer->update(latestNews);
        }
    }
};

// Concrete Observer A
class NewsChannel : public Observer {
private:
    string channelName;
    
public:
    NewsChannel(const string& name) : channelName(name) {}
    
    void update(const string& message) override {
        cout << channelName << " received news: " << message << endl;
    }
};

// Concrete Observer B
class MobileApp : public Observer {
private:
    string userId;
    
public:
    MobileApp(const string& user) : userId(user) {}
    
    void update(const string& message) override {
        cout << "Push notification to " << userId << ": " << message << endl;
    }
};

// Concrete Observer C
class EmailSubscriber : public Observer {
private:
    string email;
    
public:
    EmailSubscriber(const string& e) : email(e) {}
    
    void update(const string& message) override {
        cout << "Email sent to " << email << ": " << message << endl;
    }
};
```

**Usage Example**:
```cpp
NewsAgency agency;

NewsChannel cnn("CNN");
MobileApp app("user123");
EmailSubscriber subscriber("user@email.com");

// Subscribe observers
agency.attach(&cnn);
agency.attach(&app);
agency.attach(&subscriber);

// Publish news - all observers notified
agency.setNews("Breaking: New technology announced!");

// Unsubscribe one observer
agency.detach(&app);

// Next news update
agency.setNews("Update: Stock market reaches new high");
```

---

## 3. Command Pattern

**Intent**: Encapsulate a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations.

**When to Use**:
- Parameterize objects with operations
- Queue operations
- Support undo/redo
- Log changes for crash recovery
- Structure system around high-level operations

### Structure

```
┌──────────────┐       ┌──────────────┐
│   Client     │──────>│   Invoker    │
└──────────────┘       ├──────────────┤
                       │- command     │
                       │+ execute()   │
                       └──────┬───────┘
                              │
                              ▼
                       ┌──────────────┐
                       │   Command    │ (interface)
                       ├──────────────┤
                       │ + execute()  │
                       │ + undo()     │
                       └──────△───────┘
                              │
                       ┌──────┴───────┐
                ┌──────▼──────┐  ┌────▼──────┐
                │ConcreteCmd A│  │ConcreteCmd B│
                ├─────────────┤  ├───────────┤
                │- receiver   │  │- receiver │
                │+ execute()  │  │+ execute()│
                │+ undo()     │  │+ undo()   │
                └──────┬──────┘  └─────┬─────┘
                       │               │
                       ▼               ▼
                  ┌──────────────┐
                  │   Receiver   │
                  ├──────────────┤
                  │+ action()    │
                  └──────────────┘
```

### C++ Implementation

```cpp
#include <iostream>
#include <memory>
#include <vector>
#include <string>

using namespace std;

// Receiver
class Light {
private:
    bool isOn;
    int brightness;
    
public:
    Light() : isOn(false), brightness(0) {}
    
    void turnOn() {
        isOn = true;
        brightness = 100;
        cout << "Light is ON (brightness: " << brightness << "%)" << endl;
    }
    
    void turnOff() {
        isOn = false;
        brightness = 0;
        cout << "Light is OFF" << endl;
    }
    
    void dim(int level) {
        if (isOn) {
            brightness = level;
            cout << "Light dimmed to " << brightness << "%" << endl;
        }
    }
};

// Command interface
class Command {
public:
    virtual ~Command() = default;
    virtual void execute() = 0;
    virtual void undo() = 0;
};

// Concrete Command A
class LightOnCommand : public Command {
private:
    Light* light;
    
public:
    LightOnCommand(Light* l) : light(l) {}
    
    void execute() override {
        light->turnOn();
    }
    
    void undo() override {
        light->turnOff();
    }
};

// Concrete Command B
class LightOffCommand : public Command {
private:
    Light* light;
    
public:
    LightOffCommand(Light* l) : light(l) {}
    
    void execute() override {
        light->turnOff();
    }
    
    void undo() override {
        light->turnOn();
    }
};

// Concrete Command C
class LightDimCommand : public Command {
private:
    Light* light;
    int level;
    int previousLevel;
    
public:
    LightDimCommand(Light* l, int lvl) : light(l), level(lvl), previousLevel(100) {}
    
    void execute() override {
        light->dim(level);
    }
    
    void undo() override {
        light->dim(previousLevel);
    }
};

// Invoker
class RemoteControl {
private:
    vector<unique_ptr<Command>> history;
    
public:
    void executeCommand(unique_ptr<Command> command) {
        command->execute();
        history.push_back(move(command));
    }
    
    void undo() {
        if (!history.empty()) {
            history.back()->undo();
            history.pop_back();
        } else {
            cout << "Nothing to undo!" << endl;
        }
    }
};
```

**Usage Example**:
```cpp
Light livingRoomLight;
RemoteControl remote;

// Execute commands
remote.executeCommand(make_unique<LightOnCommand>(&livingRoomLight));
remote.executeCommand(make_unique<LightDimCommand>(&livingRoomLight, 50));
remote.executeCommand(make_unique<LightOffCommand>(&livingRoomLight));

// Undo last command
remote.undo();  // Turns light back on
remote.undo();  // Restores to 100%
remote.undo();  // Turns light off
```

---

## 4. State Pattern

**Intent**: Allow an object to alter its behavior when its internal state changes. The object will appear to change its class.

**When to Use**:
- Object behavior depends on its state
- Operations have large conditional statements
- State transitions are explicit
- State-specific behavior needs to be defined in separate classes

### Structure

```
┌──────────────┐         ┌──────────────┐
│   Context    │────────>│    State     │ (interface)
├──────────────┤         ├──────────────┤
│- state       │         │ + handle()   │
│+ request()   │         └──────△───────┘
└──────────────┘                │
                        ┌───────┼───────┬───────┐
                 ┌──────▼────┐  ┌──▼───────┐  ┌──▼───────┐
                 │ConcreteState│  │ConcreteState│  │ConcreteState│
                 │     A     │  │     B     │  │     C     │
                 ├───────────┤  ├───────────┤  ├───────────┤
                 │+ handle() │  │+ handle() │  │+ handle() │
                 └───────────┘  └───────────┘  └───────────┘
```

### C++ Implementation

```cpp
#include <iostream>
#include <memory>

using namespace std;

// Forward declaration
class TCPConnection;

// State interface
class TCPState {
public:
    virtual ~TCPState() = default;
    virtual void open(TCPConnection* connection) = 0;
    virtual void close(TCPConnection* connection) = 0;
    virtual void acknowledge(TCPConnection* connection) = 0;
};

// Context
class TCPConnection {
private:
    unique_ptr<TCPState> state;
    
public:
    TCPConnection();
    
    void setState(unique_ptr<TCPState> newState) {
        state = move(newState);
    }
    
    void open() {
        state->open(this);
    }
    
    void close() {
        state->close(this);
    }
    
    void acknowledge() {
        state->acknowledge(this);
    }
};

// Concrete State A - Closed
class TCPClosed : public TCPState {
public:
    void open(TCPConnection* connection) override;
    
    void close(TCPConnection* connection) override {
        cout << "Connection is already closed" << endl;
    }
    
    void acknowledge(TCPConnection* connection) override {
        cout << "Cannot acknowledge, connection is closed" << endl;
    }
};

// Concrete State B - Listen
class TCPListen : public TCPState {
public:
    void open(TCPConnection* connection) override {
        cout << "Connection is already listening" << endl;
    }
    
    void close(TCPConnection* connection) override;
    
    void acknowledge(TCPConnection* connection) override;
};

// Concrete State C - Established
class TCPEstablished : public TCPState {
public:
    void open(TCPConnection* connection) override {
        cout << "Connection is already established" << endl;
    }
    
    void close(TCPConnection* connection) override;
    
    void acknowledge(TCPConnection* connection) override {
        cout << "Data acknowledged in established connection" << endl;
    }
};

// Implementations
void TCPClosed::open(TCPConnection* connection) {
    cout << "Opening connection..." << endl;
    connection->setState(make_unique<TCPListen>());
}

void TCPListen::close(TCPConnection* connection) {
    cout << "Closing connection..." << endl;
    connection->setState(make_unique<TCPClosed>());
}

void TCPListen::acknowledge(TCPConnection* connection) {
    cout << "Connection established!" << endl;
    connection->setState(make_unique<TCPEstablished>());
}

void TCPEstablished::close(TCPConnection* connection) {
    cout << "Closing established connection..." << endl;
    connection->setState(make_unique<TCPClosed>());
}

TCPConnection::TCPConnection() {
    state = make_unique<TCPClosed>();
}
```

**Usage Example**:
```cpp
TCPConnection connection;

connection.open();          // Opens, transitions to Listen
connection.acknowledge();   // Establishes connection
connection.acknowledge();   // Already established
connection.close();         // Closes connection
connection.close();         // Already closed
```

---

## 5. Template Method Pattern

**Intent**: Define the skeleton of an algorithm in an operation, deferring some steps to subclasses. Template Method lets subclasses redefine certain steps of an algorithm without changing the algorithm's structure.

**When to Use**:
- Implement invariant parts of algorithm once
- Common behavior should be factored and localized
- Control subclass extensions
- "Hollywood Principle" - Don't call us, we'll call you

### Structure

```
┌──────────────────┐
│ AbstractClass    │
├──────────────────┤
│+templateMethod() │────┐
│+primitiveOp1()   │    │ Calls
│+primitiveOp2()   │◄───┘
└────────△─────────┘
         │
    ┌────┴────┐
    │         │
┌───▼────────┐ ┌──▼──────────┐
│ConcreteClass│ │ConcreteClass │
│     A      │ │     B        │
├────────────┤ ├──────────────┤
│+ primitiveOp1()│ │+ primitiveOp1()│
│+ primitiveOp2()│ │+ primitiveOp2()│
└────────────┘ └──────────────┘
```

### C++ Implementation

```cpp
#include <iostream>
#include <string>

using namespace std;

// Abstract Class
class DataProcessor {
public:
    // Template method
    void process() {
        readData();
        processData();
        writeData();
    }
    
    virtual ~DataProcessor() = default;
    
protected:
    virtual void readData() = 0;
    virtual void processData() = 0;
    virtual void writeData() = 0;
};

// Concrete Class A
class CSVProcessor : public DataProcessor {
protected:
    void readData() override {
        cout << "Reading data from CSV file" << endl;
    }
    
    void processData() override {
        cout << "Processing CSV data" << endl;
    }
    
    void writeData() override {
        cout << "Writing data to CSV file" << endl;
    }
};

// Concrete Class B
class JSONProcessor : public DataProcessor {
protected:
    void readData() override {
        cout << "Reading data from JSON file" << endl;
    }
    
    void processData() override {
        cout << "Processing JSON data" << endl;
    }
    
    void writeData() override {
        cout << "Writing data to JSON file" << endl;
    }
};

// Concrete Class C with hooks
class XMLProcessor : public DataProcessor {
protected:
    void readData() override {
        cout << "Reading data from XML file" << endl;
    }
    
    void processData() override {
        cout << "Processing XML data" << endl;
        if (shouldValidate()) {
            validateSchema();
        }
    }
    
    void writeData() override {
        cout << "Writing data to XML file" << endl;
    }
    
    // Hook method
    virtual bool shouldValidate() {
        return true;
    }
    
    void validateSchema() {
        cout << "Validating XML schema" << endl;
    }
};
```

**Usage Example**:
```cpp
CSVProcessor csvProcessor;
cout << "=== Processing CSV ===" << endl;
csvProcessor.process();

cout << "\n=== Processing JSON ===" << endl;
JSONProcessor jsonProcessor;
jsonProcessor.process();

cout << "\n=== Processing XML ===" << endl;
XMLProcessor xmlProcessor;
xmlProcessor.process();
```

---

## 6. Iterator Pattern

**Intent**: Provide a way to access the elements of an aggregate object sequentially without exposing its underlying representation.

**When to Use**:
- Access contents without exposing internal structure
- Support multiple traversals
- Provide uniform interface for different structures

### Structure

```
┌──────────────┐         ┌──────────────┐
│  Aggregate   │────────>│   Iterator   │
│ (interface)  │         │ (interface)  │
├──────────────┤         ├──────────────┤
│+createIter() │         │ + next()     │
└──────△───────┘         │ + hasNext()  │
       │                 │ + current()  │
       │                 └──────△───────┘
┌──────▼────────┐                 │
│ConcreteAggreg │          ┌──────▼──────┐
├───────────────┤          │ConcreteIter │
│+ createIter() │─creates─>├─────────────┤
└───────────────┘          │+ next()     │
                           │+ hasNext()  │
                           │+ current()  │
                           └─────────────┘
```

### C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>

using namespace std;

// Forward declaration
template<typename T>
class ConcreteAggregate;

// Iterator interface
template<typename T>
class Iterator {
public:
    virtual ~Iterator() = default;
    virtual bool hasNext() = 0;
    virtual T next() = 0;
    virtual T current() = 0;
};

// Aggregate interface
template<typename T>
class Aggregate {
public:
    virtual ~Aggregate() = default;
    virtual unique_ptr<Iterator<T>> createIterator() = 0;
};

// Concrete Iterator
template<typename T>
class ConcreteIterator : public Iterator<T> {
private:
    const ConcreteAggregate<T>* aggregate;
    size_t index;
    
public:
    ConcreteIterator(const ConcreteAggregate<T>* agg) : aggregate(agg), index(0) {}
    
    bool hasNext() override {
        return index < aggregate->size();
    }
    
    T next() override {
        return aggregate->at(index++);
    }
    
    T current() override {
        return aggregate->at(index);
    }
};

// Concrete Aggregate
template<typename T>
class ConcreteAggregate : public Aggregate<T> {
private:
    vector<T> items;
    
public:
    void add(const T& item) {
        items.push_back(item);
    }
    
    size_t size() const {
        return items.size();
    }
    
    T at(size_t index) const {
        return items[index];
    }
    
    unique_ptr<Iterator<T>> createIterator() override {
        return make_unique<ConcreteIterator<T>>(this);
    }
};
```

**Usage Example**:
```cpp
ConcreteAggregate<string> library;
library.add("Book 1");
library.add("Book 2");
library.add("Book 3");

auto iterator = library.createIterator();

cout << "Iterating through library:" << endl;
while (iterator->hasNext()) {
    cout << "- " << iterator->next() << endl;
}
```

---

## 7. Chain of Responsibility Pattern

**Intent**: Avoid coupling the sender of a request to its receiver by giving more than one object a chance to handle the request. Chain the receiving objects and pass the request along the chain until an object handles it.

**When to Use**:
- More than one object may handle request
- Handler isn't known a priori
- Set of handlers should be specified dynamically
- Logging systems, event handling

### Structure

```
┌──────────────┐       ┌───────────────────────┐
│   Client     │──────>│   Handler (abstract)  │
└──────────────┘       ├───────────────────────┤
                       │- successor: Handler*  │
                       │+ handleRequest()      │
                       │+ setNext(Handler*)    │
                       └──────────△────────────┘
                                  │
                    ┌─────────────┼─────────────────┬
                    │             │                 │            
          ┌─────────▼────────┐  ┌─▼────────────┐  ┌─▼────────────┐
          │ ConcreteHandlerA │  │ConcreteHandlerB │ ConcreteHandlerC│
          ├──────────────────┤  ├──────────────┤  ├──────────────┤
          │+ handleRequest() │  │+ handleRequest()│+ handleRequest()│
          └──────────────────┘  └──────────────┘  └──────────────┘

Chain at runtime:
  Client ──> HandlerA ──> HandlerB ──> HandlerC ──> null
           (if can't handle, pass to next)
```

### C++ Implementation

```cpp
#include <iostream>
#include <memory>
#include <string>

using namespace std;

// Request
class SupportTicket {
private:
    string issue;
    int priority;  // 1=Low, 2=Medium, 3=High
    
public:
    SupportTicket(const string& i, int p) : issue(i), priority(p) {}
    
    string getIssue() const { return issue; }
    int getPriority() const { return priority; }
};

// Handler interface
class SupportHandler {
protected:
    unique_ptr<SupportHandler> nextHandler;
    
public:
    virtual ~SupportHandler() = default;
    
    void setNext(unique_ptr<SupportHandler> handler) {
        nextHandler = move(handler);
    }
    
    virtual void handleTicket(const SupportTicket& ticket) {
        if (nextHandler) {
            nextHandler->handleTicket(ticket);
        } else {
            cout << "Ticket escalated to management" << endl;
        }
    }
};

// Concrete Handler A
class Level1Support : public SupportHandler {
public:
    void handleTicket(const SupportTicket& ticket) override {
        if (ticket.getPriority() == 1) {
            cout << "Level 1 Support handling: " << ticket.getIssue() << endl;
        } else {
            cout << "Level 1 cannot handle, escalating..." << endl;
            SupportHandler::handleTicket(ticket);
        }
    }
};

// Concrete Handler B
class Level2Support : public SupportHandler {
public:
    void handleTicket(const SupportTicket& ticket) override {
        if (ticket.getPriority() == 2) {
            cout << "Level 2 Support handling: " << ticket.getIssue() << endl;
        } else {
            cout << "Level 2 cannot handle, escalating..." << endl;
            SupportHandler::handleTicket(ticket);
        }
    }
};

// Concrete Handler C
class Level3Support : public SupportHandler {
public:
    void handleTicket(const SupportTicket& ticket) override {
        if (ticket.getPriority() == 3) {
            cout << "Level 3 Support handling: " << ticket.getIssue() << endl;
        } else {
            cout << "Level 3 cannot handle, escalating..." << endl;
            SupportHandler::handleTicket(ticket);
        }
    }
};
```

**Usage Example**:
```cpp
// Build chain
auto level1 = make_unique<Level1Support>();
auto level2 = make_unique<Level2Support>();
auto level3 = make_unique<Level3Support>();

level1->setNext(move(level2));
level1->getNext()->setNext(move(level3));

// Submit tickets
SupportTicket ticket1("Password reset", 1);
SupportTicket ticket2("Database error", 2);
SupportTicket ticket3("Server crash", 3);

level1->handleTicket(ticket1);
cout << endl;
level1->handleTicket(ticket2);
cout << endl;
level1->handleTicket(ticket3);
```

---

## Pattern Comparison

| Pattern | Purpose | Key Characteristic |
|---------|---------|-------------------|
| **Strategy** | Algorithm selection | Encapsulate algorithms |
| **Observer** | Event notification | One-to-many dependency |
| **Command** | Request as object | Parameterize, queue, undo |
| **State** | State-dependent behavior | Change behavior with state |
| **Template Method** | Algorithm skeleton | Define algorithm structure |
| **Iterator** | Sequential access | Access without exposure |
| **Chain of Responsibility** | Pass request along chain | Decouple sender/receiver |

---

## When to Use Which Pattern?

### Choose Strategy when:
- You have multiple algorithms for a task
- You want to switch algorithms at runtime

### Choose Observer when:
- One object change affects many others
- You need publish-subscribe capability

### Choose Command when:
- You need to parameterize objects with operations
- You need undo/redo functionality

### Choose State when:
- Object behavior depends on state
- You have large conditional statements

### Choose Template Method when:
- You have invariant algorithm structure
- Subclasses should implement specific steps

### Choose Iterator when:
- You need to traverse collection
- You want to hide internal structure

### Choose Chain of Responsibility when:
- Multiple objects can handle request
- Handler isn't known in advance

---

## Real-World Usage in Problems

**Strategy**: Payment methods, pricing algorithms, sorting  
**Observer**: Stock price updates, event systems, notifications  
**Command**: Remote control, transaction system, undo/redo  
**State**: ATM states, elevator states, TCP connection  
**Template Method**: Data processing, game AI, workflows  
**Iterator**: Collection traversal, file system navigation  
**Chain of Responsibility**: Logging levels, authentication, request filtering  

---

## Course Complete!

You now have all three major categories of design patterns:
1. ✅ **Creational Patterns** - Object creation
2. ✅ **Structural Patterns** - Object composition
3. ✅ **Behavioral Patterns** - Object communication

**Next**: Start practicing with the 25 LLD problems in `03-problems/`!

