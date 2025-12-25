# Problem 1: Elevator System

**Difficulty**: Medium  
**Time to Solve**: 45-60 minutes  
**Companies**: Amazon, Microsoft, Google, Facebook

## Problem Statement

Design an elevator control system for a building with multiple elevators. The system should:
1. Handle multiple elevators efficiently
2. Process requests from both inside and outside elevators
3. Implement intelligent scheduling algorithms
4. Handle emergency situations
5. Optimize for minimal waiting time

### Requirements

**Functional Requirements**:
- Multiple elevators in a building
- Request elevator from any floor (up/down buttons)
- Select destination inside elevator
- Display current floor and direction
- Door open/close mechanism
- Emergency stop button
- Optimal elevator selection algorithm

**Non-Functional Requirements**:
- Thread-safe operations
- Minimize average waiting time
- Energy efficient (idle strategy)
- Handle edge cases (overweight, door obstruction)

---

## Concepts Involved

1. **Design Patterns**:
   - **Strategy Pattern** (Scheduling algorithms)
   - **State Pattern** (Elevator states)
   - **Observer Pattern** (Floor displays)
   - **Singleton** (Elevator controller)
2. **Algorithms**: Scheduling (FCFS, SCAN, LOOK)
3. **Concurrency**: Thread-safe request handling
4. **State Machines**: Complex state transitions

---

## System Design

```
┌──────────────────────────────────────────────────┐
│            ElevatorControlSystem                 │
│  ┌──────────────────────────────────────────┐    │
│  │  ElevatorController (Singleton)          │    │
│  │  - elevators: vector<Elevator>           │    │
│  │  - scheduler: SchedulingStrategy         │    │
│  │  + handleExternalRequest(floor, dir)     │    │
│  │  + findOptimalElevator()                 │    │
│  └──────────────┬───────────────────────────┘    │
│                 │ manages                        │
│                 ▼                                │
│  ┌──────────────────────────────────────────┐    │
│  │         Elevator                         │    │
│  │  - id: int                               │    │
│  │  - currentFloor: int                     │    │
│  │  - direction: Direction                  │    │
│  │  - state: ElevatorState                  │    │
│  │  - requests: priority_queue              │    │
│  │  + move()                                │    │
│  │  + addRequest(floor)                     │    │
│  │  + openDoor() / closeDoor()              │    │
│  └──────────────────────────────────────────┘    │
└──────────────────────────────────────────────────┘

State Machine:
┌──────┐  moveUp   ┌────────┐  arrive  ┌──────────┐
│ IDLE │────────>  │ MOVING │────────> │ STOPPED  │
└───┬──┘           └────────┘          └─────┬────┘
    │                                        │openDoor
    │                                        ▼
    │                                  ┌──────────┐
    │◄─────────────────────────────────│   DOOR   │
    │           closeDoor              │   OPEN   │
    └──────────────────────────────────┴──────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <set>
#include <memory>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <chrono>
#include <algorithm>

using namespace std;

// ============== Enums ==============

enum class Direction {
    UP,
    DOWN,
    IDLE
};

enum class ElevatorState {
    IDLE,
    MOVING,
    STOPPED,
    DOOR_OPEN,
    MAINTENANCE
};

// ============== Request ==============

struct Request {
    int floor;
    Direction direction;
    time_t timestamp;
    
    Request(int f, Direction d) 
        : floor(f), direction(d), timestamp(time(nullptr)) {}
};

// ============== Door ==============

class Door {
private:
    bool isOpen;
    mutex doorMutex;
    
public:
    Door() : isOpen(false) {}
    
    void open() {
        lock_guard<mutex> lock(doorMutex);
        if (!isOpen) {
            cout << "  [Door Opening...]" << endl;
            this_thread::sleep_for(chrono::milliseconds(500));
            isOpen = true;
            cout << "  [Door Open]" << endl;
        }
    }
    
    void close() {
        lock_guard<mutex> lock(doorMutex);
        if (isOpen) {
            cout << "  [Door Closing...]" << endl;
            this_thread::sleep_for(chrono::milliseconds(500));
            isOpen = false;
            cout << "  [Door Closed]" << endl;
        }
    }
    
    bool isDoorOpen() const { return isOpen; }
};

// ============== Display ==============

class Display {
public:
    void showFloor(int elevatorId, int floor, Direction dir) {
        string dirStr = (dir == Direction::UP) ? "↑" : 
                       (dir == Direction::DOWN) ? "↓" : "•";
        cout << "[Elevator " << elevatorId << "] Floor: " << floor 
             << " " << dirStr << endl;
    }
    
    void showMessage(int elevatorId, const string& message) {
        cout << "[Elevator " << elevatorId << "] " << message << endl;
    }
};

// ============== Elevator ==============

class Elevator {
private:
    int id;
    int currentFloor;
    int capacity;
    Direction direction;
    ElevatorState state;
    
    set<int> upRequests;    // Floors requested going up
    set<int> downRequests;  // Floors requested going down
    
    Door door;
    Display display;
    
    mutex elevatorMutex;
    condition_variable cv;
    bool running;
    
public:
    Elevator(int elevatorId, int maxFloor) 
        : id(elevatorId), currentFloor(1), capacity(10), 
          direction(Direction::IDLE), state(ElevatorState::IDLE), 
          running(true) {}
    
    int getId() const { return id; }
    int getCurrentFloor() const { return currentFloor; }
    Direction getDirection() const { return direction; }
    ElevatorState getState() const { return state; }
    
    void addRequest(int floor, Direction requestDir) {
        lock_guard<mutex> lock(elevatorMutex);
        
        if (floor == currentFloor) {
            return; // Already at the floor
        }
        
        if (floor > currentFloor) {
            upRequests.insert(floor);
        } else {
            downRequests.insert(floor);
        }
        
        cout << "[Elevator " << id << "] Request added: Floor " 
             << floor << endl;
        
        cv.notify_one();
    }
    
    void processRequests() {
        while (running) {
            unique_lock<mutex> lock(elevatorMutex);
            
            // Wait if no requests
            cv.wait(lock, [this] { 
                return !upRequests.empty() || !downRequests.empty() || !running; 
            });
            
            if (!running) break;
            
            // Process requests based on current direction
            if (direction == Direction::IDLE) {
                if (!upRequests.empty()) {
                    direction = Direction::UP;
                } else if (!downRequests.empty()) {
                    direction = Direction::DOWN;
                }
            }
            
            lock.unlock();
            
            if (direction == Direction::UP) {
                processUpRequests();
            } else if (direction == Direction::DOWN) {
                processDownRequests();
            }
        }
    }
    
    void processUpRequests() {
        while (true) {
            lock_guard<mutex> lock(elevatorMutex);
            
            if (upRequests.empty()) {
                direction = Direction::IDLE;
                break;
            }
            
            // Get next floor
            auto it = upRequests.begin();
            int targetFloor = *it;
            
            if (targetFloor > currentFloor) {
                moveToFloor(targetFloor);
            }
            
            // Arrive at floor
            upRequests.erase(it);
            stopAtFloor(targetFloor);
        }
    }
    
    void processDownRequests() {
        while (true) {
            lock_guard<mutex> lock(elevatorMutex);
            
            if (downRequests.empty()) {
                direction = Direction::IDLE;
                break;
            }
            
            // Get next floor (highest in down requests)
            auto it = downRequests.rbegin();
            int targetFloor = *it;
            
            if (targetFloor < currentFloor) {
                moveToFloor(targetFloor);
            }
            
            // Arrive at floor
            downRequests.erase(*it);
            stopAtFloor(targetFloor);
        }
    }
    
    void moveToFloor(int targetFloor) {
        state = ElevatorState::MOVING;
        
        while (currentFloor != targetFloor) {
            this_thread::sleep_for(chrono::milliseconds(1000)); // 1 sec per floor
            
            if (currentFloor < targetFloor) {
                currentFloor++;
                direction = Direction::UP;
            } else {
                currentFloor--;
                direction = Direction::DOWN;
            }
            
            display.showFloor(id, currentFloor, direction);
        }
    }
    
    void stopAtFloor(int floor) {
        state = ElevatorState::STOPPED;
        display.showMessage(id, "Arrived at floor " + to_string(floor));
        
        door.open();
        state = ElevatorState::DOOR_OPEN;
        
        // Wait for passengers
        this_thread::sleep_for(chrono::milliseconds(2000));
        
        door.close();
        state = ElevatorState::IDLE;
    }
    
    void stop() {
        running = false;
        cv.notify_one();
    }
    
    // For scheduling algorithm
    int calculateDistance(int fromFloor, Direction requestDir) const {
        int distance = abs(currentFloor - fromFloor);
        
        // If elevator is moving in same direction, prioritize
        if (direction == requestDir) {
            if (direction == Direction::UP && fromFloor >= currentFloor) {
                return distance;
            } else if (direction == Direction::DOWN && fromFloor <= currentFloor) {
                return distance;
            }
        }
        
        // If idle, just distance matters
        if (direction == Direction::IDLE) {
            return distance;
        }
        
        // Moving in opposite direction - higher cost
        return distance + 100;
    }
};

// ============== Scheduling Strategy ==============

class SchedulingStrategy {
public:
    virtual ~SchedulingStrategy() = default;
    virtual Elevator* selectElevator(vector<unique_ptr<Elevator>>& elevators, 
                                     int floor, Direction direction) = 0;
};

// Nearest Car Algorithm
class NearestCarStrategy : public SchedulingStrategy {
public:
    Elevator* selectElevator(vector<unique_ptr<Elevator>>& elevators, 
                            int floor, Direction direction) override {
        Elevator* best = nullptr;
        int minDistance = INT_MAX;
        
        for (auto& elevator : elevators) {
            if (elevator->getState() == ElevatorState::MAINTENANCE) {
                continue;
            }
            
            int distance = elevator->calculateDistance(floor, direction);
            
            if (distance < minDistance) {
                minDistance = distance;
                best = elevator.get();
            }
        }
        
        return best;
    }
};

// ============== Elevator Controller ==============

class ElevatorController {
private:
    static ElevatorController* instance;
    static mutex mtx;
    
    vector<unique_ptr<Elevator>> elevators;
    unique_ptr<SchedulingStrategy> strategy;
    int numFloors;
    vector<thread> elevatorThreads;
    
    ElevatorController(int numElevators, int floors) : numFloors(floors) {
        strategy = make_unique<NearestCarStrategy>();
        
        for (int i = 0; i < numElevators; i++) {
            elevators.push_back(make_unique<Elevator>(i + 1, floors));
        }
    }
    
public:
    static ElevatorController* getInstance(int numElevators = 3, int floors = 10) {
        lock_guard<mutex> lock(mtx);
        if (instance == nullptr) {
            instance = new ElevatorController(numElevators, floors);
        }
        return instance;
    }
    
    void startAll() {
        for (auto& elevator : elevators) {
            elevatorThreads.emplace_back(&Elevator::processRequests, elevator.get());
        }
    }
    
    void requestElevator(int floor, Direction direction) {
        cout << "\n[REQUEST] Floor " << floor << " Direction: " 
             << (direction == Direction::UP ? "UP" : "DOWN") << endl;
        
        Elevator* selectedElevator = strategy->selectElevator(elevators, floor, direction);
        
        if (selectedElevator) {
            cout << "[ASSIGNED] Elevator " << selectedElevator->getId() << endl;
            selectedElevator->addRequest(floor, direction);
        } else {
            cout << "[ERROR] No elevator available!" << endl;
        }
    }
    
    void selectDestination(int elevatorId, int floor) {
        if (elevatorId > 0 && elevatorId <= elevators.size()) {
            elevators[elevatorId - 1]->addRequest(floor, Direction::IDLE);
        }
    }
    
    void displayStatus() {
        cout << "\n========== ELEVATOR STATUS ==========" << endl;
        for (auto& elevator : elevators) {
            cout << "Elevator " << elevator->getId() << ": "
                 << "Floor " << elevator->getCurrentFloor() << " | "
                 << "State: " << (int)elevator->getState() << endl;
        }
        cout << "====================================\n" << endl;
    }
    
    void stopAll() {
        for (auto& elevator : elevators) {
            elevator->stop();
        }
        
        for (auto& thread : elevatorThreads) {
            if (thread.joinable()) {
                thread.join();
            }
        }
    }
    
    static void cleanup() {
        if (instance) {
            instance->stopAll();
            delete instance;
            instance = nullptr;
        }
    }
};

ElevatorController* ElevatorController::instance = nullptr;
mutex ElevatorController::mtx;

// ============== Demo ==============

int main() {
    // Initialize elevator system with 3 elevators and 10 floors
    ElevatorController* controller = ElevatorController::getInstance(3, 10);
    
    // Start all elevators
    controller->startAll();
    
    cout << "Elevator System Started!" << endl;
    controller->displayStatus();
    
    // Simulate external requests
    this_thread::sleep_for(chrono::seconds(1));
    controller->requestElevator(5, Direction::UP);
    
    this_thread::sleep_for(chrono::seconds(2));
    controller->requestElevator(3, Direction::DOWN);
    
    this_thread::sleep_for(chrono::seconds(2));
    controller->requestElevator(7, Direction::UP);
    
    this_thread::sleep_for(chrono::seconds(2));
    controller->requestElevator(2, Direction::UP);
    
    // Let elevators process requests
    this_thread::sleep_for(chrono::seconds(15));
    
    controller->displayStatus();
    
    // Cleanup
    cout << "\nShutting down elevator system..." << endl;
    ElevatorController::cleanup();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Scheduling Algorithm**
- **Nearest Car**: Assigns closest available elevator
- **SCAN (Look)**: Elevator continues in one direction until no more requests
- **Priority-based**: VIP floors, emergency priorities

### 2. **Concurrency Handling**
- Each elevator runs in separate thread
- Mutex for request queue
- Condition variable for waiting

### 3. **Request Management**
- Separate up/down request queues
- Priority-based processing
- Avoid starvation

### 4. **State Management**
- Clear state transitions
- State-based behavior
- Thread-safe state changes

---

## Follow-up Questions

**Q1: How to handle multiple requests on same floor?**
- Group requests by floor
- Single stop for all requests on floor
- Optimize door open time

**Q2: How to implement energy-saving mode?**
- Move idle elevators to strategic floors (e.g., ground floor)
- Power down after timeout
- Wake up on request

**Q3: How to handle emergency situations?**
- Add EMERGENCY state
- Override normal scheduling
- Direct to nearest safe floor

**Q4: How to optimize for peak hours?**
- Zone-based control (elevators serve specific floor ranges)
- Predictive algorithms based on time/patterns
- Load balancing

**Q5: How to add weight sensors?**
- Add `currentWeight` and `maxWeight` to Elevator
- Reject new passengers if overweight
- Skip floor if full

---

## Complexity Analysis

- **Request Elevator**: O(n) where n = number of elevators
- **Process Request**: O(log k) where k = pending requests (priority queue)
- **Space**: O(n * k) for all elevator requests

---

## Compilation & Execution

```bash
g++ -std=c++17 -pthread elevator_system.cpp -o elevator
./elevator
```

---

**Next Problem**: `02-hotel-booking-system.md`

