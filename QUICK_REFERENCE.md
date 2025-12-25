# LLD Quick Reference - Cheat Sheet

**For Last-Minute Interview Prep** ⚡

---

## Design Pattern Quick Match

```
┌────────────────────────────────────────────────────────────┐
│ Need                          │ Pattern                    │
├───────────────────────────────┼────────────────────────────┤
│ Single instance               │ Singleton                  │
│ Object creation families      │ Abstract Factory           │
│ Complex object construction   │ Builder                    │
│ Clone expensive objects       │ Prototype                  │
│ Defer instantiation           │ Factory Method             │
│ Add features dynamically      │ Decorator                  │
│ Simplify complex subsystem    │ Facade                     │
│ Tree structures               │ Composite                  │
│ Runtime behavior change       │ Strategy                   │
│ State-dependent behavior      │ State                      │
│ Notify multiple objects       │ Observer                   │
│ Encapsulate requests          │ Command                    │
└────────────────────────────────────────────────────────────┘
```

---

## Top 10 Must-Know Problems

### 1. Parking Lot ⭐⭐⭐
- **Time**: 30-40 min
- **Patterns**: Singleton, Factory, Strategy
- **Key**: Spot types, vehicle types, fee calculation
- **Follow-up**: Reservations, multiple entrances, payment integration

### 2. Elevator System ⭐⭐⭐  
- **Time**: 45-60 min
- **Patterns**: State, Strategy (Scheduling), Singleton
- **Key**: Multiple elevators, optimal selection, thread-safety
- **Follow-up**: Energy optimization, peak hour handling, emergency mode

### 3. LRU Cache ⭐⭐⭐
- **Time**: 30-40 min
- **DS**: Doubly Linked List + HashMap
- **Key**: O(1) get/put, eviction policy
- **Follow-up**: LFU, TTL, thread-safe, distributed

### 4. ATM Machine ⭐⭐
- **Time**: 30-35 min
- **Patterns**: State, Strategy (Transaction types)
- **Key**: State transitions, cash denomination, transactions
- **Follow-up**: Multiple ATMs, network failure, biometric auth

### 5. Hotel Booking ⭐⭐
- **Time**: 40-50 min
- **Patterns**: Factory, Builder, Strategy (Pricing)
- **Key**: Availability search, concurrent booking, pricing
- **Follow-up**: Overbooking, cancellation, dynamic pricing

### 6. Movie Ticket Booking ⭐⭐
- **Time**: 45-55 min
- **Patterns**: Factory, Strategy
- **Key**: Seat locking, concurrency, payment timeout
- **Follow-up**: Multiple theaters, seat recommendations

### 7. Ride Sharing (Uber) ⭐⭐⭐
- **Time**: 60-90 min
- **Patterns**: Strategy (Matching, Pricing), Observer, State
- **Key**: Driver matching, dynamic pricing, trip states
- **Follow-up**: Pooling, heat maps, fraud detection

### 8. Online Shopping ⭐⭐
- **Time**: 50-60 min
- **Patterns**: Strategy (Payment, Shipping), Observer
- **Key**: Cart, inventory, order flow, payment
- **Follow-up**: Recommendations, reviews, wishlists

### 9. Library Management ⭐⭐
- **Time**: 30-40 min
- **Patterns**: Strategy (Fine calculation)
- **Key**: Book copies, lending, fines, reservations
- **Follow-up**: Lost books, renewals, digital books

### 10. Vending Machine ⭐⭐
- **Time**: 25-30 min
- **Patterns**: State, Factory
- **Key**: State transitions, money handling, inventory
- **Follow-up**: Exact change, card payment, temperature control

---

## Common Interview Questions

### Q: "Walk me through your design"
**Answer Template**:
1. "Let me start with the core entities..."
2. "The main classes are X, Y, Z"
3. "The relationships are..." (draw diagram)
4. "I'm using [Pattern] because..."
5. "The main flow is..."

### Q: "What design patterns did you use?"
**Answer Template**:
- "I used [Pattern] for [Reason]"
- Explain benefit vs alternatives
- Don't force patterns!

### Q: "How would you handle concurrency?"
**Answer Template**:
```cpp
// Identify critical sections
mutex mtx;
{
    lock_guard<mutex> lock(mtx);
    // Critical code
}

// Or use atomic operations
atomic<int> counter;
```

### Q: "How would this scale?"
**Answer Template**:
1. **Database**: Sharding by [key], Replication
2. **Caching**: Redis for [what], TTL strategy
3. **Load Balancing**: Round-robin/Consistent hashing
4. **Async Processing**: Message queues (Kafka)
5. **Microservices**: Split by [domain]

---

## SOLID Principles - One-Liners

```
S - Single Responsibility
    "One class, one reason to change"
    ❌ Employee handles DB + calculations
    ✅ Employee, EmployeeDB, PayrollCalculator

O - Open/Closed
    "Open for extension, closed for modification"
    ❌ if-else for new types
    ✅ Interface + polymorphism

L - Liskov Substitution
    "Subclass should work wherever parent works"
    ❌ Bird has fly(), but Ostrich can't fly
    ✅ FlyingBird, FlightlessBird

I - Interface Segregation
    "Many specific interfaces > one general"
    ❌ IWorker with eat(), sleep(), work() for Robot
    ✅ IWorkable, IEatable, ISleepable

D - Dependency Inversion
    "Depend on abstractions, not concretions"
    ❌ UserService has MySQLDatabase
    ✅ UserService has IDatabase interface
```

---

## Class Diagram Symbols

```
Inheritance:     Child ───▷ Parent
Implementation:  Class ─ ─▷ Interface
Association:     Class1 ───> Class2  (uses)
Aggregation:     Whole ◇───> Part    (has, part can exist alone)
Composition:     Whole ◆───> Part    (owns, part dies with whole)
```

---

## State Pattern Template

```cpp
class Context;

class State {
public:
    virtual void handle(Context* ctx) = 0;
};

class ConcreteStateA : public State {
    void handle(Context* ctx) override {
        // Do work
        ctx->setState(new ConcreteStateB());
    }
};

class Context {
    State* state;
public:
    void setState(State* s) { state = s; }
    void request() { state->handle(this); }
};
```

---

## Strategy Pattern Template

```cpp
class Strategy {
public:
    virtual void execute() = 0;
};

class ConcreteStrategyA : public Strategy {
    void execute() override { /* Implementation A */ }
};

class Context {
    Strategy* strategy;
public:
    void setStrategy(Strategy* s) { strategy = s; }
    void doWork() { strategy->execute(); }
};
```

---

## Observer Pattern Template

```cpp
class Observer {
public:
    virtual void update(const string& message) = 0;
};

class Subject {
    vector<Observer*> observers;
public:
    void attach(Observer* obs) { observers.push_back(obs); }
    void notify(const string& message) {
        for (auto* obs : observers) {
            obs->update(message);
        }
    }
};
```

---

## Singleton Pattern (Thread-Safe)

```cpp
class Singleton {
private:
    static Singleton* instance;
    static mutex mtx;
    Singleton() {}
    
public:
    static Singleton* getInstance() {
        lock_guard<mutex> lock(mtx);
        if (!instance) {
            instance = new Singleton();
        }
        return instance;
    }
    
    // Delete copy constructor
    Singleton(const Singleton&) = delete;
    Singleton& operator=(const Singleton&) = delete;
};

// C++11 Magic Static (Thread-safe)
class ModernSingleton {
public:
    static ModernSingleton& getInstance() {
        static ModernSingleton instance;
        return instance;
    }
};
```

---

## Time Complexity Quick Reference

```
┌──────────────────────┬──────────────┬─────────────────┐
│ Operation            │Data Structure│ Complexity      │
├──────────────────────┼──────────────┼─────────────────┤
│ Cache Get/Put        │ HashMap + DLL│ O(1)            │
│ Find Parking Spot    │ Linear scan  │ O(n), O(1) opt  │
│ Elevator Selection   │ Linear scan  │ O(n)            │
│ Search Books         │ Hash map     │ O(1)            │
│ Order Matching       │Priority queue│ O(log n)        │
│ Find Nearby Drivers  │ QuadTree     │ O(log n)        │
└──────────────────────┴──────────────┴─────────────────┘
```

---

## Common Follow-up Questions by Topic

### Booking Systems
- How to handle overbooking?
- Cancellation policy?
- Concurrent bookings?
- Refund processing?

### Real-time Systems
- How to handle high traffic?
- Caching strategy?
- Eventual consistency?
- Failover handling?

### Payment Systems
- Idempotency?
- Transaction rollback?
- Payment provider failure?
- Fraud detection?

### Matching Systems
- Matching algorithm?
- Real-time updates?
- What if no match?
- Optimization criteria?

---

## Interview Day Checklist

**Before Interview**:
- [ ] Review top 5 problems
- [ ] Review SOLID principles
- [ ] Review 3-4 design patterns
- [ ] Have pen/paper ready
- [ ] Test screen sharing

**During Interview**:
- [ ] Listen carefully (2 min)
- [ ] Ask clarifying questions (5 min)
- [ ] Design on paper/whiteboard (10 min)
- [ ] Implement core classes (25 min)
- [ ] Handle follow-ups (10 min)

**What to Say**:
- "Let me clarify the requirements..."
- "I'm thinking of using [Pattern] because..."
- "The tradeoff here is..."
- "For scale, we could..."
- "An alternative approach would be..."

**What NOT to Say**:
- "I don't know" (say "Let me think...")
- "That's impossible" (say "That's challenging, one approach...")
- Silence (think out loud!)

---

## Code Templates

### Enum Class
```cpp
enum class Status {
    PENDING,
    ACTIVE,
    COMPLETED
};
```

### Abstract Base Class
```cpp
class Base {
public:
    virtual ~Base() = default;
    virtual void method() = 0; // Pure virtual
};
```

### Smart Pointers
```cpp
unique_ptr<Type> obj = make_unique<Type>(args);
shared_ptr<Type> obj = make_shared<Type>(args);
```

### Timestamp
```cpp
time_t now = time(nullptr);
time_t future = now + (days * 24 * 3600);
double diff = difftime(end, start);
```

---

## Mental Checklist Before Submitting

- [ ] All classes follow SRP?
- [ ] Used appropriate design patterns?
- [ ] Handled edge cases?
- [ ] Proper access modifiers (private/protected/public)?
- [ ] Meaningful names?
- [ ] Can extend easily?
- [ ] Thread-safe where needed?

---

## Quick Win Statements

**Show expertise**:
- "I'll use RAII for resource management"
- "Let's ensure exception safety here"
- "We should consider const-correctness"
- "I'll make this thread-safe using RAII locks"
- "Let's favor composition over inheritance here"

**Show scalability thinking**:
- "For millions of users, we'd need sharding"
- "We could cache this with Redis"
- "This could be async with a message queue"
- "We'd need database indexing on [field]"
- "For global scale, we'd use CDN for [what]"

---

## Problem-Pattern Quick Map

```
Parking Lot      → Singleton, Factory, Strategy
ATM             → State, Strategy
Elevator        → State, Strategy, Observer
LRU Cache       → HashMap + DLL (no pattern needed)
Hotel Booking   → Factory, Builder, Strategy
Movie Booking   → Factory, Strategy + Concurrency
Vending Machine → State, Factory
Library         → Strategy (Fine), Factory
Ride Sharing    → Strategy × 3, Observer, State
Chess           → Strategy (Piece moves)
File System     → Composite
Shopping        → Strategy (Payment), Observer
Restaurant      → Observer, Command
```

---

**Remember**: Interview is about problem-solving approach, not perfection!

**Good luck! 🚀**

