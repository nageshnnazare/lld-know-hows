# Problem 6: Traffic Signal System

**Difficulty**: Easy  
**Time to Solve**: 30-35 minutes  
**Companies**: Cisco, Uber, Transportation companies

## Problem Statement

Design a traffic signal control system that can:
1. Manage signals for 4-way intersection
2. Coordinate signals to prevent conflicts
3. Handle emergency vehicle priority
4. Support pedestrian crossing signals
5. Implement different timing strategies
6. Monitor and log signal states

### Requirements

**Functional Requirements**:
- 4-way intersection (North, South, East, West)
- Each direction has Red, Yellow, Green lights
- Only one direction GREEN at a time (or opposite directions)
- Yellow transition between Green and Red
- Pedestrian crossing signals
- Emergency override (all red except emergency direction)
- Configurable timing for each state

**Non-Functional Requirements**:
- Thread-safe state transitions
- Real-time state updates
- Observer pattern for monitoring
- State pattern for signal states

---

## Concepts Involved

1. **Design Patterns**:
   - **State Pattern** (Signal states)
   - **Observer Pattern** (Monitoring)
   - **Strategy Pattern** (Timing strategies)
   - **Singleton** (Controller)
2. **Concurrency**: Thread-safe operations
3. **Real-time Systems**: Timer-based transitions

---

## System Design

```
┌────────────────────────────────────────┐
│    TrafficControlSystem                │
│  ┌──────────────────────────────────┐  │
│  │  TrafficController (Singleton)   │  │
│  │  - signals: map<Direction, *>    │  │
│  │  - currentState: SystemState*    │  │
│  │  + changeState()                 │  │
│  │  + handleEmergency()             │  │
│  └──────────────┬───────────────────┘  │
│                 │                      │
│                 ▼                      │
│  ┌──────────────────────────────────┐  │
│  │      TrafficSignal               │  │
│  │  - direction: Direction          │  │
│  │  - lightState: LightState        │  │
│  │  - pedestrianState: PedState     │  │
│  │  + changeLight()                 │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘

State Transitions:
  GREEN → YELLOW → RED → GREEN
  (with timing for each state)
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <map>
#include <vector>
#include <thread>
#include <mutex>
#include <chrono>
#include <memory>
#include <atomic>

using namespace std;

// ============== Enums ==============

enum class Direction {
    NORTH,
    SOUTH,
    EAST,
    WEST
};

enum class LightColor {
    RED,
    YELLOW,
    GREEN
};

enum class PedestrianSignal {
    WALK,
    DONT_WALK
};

// ============== Observer Interface ==============

class TrafficObserver {
public:
    virtual ~TrafficObserver() = default;
    virtual void onSignalChange(Direction dir, LightColor color) = 0;
    virtual void onEmergency(Direction emergencyDir) = 0;
};

// ============== Traffic Signal ==============

class TrafficSignal {
private:
    Direction direction;
    LightColor currentLight;
    PedestrianSignal pedestrianSignal;
    mutex signalMutex;
    
    string directionToString() const {
        switch(direction) {
            case Direction::NORTH: return "NORTH";
            case Direction::SOUTH: return "SOUTH";
            case Direction::EAST: return "EAST";
            case Direction::WEST: return "WEST";
            default: return "UNKNOWN";
        }
    }
    
    string lightToString() const {
        switch(currentLight) {
            case LightColor::RED: return "🔴 RED";
            case LightColor::YELLOW: return "🟡 YELLOW";
            case LightColor::GREEN: return "🟢 GREEN";
            default: return "UNKNOWN";
        }
    }
    
public:
    TrafficSignal(Direction dir) 
        : direction(dir), currentLight(LightColor::RED), 
          pedestrianSignal(PedestrianSignal::DONT_WALK) {}
    
    Direction getDirection() const { return direction; }
    LightColor getCurrentLight() const { return currentLight; }
    
    void changeLight(LightColor newLight) {
        lock_guard<mutex> lock(signalMutex);
        currentLight = newLight;
        
        // Pedestrian signal logic
        if (newLight == LightColor::GREEN) {
            pedestrianSignal = PedestrianSignal::DONT_WALK;
        } else if (newLight == LightColor::RED) {
            pedestrianSignal = PedestrianSignal::WALK;
        }
    }
    
    void display() const {
        cout << "[" << directionToString() << "] " << lightToString();
        
        if (pedestrianSignal == PedestrianSignal::WALK) {
            cout << " | Pedestrian: 🚶 WALK";
        } else {
            cout << " | Pedestrian: 🚫 DON'T WALK";
        }
        
        cout << endl;
    }
};

// ============== Timing Strategy ==============

class TimingStrategy {
public:
    virtual ~TimingStrategy() = default;
    virtual int getGreenDuration() const = 0;
    virtual int getYellowDuration() const = 0;
    virtual int getRedDuration() const = 0;
};

class StandardTiming : public TimingStrategy {
public:
    int getGreenDuration() const override { return 30; } // 30 seconds
    int getYellowDuration() const override { return 5; }  // 5 seconds
    int getRedDuration() const override { return 35; }    // 35 seconds
};

class PeakHourTiming : public TimingStrategy {
public:
    int getGreenDuration() const override { return 45; } // Longer green
    int getYellowDuration() const override { return 5; }
    int getRedDuration() const override { return 50; }
};

class NightTimeTiming : public TimingStrategy {
public:
    int getGreenDuration() const override { return 20; } // Shorter cycles
    int getYellowDuration() const override { return 3; }
    int getRedDuration() const override { return 23; }
};

// ============== System States ==============

class TrafficController;

class SystemState {
public:
    virtual ~SystemState() = default;
    virtual void handle(TrafficController* controller) = 0;
    virtual string getStateName() const = 0;
};

// Forward declarations
class NorthSouthGreenState;
class EastWestGreenState;
class EmergencyState;

// ============== Traffic Controller ==============

class TrafficController {
private:
    static TrafficController* instance;
    static mutex mtx;
    
    map<Direction, unique_ptr<TrafficSignal>> signals;
    SystemState* currentState;
    unique_ptr<TimingStrategy> timingStrategy;
    vector<TrafficObserver*> observers;
    
    unique_ptr<NorthSouthGreenState> nsGreenState;
    unique_ptr<EastWestGreenState> ewGreenState;
    unique_ptr<EmergencyState> emergencyState;
    
    atomic<bool> running;
    thread controlThread;
    
    TrafficController() : currentState(nullptr), running(false) {
        // Initialize signals for all directions
        signals[Direction::NORTH] = make_unique<TrafficSignal>(Direction::NORTH);
        signals[Direction::SOUTH] = make_unique<TrafficSignal>(Direction::SOUTH);
        signals[Direction::EAST] = make_unique<TrafficSignal>(Direction::EAST);
        signals[Direction::WEST] = make_unique<TrafficSignal>(Direction::WEST);
        
        // Default timing strategy
        timingStrategy = make_unique<StandardTiming>();
        
        // Initialize all signals to RED
        for (auto& [dir, signal] : signals) {
            signal->changeLight(LightColor::RED);
        }
    }
    
public:
    static TrafficController* getInstance() {
        lock_guard<mutex> lock(mtx);
        if (instance == nullptr) {
            instance = new TrafficController();
        }
        return instance;
    }
    
    void initializeStates();
    
    void setState(SystemState* state) {
        if (currentState) {
            cout << "\n[State Transition: " << currentState->getStateName() 
                 << " → " << state->getStateName() << "]" << endl;
        }
        currentState = state;
    }
    
    SystemState* getNSGreenState() { return nsGreenState.get(); }
    SystemState* getEWGreenState() { return ewGreenState.get(); }
    SystemState* getEmergencyState() { return emergencyState.get(); }
    
    TrafficSignal* getSignal(Direction dir) {
        return signals[dir].get();
    }
    
    TimingStrategy* getTimingStrategy() { return timingStrategy.get(); }
    
    void setTimingStrategy(unique_ptr<TimingStrategy> strategy) {
        timingStrategy = move(strategy);
        cout << "Timing strategy updated" << endl;
    }
    
    void addObserver(TrafficObserver* observer) {
        observers.push_back(observer);
    }
    
    void notifySignalChange(Direction dir, LightColor color) {
        for (auto* observer : observers) {
            observer->onSignalChange(dir, color);
        }
    }
    
    void notifyEmergency(Direction emergencyDir) {
        for (auto* observer : observers) {
            observer->onEmergency(emergencyDir);
        }
    }
    
    void start() {
        if (running) return;
        
        running = true;
        controlThread = thread(&TrafficController::controlLoop, this);
        cout << "\n🚦 Traffic Control System Started 🚦\n" << endl;
    }
    
    void stop() {
        running = false;
        if (controlThread.joinable()) {
            controlThread.join();
        }
        cout << "\n🚦 Traffic Control System Stopped 🚦\n" << endl;
    }
    
    void controlLoop() {
        while (running) {
            if (currentState) {
                currentState->handle(this);
            }
            this_thread::sleep_for(chrono::seconds(1));
        }
    }
    
    void displayStatus() {
        cout << "\n========== TRAFFIC SIGNAL STATUS ==========" << endl;
        if (currentState) {
            cout << "Current State: " << currentState->getStateName() << endl;
        }
        cout << "-------------------------------------------" << endl;
        
        for (auto& [dir, signal] : signals) {
            signal->display();
        }
        
        cout << "===========================================\n" << endl;
    }
    
    void handleEmergency(Direction emergencyDir) {
        cout << "\n🚨 EMERGENCY VEHICLE DETECTED 🚨" << endl;
        notifyEmergency(emergencyDir);
        setState(emergencyState.get());
    }
    
    static void cleanup() {
        if (instance) {
            instance->stop();
            delete instance;
            instance = nullptr;
        }
    }
};

TrafficController* TrafficController::instance = nullptr;
mutex TrafficController::mtx;

// ============== Concrete System States ==============

class NorthSouthGreenState : public SystemState {
private:
    int elapsedTime;
    
public:
    NorthSouthGreenState() : elapsedTime(0) {}
    
    void handle(TrafficController* controller) override {
        TimingStrategy* timing = controller->getTimingStrategy();
        
        if (elapsedTime == 0) {
            // Set North-South to GREEN
            controller->getSignal(Direction::NORTH)->changeLight(LightColor::GREEN);
            controller->getSignal(Direction::SOUTH)->changeLight(LightColor::GREEN);
            controller->notifySignalChange(Direction::NORTH, LightColor::GREEN);
            controller->notifySignalChange(Direction::SOUTH, LightColor::GREEN);
            
            // Set East-West to RED
            controller->getSignal(Direction::EAST)->changeLight(LightColor::RED);
            controller->getSignal(Direction::WEST)->changeLight(LightColor::RED);
            
            controller->displayStatus();
        }
        
        elapsedTime++;
        
        // Transition to YELLOW
        if (elapsedTime >= timing->getGreenDuration()) {
            controller->getSignal(Direction::NORTH)->changeLight(LightColor::YELLOW);
            controller->getSignal(Direction::SOUTH)->changeLight(LightColor::YELLOW);
            controller->displayStatus();
            
            this_thread::sleep_for(chrono::seconds(timing->getYellowDuration()));
            
            // Reset and transition to East-West
            elapsedTime = 0;
            controller->setState(controller->getEWGreenState());
        }
    }
    
    string getStateName() const override { return "NORTH-SOUTH GREEN"; }
};

class EastWestGreenState : public SystemState {
private:
    int elapsedTime;
    
public:
    EastWestGreenState() : elapsedTime(0) {}
    
    void handle(TrafficController* controller) override {
        TimingStrategy* timing = controller->getTimingStrategy();
        
        if (elapsedTime == 0) {
            // Set East-West to GREEN
            controller->getSignal(Direction::EAST)->changeLight(LightColor::GREEN);
            controller->getSignal(Direction::WEST)->changeLight(LightColor::GREEN);
            controller->notifySignalChange(Direction::EAST, LightColor::GREEN);
            controller->notifySignalChange(Direction::WEST, LightColor::GREEN);
            
            // Set North-South to RED
            controller->getSignal(Direction::NORTH)->changeLight(LightColor::RED);
            controller->getSignal(Direction::SOUTH)->changeLight(LightColor::RED);
            
            controller->displayStatus();
        }
        
        elapsedTime++;
        
        // Transition to YELLOW
        if (elapsedTime >= timing->getGreenDuration()) {
            controller->getSignal(Direction::EAST)->changeLight(LightColor::YELLOW);
            controller->getSignal(Direction::WEST)->changeLight(LightColor::YELLOW);
            controller->displayStatus();
            
            this_thread::sleep_for(chrono::seconds(timing->getYellowDuration()));
            
            // Reset and transition to North-South
            elapsedTime = 0;
            controller->setState(controller->getNSGreenState());
        }
    }
    
    string getStateName() const override { return "EAST-WEST GREEN"; }
};

class EmergencyState : public SystemState {
private:
    Direction emergencyDirection;
    int duration;
    
public:
    EmergencyState() : emergencyDirection(Direction::NORTH), duration(0) {}
    
    void setEmergencyDirection(Direction dir) {
        emergencyDirection = dir;
        duration = 0;
    }
    
    void handle(TrafficController* controller) override {
        if (duration == 0) {
            // Set all to RED except emergency direction
            for (auto dir : {Direction::NORTH, Direction::SOUTH, Direction::EAST, Direction::WEST}) {
                if (dir == emergencyDirection) {
                    controller->getSignal(dir)->changeLight(LightColor::GREEN);
                } else {
                    controller->getSignal(dir)->changeLight(LightColor::RED);
                }
            }
            controller->displayStatus();
        }
        
        duration++;
        
        // Emergency cleared after 20 seconds
        if (duration >= 20) {
            cout << "\n✓ Emergency cleared, resuming normal operation\n" << endl;
            duration = 0;
            controller->setState(controller->getNSGreenState());
        }
    }
    
    string getStateName() const override { return "EMERGENCY MODE"; }
};

void TrafficController::initializeStates() {
    nsGreenState = make_unique<NorthSouthGreenState>();
    ewGreenState = make_unique<EastWestGreenState>();
    emergencyState = make_unique<EmergencyState>();
    
    currentState = nsGreenState.get();
}

// ============== Concrete Observer ==============

class MonitoringSystem : public TrafficObserver {
private:
    string name;
    
public:
    MonitoringSystem(const string& n) : name(n) {}
    
    void onSignalChange(Direction dir, LightColor color) override {
        // Log signal change (in real system, would log to file/database)
        // cout << "[" << name << "] Signal changed: " << (int)dir << " -> " << (int)color << endl;
    }
    
    void onEmergency(Direction emergencyDir) override {
        cout << "[" << name << "] 🚨 Emergency detected on direction: " << (int)emergencyDir << endl;
    }
};

// ============== Demo ==============

int main() {
    TrafficController* controller = TrafficController::getInstance();
    controller->initializeStates();
    
    // Add monitoring system
    MonitoringSystem monitor("Central Monitor");
    controller->addObserver(&monitor);
    
    // Display initial status
    controller->displayStatus();
    
    // Start traffic control
    controller->start();
    
    // Run for 60 seconds with standard timing
    cout << "Running with STANDARD timing for 60 seconds..." << endl;
    this_thread::sleep_for(chrono::seconds(60));
    
    // Switch to peak hour timing
    cout << "\n🕐 Switching to PEAK HOUR timing...\n" << endl;
    controller->setTimingStrategy(make_unique<PeakHourTiming>());
    this_thread::sleep_for(chrono::seconds(50));
    
    // Simulate emergency
    cout << "\n🚨 Emergency vehicle approaching from NORTH!\n" << endl;
    controller->handleEmergency(Direction::NORTH);
    this_thread::sleep_for(chrono::seconds(25));
    
    // Continue normal operation
    this_thread::sleep_for(chrono::seconds(40));
    
    // Stop system
    TrafficController::cleanup();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **State Pattern**
- Each system state (NS Green, EW Green, Emergency) is a separate class
- Clean state transitions
- Easy to add new states

### 2. **Strategy Pattern for Timing**
- Different timing strategies for different times of day
- Easy to switch strategies at runtime
- Standard, Peak Hour, Night Time timings

### 3. **Observer Pattern**
- Monitoring systems can observe signal changes
- Decoupled from main controller
- Easy to add new observers

### 4. **Thread Safety**
- Mutex protection for signal state changes
- Atomic running flag
- Safe concurrent access

---

## Follow-up Questions

**Q1: How to add turn signals (left turn arrows)?**
```cpp
enum class LightColor {
    RED, YELLOW, GREEN,
    GREEN_LEFT_ARROW, YELLOW_LEFT_ARROW
};

// Add left turn phases to state machine
```

**Q2: How to implement adaptive timing based on traffic flow?**
```cpp
class AdaptiveTiming : public TimingStrategy {
    TrafficSensor* sensor;
public:
    int getGreenDuration() const override {
        return sensor->getTrafficDensity() > 0.7 ? 45 : 30;
    }
};
```

**Q3: How to coordinate multiple intersections?**
```cpp
class IntersectionNetwork {
    vector<TrafficController*> intersections;
public:
    void synchronize(); // Green wave coordination
    void optimizeFlow();
};
```

**Q4: How to handle sensor failures?**
```cpp
class FailSafeState : public SystemState {
    // All signals flash yellow/red
    // Switch to fixed timing
};
```

---

## Compilation & Execution

```bash
g++ -std=c++17 -pthread traffic_signal.cpp -o traffic
./traffic
```

---

**Next Problem**: `07-logger-system.md`

