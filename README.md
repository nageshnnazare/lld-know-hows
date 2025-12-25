# Low-Level Design (LLD) Course for C/C++ Developers

## 🎯 Course Overview

This comprehensive course is designed for experienced C/C++ developers preparing for system design interviews. It covers Low-Level Design (LLD) from fundamentals to advanced concepts with **30 real-world problems**.

## 📚 Course Structure

```
lld/
├── 01-concepts/          # Core OOP and Design Concepts (3 chapters)
├── 02-design-patterns/   # 21 Design Patterns
├── 03-problems/          # Interview Problems by Difficulty
│   ├── easy/            # 11 Easy Problems
│   ├── medium/          # 12 Medium Problems
│   └── hard/            # 7 Hard Problems
├── compile.sh           # Helper compilation script
├── COURSE_COMPLETE.md   # Course completion guide
└── QUICK_REFERENCE.md   # Design patterns cheat sheet
```

## 🎓 Learning Path

### Phase 1: Fundamentals (Week 1-2)
1. **OOP Concepts Review** (`01-concepts/01-oop-fundamentals.md`)
   - Classes, Inheritance, Polymorphism, Encapsulation, Abstraction
   - Class relationships, Interfaces vs Abstract Classes
2. **SOLID Principles** (`01-concepts/02-solid-principles.md`)
   - SRP, OCP, LSP, ISP, DIP with detailed examples
3. **UML Diagrams** (`01-concepts/03-uml-diagrams.md`)
   - Class diagrams, relationships, notation, patterns in UML

### Phase 2: Design Patterns (Week 3-4)
4. **Creational Patterns** (`02-design-patterns/01-creational-patterns.md`)
   - Singleton, Factory Method, Abstract Factory, Builder, Prototype
5. **Structural Patterns** (`02-design-patterns/02-structural-patterns.md`)
   - Adapter, Decorator, Facade, Composite, Proxy, Bridge, Flyweight
6. **Behavioral Patterns** (`02-design-patterns/03-behavioral-patterns.md`)
   - Strategy, Observer, Command, State, Template Method, Iterator, Chain of Responsibility

*Each pattern includes: Intent, When to Use, Structure, C++ Implementation, Real-world Examples*

### Phase 3: Easy Problems (Week 5-6)
- Parking Lot System
- ATM Machine
- Library Management System
- Vending Machine
- Tic Tac Toe
- Traffic Signal System
- Logger System
- URL Shortener
- Coffee Machine
- Snakes and Ladders
- Deck of Cards
- URL Shortener

### Phase 4: Medium Problems (Week 7-9)
- Elevator System
- Hotel Booking System
- Movie Ticket Booking System
- Car Rental System
- LRU Cache
- Restaurant Management System
- Online Shopping System
- File System Design
- Chess Game
- Social Media Feed
- Splitwise (Expense Sharing)
- Music Streaming Service

### Phase 5: Advanced Problems (Week 10-12)
- Ride Sharing System (Uber/Lyft)
- Food Delivery System (DoorDash/Swiggy)
- Stock Trading System
- Payment Gateway
- Notification System
- Meeting Scheduler (Calendar)
- Rate Limiter

## 🔥 Problem Categories

### By Difficulty
- **Easy (8)**: Focus on basic OOP, single responsibility, simple state management
- **Medium (10)**: Multiple design patterns, complex interactions, concurrency
- **Hard (7)**: Real-world systems, scalability, distributed considerations

### By Concepts
- **State Management**: ATM, Elevator, Traffic Signal, Vending Machine
- **Booking/Reservation Systems**: Hotel, Movie Theater, Restaurant, Meeting Rooms
- **Matching Algorithms**: Ride Sharing, Food Delivery
- **Caching**: LRU Cache
- **Real-time Systems**: Notification, Stock Trading, Social Media Feed
- **Games**: Chess, Tic Tac Toe
- **System Design**: File System, Payment Gateway, Rate Limiter

## 📝 What Each Problem Includes

1. **Problem Statement** - Clear requirements and constraints
2. **Concepts Involved** - OOP principles, design patterns used
3. **Difficulty Level** - Easy/Medium/Hard with time estimate
4. **ASCII Diagrams** - Class diagrams, sequence flows
5. **Complete C++ Implementation** - Production-quality code
6. **Test Cases** - Unit tests and usage examples
7. **Follow-up Questions** - Common interview extensions

## 🛠️ Prerequisites

- Strong C++11/14/17 knowledge
- Understanding of OOP concepts
- Basic knowledge of data structures
- 7+ years of software development experience

## 🚀 Getting Started

1. Start with `01-concepts/` to review OOP, SOLID, and UML
2. Study all 21 design patterns in `02-design-patterns/`
3. Solve problems in order: Easy → Medium → Hard
4. Each problem has complete working C++ code
5. Compile: `g++ -std=c++17 problem.cpp -o solution && ./solution`
6. Use `compile.sh` helper script for quick compilation

## 📊 Interview Preparation Timeline

- **2 weeks before**: Focus on Easy + Medium problems
- **1 week before**: Practice Hard problems, review patterns
- **2-3 days before**: Revise SOLID principles, common patterns
- **Day before**: Review your solved problems, practice whiteboarding

## 💡 Tips for LLD Interviews

1. **Clarify Requirements** - Ask about scale, users, features
2. **Start with Core Entities** - Identify main classes first
3. **Define Relationships** - Use proper OOP relationships
4. **Apply Design Patterns** - Use patterns naturally, don't force
5. **Write Clean Code** - Follow SOLID principles
6. **Think Extensibility** - Design for future changes
7. **Handle Edge Cases** - Thread safety, null checks, validation

## 📖 Additional Resources

- Design Patterns: Elements of Reusable Object-Oriented Software (GoF)
- Head First Design Patterns
- Clean Code by Robert C. Martin
- Effective C++ by Scott Meyers

## 🎯 Success Metrics

After completing this course, you should be able to:
- ✅ Design 25 real-world systems from scratch
- ✅ Apply 21 design patterns appropriately
- ✅ Write production-quality C++ code
- ✅ Explain trade-offs and design decisions
- ✅ Handle follow-up questions confidently
- ✅ Complete LLD interviews in 45-60 minutes
- ✅ Ace interviews at FAANG and top companies

---

**Let's begin your LLD mastery journey! 🚀**

