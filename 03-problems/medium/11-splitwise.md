# Problem 11: Splitwise (Expense Sharing System)

**Difficulty**: Medium  
**Time to Solve**: 45-50 minutes  
**Companies**: Splitwise, PayTM, PhonePe, Google Pay

## Problem Statement

Design an expense sharing application like Splitwise that supports:
1. Add users
2. Add expenses (equal, exact, percentage split)
3. Track balances between users
4. Settle balances
5. Group expenses
6. Show who owes whom

---

## Class Diagram

```
┌──────────────────┐
│   Splitwise      │
├──────────────────┤
│- users           │
│- expenses        │
│- balances        │
├──────────────────┤
│+ addExpense()    │
│+ showBalances()  │
│+ settleBalance() │
└──────┬───────────┘
       │
   ┌───┴────┬──────────┬──────────┐
   ▼        ▼          ▼          ▼
┌──────┐┌─────────┐┌────────┐┌────────┐
│User  ││ Expense ││Balance ││ Split  │
├──────┤├─────────┤├────────┤├────────┤
│-id   ││-amount  ││-from   ││-user   │
│-name ││-paidBy  ││-to     ││-amount │
│-email││-splits  ││-amount ││-type   │
└──────┘└─────────┘└────────┘└────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <memory>
#include <iomanip>
#include <cmath>

using namespace std;

// ============== Split Type ==============

enum class SplitType { EQUAL, EXACT, PERCENTAGE };

// ============== User ==============

class User {
private:
    string id;
    string name;
    string email;
    
public:
    User(const string& id, const string& name, const string& email)
        : id(id), name(name), email(email) {}
    
    string getId() const { return id; }
    string getName() const { return name; }
    string getEmail() const { return email; }
};

// ============== Split ==============

class Split {
protected:
    User* user;
    double amount;
    
public:
    Split(User* u) : user(u), amount(0) {}
    virtual ~Split() = default;
    
    User* getUser() const { return user; }
    double getAmount() const { return amount; }
    void setAmount(double amt) { amount = amt; }
    
    virtual SplitType getType() const = 0;
};

class EqualSplit : public Split {
public:
    EqualSplit(User* u) : Split(u) {}
    SplitType getType() const override { return SplitType::EQUAL; }
};

class ExactSplit : public Split {
public:
    ExactSplit(User* u, double amount) : Split(u) {
        this->amount = amount;
    }
    SplitType getType() const override { return SplitType::EXACT; }
};

class PercentSplit : public Split {
private:
    double percentage;
    
public:
    PercentSplit(User* u, double percent) : Split(u), percentage(percent) {}
    
    SplitType getType() const override { return SplitType::PERCENTAGE; }
    double getPercentage() const { return percentage; }
    
    void calculateAmount(double totalAmount) {
        amount = (totalAmount * percentage) / 100.0;
    }
};

// ============== Expense ==============

class Expense {
private:
    string id;
    double amount;
    User* paidBy;
    vector<unique_ptr<Split>> splits;
    string description;
    
    static int expenseCounter;
    
public:
    Expense(double amt, User* payer, vector<unique_ptr<Split>> spls, const string& desc)
        : amount(amt), paidBy(payer), splits(move(spls)), description(desc) {
        id = "EXP" + to_string(++expenseCounter);
    }
    
    string getId() const { return id; }
    double getAmount() const { return amount; }
    User* getPaidBy() const { return paidBy; }
    const vector<unique_ptr<Split>>& getSplits() const { return splits; }
    string getDescription() const { return description; }
    
    bool validate() {
        double totalSplitAmount = 0;
        
        for (auto& split : splits) {
            totalSplitAmount += split->getAmount();
        }
        
        // Check if split amounts match total amount (with small tolerance for floating point)
        return abs(totalSplitAmount - amount) < 0.01;
    }
};

int Expense::expenseCounter = 0;

// ============== Balance Sheet ==============

class BalanceSheet {
private:
    // balances[userA][userB] = amount means userA owes userB 'amount'
    map<string, map<string, double>> balances;
    
public:
    void addBalance(const string& user1, const string& user2, double amount) {
        if (amount == 0) return;
        
        balances[user1][user2] += amount;
        balances[user2][user1] -= amount;
    }
    
    double getBalance(const string& user1, const string& user2) {
        if (balances.find(user1) != balances.end()) {
            if (balances[user1].find(user2) != balances[user1].end()) {
                return balances[user1][user2];
            }
        }
        return 0;
    }
    
    void showBalances(User* user) {
        cout << "\n=== Balances for " << user->getName() << " ===" << endl;
        
        bool hasBalance = false;
        if (balances.find(user->getId()) != balances.end()) {
            for (const auto& [otherId, amount] : balances[user->getId()]) {
                if (abs(amount) > 0.01) {
                    hasBalance = true;
                    if (amount > 0) {
                        cout << "  You owe: $" << fixed << setprecision(2) << amount << endl;
                    } else {
                        cout << "  Owes you: $" << fixed << setprecision(2) << -amount << endl;
                    }
                }
            }
        }
        
        if (!hasBalance) {
            cout << "  No pending balances" << endl;
        }
    }
    
    void showAllBalances(const map<string, unique_ptr<User>>& users) {
        cout << "\n========== All Balances ==========" << endl;
        
        bool hasAnyBalance = false;
        for (const auto& [userId1, userBalances] : balances) {
            for (const auto& [userId2, amount] : userBalances) {
                if (amount > 0.01) {  // Only show positive balances (to avoid duplicates)
                    hasAnyBalance = true;
                    cout << users.at(userId1)->getName() << " owes " 
                         << users.at(userId2)->getName() << ": $" 
                         << fixed << setprecision(2) << amount << endl;
                }
            }
        }
        
        if (!hasAnyBalance) {
            cout << "All settled up! 🎉" << endl;
        }
        cout << "==================================\n" << endl;
    }
    
    void settleBalance(User* user1, User* user2) {
        double amount = getBalance(user1->getId(), user2->getId());
        
        if (abs(amount) < 0.01) {
            cout << "No balance to settle between " << user1->getName() 
                 << " and " << user2->getName() << endl;
            return;
        }
        
        if (amount > 0) {
            cout << user1->getName() << " paid $" << fixed << setprecision(2) 
                 << amount << " to " << user2->getName() << endl;
        } else {
            cout << user2->getName() << " paid $" << fixed << setprecision(2) 
                 << -amount << " to " << user1->getName() << endl;
        }
        
        balances[user1->getId()][user2->getId()] = 0;
        balances[user2->getId()][user1->getId()] = 0;
    }
};

// ============== Splitwise ==============

class Splitwise {
private:
    map<string, unique_ptr<User>> users;
    vector<unique_ptr<Expense>> expenses;
    BalanceSheet balanceSheet;
    
public:
    User* addUser(const string& id, const string& name, const string& email) {
        auto user = make_unique<User>(id, name, email);
        User* userPtr = user.get();
        users[id] = move(user);
        cout << "✓ User added: " << name << endl;
        return userPtr;
    }
    
    User* getUser(const string& id) {
        if (users.find(id) != users.end()) {
            return users[id].get();
        }
        return nullptr;
    }
    
    void addExpense(SplitType type, double amount, User* paidBy, 
                    vector<User*> participants, vector<double> values, 
                    const string& description) {
        
        vector<unique_ptr<Split>> splits;
        
        switch (type) {
            case SplitType::EQUAL: {
                double splitAmount = amount / participants.size();
                for (User* user : participants) {
                    auto split = make_unique<EqualSplit>(user);
                    split->setAmount(splitAmount);
                    splits.push_back(move(split));
                }
                break;
            }
            
            case SplitType::EXACT: {
                for (size_t i = 0; i < participants.size(); i++) {
                    auto split = make_unique<ExactSplit>(participants[i], values[i]);
                    splits.push_back(move(split));
                }
                break;
            }
            
            case SplitType::PERCENTAGE: {
                for (size_t i = 0; i < participants.size(); i++) {
                    auto split = make_unique<PercentSplit>(participants[i], values[i]);
                    dynamic_cast<PercentSplit*>(split.get())->calculateAmount(amount);
                    splits.push_back(move(split));
                }
                break;
            }
        }
        
        auto expense = make_unique<Expense>(amount, paidBy, move(splits), description);
        
        if (!expense->validate()) {
            cout << "❌ Invalid expense: amounts don't match!" << endl;
            return;
        }
        
        // Update balances
        for (const auto& split : expense->getSplits()) {
            if (split->getUser()->getId() != paidBy->getId()) {
                balanceSheet.addBalance(split->getUser()->getId(), 
                                       paidBy->getId(), 
                                       split->getAmount());
            }
        }
        
        cout << "✓ Expense added: " << description << " ($" << fixed 
             << setprecision(2) << amount << ")" << endl;
        expenses.push_back(move(expense));
    }
    
    void showBalances(User* user) {
        balanceSheet.showBalances(user);
    }
    
    void showAllBalances() {
        balanceSheet.showAllBalances(users);
    }
    
    void settleBalance(User* user1, User* user2) {
        balanceSheet.settleBalance(user1, user2);
    }
};

// ============== Demo ==============

int main() {
    Splitwise app;
    
    cout << "========== Splitwise Demo ==========\n" << endl;
    
    // Add users
    User* alice = app.addUser("U1", "Alice", "alice@example.com");
    User* bob = app.addUser("U2", "Bob", "bob@example.com");
    User* charlie = app.addUser("U3", "Charlie", "charlie@example.com");
    User* diana = app.addUser("U4", "Diana", "diana@example.com");
    
    cout << endl;
    
    // Expense 1: Equal split
    cout << "=== Expense 1: Dinner (Equal Split) ===" << endl;
    app.addExpense(SplitType::EQUAL, 1000, alice, 
                   {alice, bob, charlie, diana}, {}, 
                   "Dinner at restaurant");
    
    app.showAllBalances();
    
    // Expense 2: Exact split
    cout << "\n=== Expense 2: Shopping (Exact Split) ===" << endl;
    app.addExpense(SplitType::EXACT, 1250, bob, 
                   {alice, bob, charlie}, {370, 880, 0}, 
                   "Shopping");
    
    app.showAllBalances();
    
    // Expense 3: Percentage split
    cout << "\n=== Expense 3: Trip (Percentage Split) ===" << endl;
    app.addExpense(SplitType::PERCENTAGE, 3000, charlie, 
                   {alice, bob, charlie, diana}, {40, 20, 20, 20}, 
                   "Weekend trip");
    
    app.showAllBalances();
    
    // Show individual balances
    app.showBalances(alice);
    app.showBalances(bob);
    
    // Settle some balances
    cout << "\n=== Settling Balances ===" << endl;
    app.settleBalance(bob, alice);
    
    app.showAllBalances();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Split Strategy Pattern**
- Base `Split` class with different implementations
- `EqualSplit`, `ExactSplit`, `PercentSplit`
- Easy to add new split types

### 2. **Balance Sheet**
- Maintains bidirectional balances
- Efficient lookup
- Handles settlement

### 3. **Validation**
- Ensure split amounts match total
- Prevent invalid expenses
- Clear error messages

---

## Follow-up Questions

**Q1: How to handle groups?**
```cpp
class Group {
    string id;
    string name;
    vector<User*> members;
    vector<Expense*> expenses;
    
    void addMember(User* user);
    void addExpense(Expense* expense);
};
```

**Q2: How to optimize settle-up (minimize transactions)?**
```cpp
class SettlementOptimizer {
    vector<Transaction> optimizeSettlement(BalanceSheet& sheet) {
        // Use greedy algorithm or min-cost flow
        // to minimize number of transactions
    }
};
```

**Q3: How to add expense categories and analytics?**
```cpp
enum class Category { FOOD, TRAVEL, SHOPPING, UTILITIES, OTHER };

class Expense {
    Category category;
    time_t timestamp;
};

class Analytics {
    map<Category, double> getCategoryWiseExpenses(User* user);
    double getMonthlyExpense(User* user, int month);
};
```

---

## Compilation

```bash
g++ -std=c++17 splitwise.cpp -o splitwise
./splitwise
```

---

**Next**: `medium/12-music-streaming.md`

