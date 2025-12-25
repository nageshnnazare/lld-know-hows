# Problem 2: ATM Machine System

**Difficulty**: Easy  
**Time to Solve**: 30-35 minutes  
**Companies**: Amazon, JP Morgan, Bank of America

## Problem Statement

Design an ATM machine system that can:
1. Authenticate users with card and PIN
2. Check balance
3. Withdraw cash
4. Deposit cash
5. Transfer money between accounts
6. Handle cash denomination management
7. Transaction history

### Requirements

**Functional Requirements**:
- Card authentication with PIN
- Balance inquiry
- Cash withdrawal (check balance, denomination)
- Cash deposit
- Money transfer
- Print transaction receipt
- Handle insufficient funds
- Manage cash inventory

**Non-Functional Requirements**:
- Secure PIN handling
- Thread-safe operations
- State management (Idle, CardInserted, PinEntered, etc.)
- Transaction logging

---

## Concepts Involved

1. **Design Patterns**: 
   - **State Pattern** (ATM states)
   - **Strategy Pattern** (Transaction types)
   - **Singleton** (ATM instance)
2. **OOP**: Polymorphism, Encapsulation
3. **State Machine**: Different ATM states
4. **SOLID**: SRP, OCP

---

## State Diagram

```
     ┌──────────┐
     │   IDLE   │◄───────────────────┐
     └────┬─────┘                    │
          │ insertCard()             │
          ▼                          │
  ┌────────────────┐                 │
  │ CARD_INSERTED  │                 │
  └────┬───────────┘                 │
       │ enterPIN()                  │
       ▼                             │
  ┌────────────────┐                 │
  │ PIN_VERIFIED   │                 │
  └────┬───────────┘                 │
       │ selectTransaction()         │
       ▼                             │
  ┌────────────────┐                 │
  │  TRANSACTION   │                 │
  │  IN_PROGRESS   │                 │
  └────┬───────────┘                 │
       │ complete/cancel             │
       └─────────────────────────────┘
```

---

## Class Diagram

```
┌────────────────────┐
│   ATMMachine       │ ◄──── Singleton
├────────────────────┤
│ - state: ATMState* │
│ - cashInventory    │
│ - currentCard: Card│
├────────────────────┤
│ + insertCard()     │
│ + enterPIN()       │
│ + selectTransaction│
│ +executeTransaction│
└──────────┬─────────┘
           │
           ▼
┌────────────────────┐
│     ATMState       │ ◄──── State Pattern
├────────────────────┤
│ + insertCard()     │
│ + enterPIN()       │
│ + selectTransaction│
│ +executeTransaction│
└──────────┬─────────┘
           │
    ┌──────┴──────┬──────────┬───────────┐
    ▼             ▼          ▼           ▼
┌────────┐  ┌──────────┐ ┌─────────┐ ┌──────────┐
│IdleState│ │CardState │ │PinState │ │Transaction│
│        │  │          │ │         │ │  State   │
└────────┘  └──────────┘ └─────────┘ └──────────┘

┌────────────────────┐
│   Transaction      │ ◄──── Strategy Pattern
├────────────────────┤
│ + execute()        │
└──────────┬─────────┘
           │
    ┌──────┴──────┬──────────┬───────────┐
    ▼             ▼          ▼           ▼
┌─────────┐  ┌─────────┐ ┌─────────┐ ┌─────────┐
│Withdraw │  │ Deposit │ │ Balance │ │Transfer │
└─────────┘  └─────────┘ └─────────┘ └─────────┘

┌────────────────────┐
│     Card           │
├────────────────────┤
│ - cardNumber       │
│ - pin: string      │
│ - account: Account*│
├────────────────────┤
│ + validatePIN()    │
└────────────────────┘

┌────────────────────┐
│    Account         │
├────────────────────┤
│ - accountNumber    │
│ - balance: double  │
│ - transactions     │
├────────────────────┤
│ + debit()          │
│ + credit()         │
│ + getBalance()     │
└────────────────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <unordered_map>
#include <ctime>
#include <iomanip>

using namespace std;

// Forward declarations
class ATMState;
class Card;

// ============== Transaction Record ==============

class TransactionRecord {
private:
    string transactionId;
    string type;
    double amount;
    time_t timestamp;
    static int counter;
    
public:
    TransactionRecord(const string& t, double amt) 
        : type(t), amount(amt), timestamp(time(nullptr)) {
        transactionId = "TXN" + to_string(++counter);
    }
    
    void display() const {
        char timeStr[26];
        ctime_r(&timestamp, timeStr);
        cout << transactionId << " | " << type << " | $" 
             << fixed << setprecision(2) << amount << " | " << timeStr;
    }
    
    string getType() const { return type; }
    double getAmount() const { return amount; }
};

int TransactionRecord::counter = 0;

// ============== Account ==============

class Account {
private:
    string accountNumber;
    string holderName;
    double balance;
    vector<TransactionRecord> transactions;
    
public:
    Account(const string& accNum, const string& name, double initialBalance)
        : accountNumber(accNum), holderName(name), balance(initialBalance) {}
    
    bool debit(double amount) {
        if (amount > balance) {
            cout << "Insufficient funds!" << endl;
            return false;
        }
        balance -= amount;
        transactions.emplace_back("DEBIT", amount);
        return true;
    }
    
    void credit(double amount) {
        balance += amount;
        transactions.emplace_back("CREDIT", amount);
    }
    
    double getBalance() const { return balance; }
    string getAccountNumber() const { return accountNumber; }
    string getHolderName() const { return holderName; }
    
    void printStatement() const {
        cout << "\n========== ACCOUNT STATEMENT ==========" << endl;
        cout << "Account: " << accountNumber << endl;
        cout << "Holder: " << holderName << endl;
        cout << "Balance: $" << fixed << setprecision(2) << balance << endl;
        cout << "\nRecent Transactions:" << endl;
        int count = min(5, (int)transactions.size());
        for (int i = transactions.size() - count; i < transactions.size(); i++) {
            transactions[i].display();
        }
        cout << "======================================\n" << endl;
    }
};

// ============== Card ==============

class Card {
private:
    string cardNumber;
    string pin;
    Account* account;
    
public:
    Card(const string& num, const string& p, Account* acc)
        : cardNumber(num), pin(p), account(acc) {}
    
    bool validatePIN(const string& inputPin) const {
        return pin == inputPin;
    }
    
    Account* getAccount() const { return account; }
    string getCardNumber() const { return cardNumber; }
};

// ============== Cash Denomination ==============

class CashInventory {
private:
    unordered_map<int, int> denominations; // denomination -> count
    
public:
    CashInventory() {
        // Initialize with some cash
        denominations[100] = 10;
        denominations[50] = 20;
        denominations[20] = 50;
        denominations[10] = 100;
        denominations[5] = 200;
    }
    
    bool hasSufficientCash(double amount) const {
        double available = 0;
        for (const auto& [denom, count] : denominations) {
            available += denom * count;
        }
        return available >= amount;
    }
    
    bool dispenseCash(double amount) {
        if (!hasSufficientCash(amount)) {
            cout << "ATM has insufficient cash!" << endl;
            return false;
        }
        
        unordered_map<int, int> toDispense;
        double remaining = amount;
        
        // Greedy approach: Start with largest denomination
        vector<int> denoms = {100, 50, 20, 10, 5};
        
        for (int denom : denoms) {
            if (remaining >= denom && denominations[denom] > 0) {
                int count = min((int)(remaining / denom), denominations[denom]);
                toDispense[denom] = count;
                remaining -= count * denom;
            }
        }
        
        if (remaining > 0) {
            cout << "Cannot dispense exact amount!" << endl;
            return false;
        }
        
        // Update inventory
        for (const auto& [denom, count] : toDispense) {
            denominations[denom] -= count;
        }
        
        cout << "\nCash Dispensed:" << endl;
        for (const auto& [denom, count] : toDispense) {
            cout << "$" << denom << " x " << count << " = $" << (denom * count) << endl;
        }
        
        return true;
    }
    
    void addCash(int denomination, int count) {
        denominations[denomination] += count;
    }
    
    void displayInventory() const {
        cout << "\nCash Inventory:" << endl;
        double total = 0;
        for (const auto& [denom, count] : denominations) {
            cout << "$" << denom << " x " << count << " = $" << (denom * count) << endl;
            total += denom * count;
        }
        cout << "Total: $" << total << endl;
    }
};

// ============== Transaction Interface ==============

class Transaction {
public:
    virtual ~Transaction() = default;
    virtual bool execute(Account* account, double amount) = 0;
    virtual string getType() const = 0;
};

class WithdrawTransaction : public Transaction {
private:
    CashInventory* cashInventory;
    
public:
    WithdrawTransaction(CashInventory* inventory) : cashInventory(inventory) {}
    
    bool execute(Account* account, double amount) override {
        if (account->debit(amount)) {
            return cashInventory->dispenseCash(amount);
        }
        return false;
    }
    
    string getType() const override { return "WITHDRAW"; }
};

class DepositTransaction : public Transaction {
private:
    CashInventory* cashInventory;
    
public:
    DepositTransaction(CashInventory* inventory) : cashInventory(inventory) {}
    
    bool execute(Account* account, double amount) override {
        account->credit(amount);
        // Assume we add the deposited cash to inventory
        // In reality, you'd ask for denomination breakdown
        cashInventory->addCash(20, amount / 20); // Simplified
        cout << "Deposited $" << amount << " successfully!" << endl;
        return true;
    }
    
    string getType() const override { return "DEPOSIT"; }
};

class BalanceInquiryTransaction : public Transaction {
public:
    bool execute(Account* account, double amount) override {
        cout << "\nCurrent Balance: $" << fixed << setprecision(2) 
             << account->getBalance() << endl;
        return true;
    }
    
    string getType() const override { return "BALANCE_INQUIRY"; }
};

// ============== ATM States ==============

class ATMMachine; // Forward declaration

class ATMState {
public:
    virtual ~ATMState() = default;
    virtual void insertCard(ATMMachine* atm, Card* card) = 0;
    virtual void enterPIN(ATMMachine* atm, const string& pin) = 0;
    virtual void selectTransaction(ATMMachine* atm, Transaction* transaction, double amount) = 0;
    virtual void ejectCard(ATMMachine* atm) = 0;
    virtual string getStateName() const = 0;
};

class IdleState : public ATMState {
public:
    void insertCard(ATMMachine* atm, Card* card) override;
    
    void enterPIN(ATMMachine* atm, const string& pin) override {
        cout << "Please insert card first!" << endl;
    }
    
    void selectTransaction(ATMMachine* atm, Transaction* transaction, double amount) override {
        cout << "Please insert card first!" << endl;
    }
    
    void ejectCard(ATMMachine* atm) override {
        cout << "No card inserted!" << endl;
    }
    
    string getStateName() const override { return "IDLE"; }
};

class CardInsertedState : public ATMState {
public:
    void insertCard(ATMMachine* atm, Card* card) override {
        cout << "Card already inserted!" << endl;
    }
    
    void enterPIN(ATMMachine* atm, const string& pin) override;
    
    void selectTransaction(ATMMachine* atm, Transaction* transaction, double amount) override {
        cout << "Please enter PIN first!" << endl;
    }
    
    void ejectCard(ATMMachine* atm) override;
    
    string getStateName() const override { return "CARD_INSERTED"; }
};

class PINVerifiedState : public ATMState {
public:
    void insertCard(ATMMachine* atm, Card* card) override {
        cout << "Card already inserted!" << endl;
    }
    
    void enterPIN(ATMMachine* atm, const string& pin) override {
        cout << "PIN already verified!" << endl;
    }
    
    void selectTransaction(ATMMachine* atm, Transaction* transaction, double amount) override;
    
    void ejectCard(ATMMachine* atm) override;
    
    string getStateName() const override { return "PIN_VERIFIED"; }
};

// ============== ATM Machine ==============

class ATMMachine {
private:
    ATMState* currentState;
    Card* currentCard;
    CashInventory cashInventory;
    
    unique_ptr<IdleState> idleState;
    unique_ptr<CardInsertedState> cardInsertedState;
    unique_ptr<PINVerifiedState> pinVerifiedState;
    
public:
    ATMMachine() : currentCard(nullptr) {
        idleState = make_unique<IdleState>();
        cardInsertedState = make_unique<CardInsertedState>();
        pinVerifiedState = make_unique<PINVerifiedState>();
        
        currentState = idleState.get();
    }
    
    void setState(ATMState* state) {
        cout << "\n[ATM State: " << currentState->getStateName() 
             << " -> " << state->getStateName() << "]" << endl;
        currentState = state;
    }
    
    ATMState* getIdleState() { return idleState.get(); }
    ATMState* getCardInsertedState() { return cardInsertedState.get(); }
    ATMState* getPINVerifiedState() { return pinVerifiedState.get(); }
    
    void setCurrentCard(Card* card) { currentCard = card; }
    Card* getCurrentCard() const { return currentCard; }
    CashInventory& getCashInventory() { return cashInventory; }
    
    void insertCard(Card* card) {
        currentState->insertCard(this, card);
    }
    
    void enterPIN(const string& pin) {
        currentState->enterPIN(this, pin);
    }
    
    void selectTransaction(Transaction* transaction, double amount) {
        currentState->selectTransaction(this, transaction, amount);
    }
    
    void ejectCard() {
        currentState->ejectCard(this);
    }
    
    void displayStatus() {
        cout << "\n========== ATM STATUS ==========" << endl;
        cout << "State: " << currentState->getStateName() << endl;
        if (currentCard) {
            cout << "Card: " << currentCard->getCardNumber() << endl;
        }
        cashInventory.displayInventory();
        cout << "===============================\n" << endl;
    }
};

// ============== State Method Implementations ==============

void IdleState::insertCard(ATMMachine* atm, Card* card) {
    cout << "\nCard inserted: " << card->getCardNumber() << endl;
    atm->setCurrentCard(card);
    atm->setState(atm->getCardInsertedState());
}

void CardInsertedState::enterPIN(ATMMachine* atm, const string& pin) {
    Card* card = atm->getCurrentCard();
    if (card->validatePIN(pin)) {
        cout << "PIN verified successfully!" << endl;
        atm->setState(atm->getPINVerifiedState());
    } else {
        cout << "Invalid PIN! Card ejected." << endl;
        atm->setCurrentCard(nullptr);
        atm->setState(atm->getIdleState());
    }
}

void CardInsertedState::ejectCard(ATMMachine* atm) {
    cout << "Card ejected!" << endl;
    atm->setCurrentCard(nullptr);
    atm->setState(atm->getIdleState());
}

void PINVerifiedState::selectTransaction(ATMMachine* atm, Transaction* transaction, double amount) {
    cout << "\nProcessing " << transaction->getType() << "..." << endl;
    
    Card* card = atm->getCurrentCard();
    Account* account = card->getAccount();
    
    if (transaction->execute(account, amount)) {
        cout << "Transaction successful!" << endl;
    } else {
        cout << "Transaction failed!" << endl;
    }
    
    // After transaction, return to PIN verified state for more transactions
    // or user can eject card
}

void PINVerifiedState::ejectCard(ATMMachine* atm) {
    Card* card = atm->getCurrentCard();
    card->getAccount()->printStatement();
    cout << "\nCard ejected! Thank you!" << endl;
    atm->setCurrentCard(nullptr);
    atm->setState(atm->getIdleState());
}

// ============== Demo ==============

int main() {
    // Create accounts
    Account account1("ACC001", "John Doe", 5000.0);
    Account account2("ACC002", "Jane Smith", 3000.0);
    
    // Create cards
    Card card1("1234-5678-9012-3456", "1234", &account1);
    Card card2("9876-5432-1098-7654", "5678", &account2);
    
    // Create ATM
    ATMMachine atm;
    atm.displayStatus();
    
    // Transaction 1: Withdraw money
    cout << "\n=== Transaction 1: Withdraw ===" << endl;
    atm.insertCard(&card1);
    atm.enterPIN("1234");
    
    WithdrawTransaction withdraw(&atm.getCashInventory());
    atm.selectTransaction(&withdraw, 250.0);
    
    BalanceInquiryTransaction balance;
    atm.selectTransaction(&balance, 0);
    
    atm.ejectCard();
    
    // Transaction 2: Deposit money
    cout << "\n\n=== Transaction 2: Deposit ===" << endl;
    atm.insertCard(&card2);
    atm.enterPIN("5678");
    
    DepositTransaction deposit(&atm.getCashInventory());
    atm.selectTransaction(&deposit, 500.0);
    atm.selectTransaction(&balance, 0);
    
    atm.ejectCard();
    
    // Display final ATM status
    atm.displayStatus();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **State Pattern**
- ATM behavior changes based on state
- Each state handles transitions
- Clean separation of state logic

### 2. **Strategy Pattern for Transactions**
- Different transaction types
- Easy to add new transaction types
- Execute method polymorphism

### 3. **Cash Management**
- Greedy algorithm for denomination
- Inventory tracking
- Insufficient cash handling

---

## Follow-up Questions

**Q1: How to handle multiple ATM machines?**
- Remove Singleton, create ATM instances
- Central server manages accounts

**Q2: How to add biometric authentication?**
- Create `AuthenticationStrategy` interface
- Implement PINAuth, BiometricAuth, etc.

**Q3: How to handle network failures?**
- Add offline mode with transaction queue
- Sync when network restored

**Q4: How to prevent overdraft?**
- Already handled in `Account::debit()`
- Can add overdraft limit feature

---

## Compilation & Execution

```bash
g++ -std=c++17 atm_machine.cpp -o atm
./atm
```

---

**Next Problem**: `03-library-management-system.md`

