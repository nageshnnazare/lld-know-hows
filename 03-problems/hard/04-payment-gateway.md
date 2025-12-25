# Problem 4: Payment Gateway

**Difficulty**: Hard  
**Time to Solve**: 70-90 minutes  
**Companies**: PayPal, Stripe, Square, Razorpay

## Problem Statement

Design a payment gateway that supports:
1. Multiple payment methods (Credit Card, Debit Card, UPI, Wallet)
2. Transaction processing
3. Refunds and chargebacks
4. Fraud detection
5. Multi-currency support
6. Payment retry logic

---

## Class Diagram

```
┌────────────────────────┐
│  PaymentGateway        │
├────────────────────────┤
│ - merchants            │
│ - transactions         │
│ - paymentProcessors    │
│ - fraudDetector        │
├────────────────────────┤
│ + processPayment()     │
│ + refundPayment()      │
│ + verifyTransaction()  │
│ + handleCallback()     │
└──────┬─────────────────┘
       │
   ┌───┴────┬──────────┬──────────┬──────────┐
   ▼        ▼          ▼          ▼          ▼
┌──────────┐ ┌─────────────┐ ┌──────────┐ ┌──────────┐
│ Merchant │ │ Transaction │ │ Payment  │ │  Fraud   │
│          │ │             │ │Processor │ │ Detector │
├──────────┤ ├─────────────┤ ├──────────┤ ├──────────┤
│- apiKey  │ │- amount     │ │- type    │ │- rules   │
│- balance │ │- status     │ │- process │ │- score   │
└──────────┘ └─────────────┘ └──────────┘ └──────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <map>
#include <memory>
#include <string>
#include <ctime>
#include <random>
#include <iomanip>
#include <sstream>

using namespace std;

// ============== Enums ==============

enum class PaymentMethod { CREDIT_CARD, DEBIT_CARD, UPI, WALLET, NET_BANKING };
enum class TransactionStatus { PENDING, SUCCESS, FAILED, REFUNDED, CHARGEBACK };
enum class Currency { USD, EUR, GBP, INR };

// ============== Payment Method Details ==============

class PaymentDetails {
protected:
    PaymentMethod method;
    
public:
    PaymentDetails(PaymentMethod m) : method(m) {}
    virtual ~PaymentDetails() = default;
    
    PaymentMethod getMethod() const { return method; }
    virtual string getDisplayInfo() const = 0;
    virtual bool validate() const = 0;
};

class CardDetails : public PaymentDetails {
private:
    string cardNumber;
    string cardholderName;
    string expiryDate;
    string cvv;
    
public:
    CardDetails(PaymentMethod m, const string& num, const string& name,
               const string& exp, const string& c)
        : PaymentDetails(m), cardNumber(num), cardholderName(name),
          expiryDate(exp), cvv(c) {}
    
    string getCardNumber() const { return cardNumber; }
    
    string getDisplayInfo() const override {
        return "Card ending in " + cardNumber.substr(cardNumber.length() - 4);
    }
    
    bool validate() const override {
        // Basic validation
        return cardNumber.length() >= 13 && cardNumber.length() <= 19 &&
               cvv.length() >= 3 && cvv.length() <= 4;
    }
};

class UPIDetails : public PaymentDetails {
private:
    string upiId;
    
public:
    UPIDetails(const string& id) : PaymentDetails(PaymentMethod::UPI), upiId(id) {}
    
    string getDisplayInfo() const override {
        return "UPI: " + upiId;
    }
    
    bool validate() const override {
        return upiId.find('@') != string::npos;
    }
};

// ============== Money ==============

class Money {
private:
    double amount;
    Currency currency;
    
public:
    Money(double amt = 0, Currency cur = Currency::USD)
        : amount(amt), currency(cur) {}
    
    double getAmount() const { return amount; }
    Currency getCurrency() const { return currency; }
    
    string toString() const {
        string symbol;
        switch (currency) {
            case Currency::USD: symbol = "$"; break;
            case Currency::EUR: symbol = "€"; break;
            case Currency::GBP: symbol = "£"; break;
            case Currency::INR: symbol = "₹"; break;
        }
        
        stringstream ss;
        ss << symbol << fixed << setprecision(2) << amount;
        return ss.str();
    }
    
    Money convert(Currency targetCurrency) const {
        // Simplified conversion rates
        static map<pair<Currency, Currency>, double> rates = {
            {{Currency::USD, Currency::INR}, 83.0},
            {{Currency::USD, Currency::EUR}, 0.92},
            {{Currency::USD, Currency::GBP}, 0.79},
            {{Currency::INR, Currency::USD}, 0.012},
            // ... more rates
        };
        
        if (currency == targetCurrency) return *this;
        
        auto it = rates.find({currency, targetCurrency});
        if (it != rates.end()) {
            return Money(amount * it->second, targetCurrency);
        }
        
        return *this;
    }
};

// ============== Transaction ==============

class Transaction {
private:
    string transactionId;
    string merchantId;
    string customerId;
    Money amount;
    unique_ptr<PaymentDetails> paymentDetails;
    TransactionStatus status;
    time_t timestamp;
    string description;
    double fraudScore;
    static int transactionCounter;
    
public:
    Transaction(const string& mId, const string& cId, const Money& amt,
               unique_ptr<PaymentDetails> details, const string& desc)
        : merchantId(mId), customerId(cId), amount(amt),
          paymentDetails(move(details)), status(TransactionStatus::PENDING),
          timestamp(time(nullptr)), description(desc), fraudScore(0) {
        
        // Generate transaction ID
        transactionId = "TXN" + to_string(++transactionCounter);
    }
    
    string getId() const { return transactionId; }
    string getMerchantId() const { return merchantId; }
    string getCustomerId() const { return customerId; }
    Money getAmount() const { return amount; }
    TransactionStatus getStatus() const { return status; }
    double getFraudScore() const { return fraudScore; }
    time_t getTimestamp() const { return timestamp; }
    
    void setStatus(TransactionStatus s) { status = s; }
    void setFraudScore(double score) { fraudScore = score; }
    
    PaymentDetails* getPaymentDetails() const { return paymentDetails.get(); }
    
    bool isSuccess() const { return status == TransactionStatus::SUCCESS; }
    
    void display() const {
        cout << "\n========== TRANSACTION ==========" << endl;
        cout << "ID: " << transactionId << endl;
        cout << "Merchant: " << merchantId << endl;
        cout << "Amount: " << amount.toString() << endl;
        cout << "Method: " << paymentDetails->getDisplayInfo() << endl;
        cout << "Status: " << (int)status << endl;
        cout << "Description: " << description << endl;
        
        char timeStr[20];
        struct tm* timeinfo = localtime(&timestamp);
        strftime(timeStr, sizeof(timeStr), "%Y-%m-%d %H:%M:%S", timeinfo);
        cout << "Time: " << timeStr << endl;
        
        if (fraudScore > 0) {
            cout << "Fraud Score: " << fraudScore << "/100" << endl;
        }
        cout << "================================\n" << endl;
    }
};

int Transaction::transactionCounter = 0;

// ============== Fraud Detector ==============

class FraudDetector {
private:
    map<string, vector<time_t>> customerTransactions;
    map<string, double> customerRiskScores;
    
public:
    double calculateFraudScore(Transaction* transaction) {
        double score = 0;
        
        // Check amount (high amounts are riskier)
        double amount = transaction->getAmount().getAmount();
        if (amount > 1000) score += 20;
        if (amount > 5000) score += 30;
        
        // Check transaction frequency
        string customerId = transaction->getCustomerId();
        time_t now = time(nullptr);
        
        auto& transactions = customerTransactions[customerId];
        
        // Count transactions in last hour
        int recentCount = 0;
        for (time_t t : transactions) {
            if (now - t < 3600) { // 1 hour
                recentCount++;
            }
        }
        
        if (recentCount > 3) score += 25;
        if (recentCount > 5) score += 40;
        
        transactions.push_back(now);
        
        // Check customer risk score
        if (customerRiskScores.find(customerId) != customerRiskScores.end()) {
            score += customerRiskScores[customerId];
        }
        
        return min(score, 100.0);
    }
    
    bool shouldBlock(double fraudScore) {
        return fraudScore >= 75;
    }
    
    bool requiresVerification(double fraudScore) {
        return fraudScore >= 50 && fraudScore < 75;
    }
};

// ============== Payment Processor ==============

class PaymentProcessor {
public:
    virtual ~PaymentProcessor() = default;
    
    virtual bool processPayment(Transaction* transaction) {
        // Simulate payment processing
        random_device rd;
        mt19937 gen(rd());
        uniform_int_distribution<> dis(1, 100);
        
        int success = dis(gen);
        
        // 95% success rate
        return success <= 95;
    }
    
    virtual bool refund(Transaction* transaction) {
        if (transaction->isSuccess()) {
            transaction->setStatus(TransactionStatus::REFUNDED);
            return true;
        }
        return false;
    }
};

class CardProcessor : public PaymentProcessor {
public:
    bool processPayment(Transaction* transaction) override {
        CardDetails* card = dynamic_cast<CardDetails*>(transaction->getPaymentDetails());
        
        if (!card || !card->validate()) {
            return false;
        }
        
        cout << "Processing card payment..." << endl;
        return PaymentProcessor::processPayment(transaction);
    }
};

class UPIProcessor : public PaymentProcessor {
public:
    bool processPayment(Transaction* transaction) override {
        UPIDetails* upi = dynamic_cast<UPIDetails*>(transaction->getPaymentDetails());
        
        if (!upi || !upi->validate()) {
            return false;
        }
        
        cout << "Processing UPI payment..." << endl;
        return PaymentProcessor::processPayment(transaction);
    }
};

// ============== Merchant ==============

class Merchant {
private:
    string merchantId;
    string name;
    string apiKey;
    double balance;
    vector<string> transactionHistory;
    
public:
    Merchant(const string& id, const string& n)
        : merchantId(id), name(n), balance(0) {
        // Generate API key
        apiKey = "sk_live_" + id;
    }
    
    string getId() const { return merchantId; }
    string getName() const { return name; }
    string getApiKey() const { return apiKey; }
    double getBalance() const { return balance; }
    
    void creditAmount(double amount) {
        balance += amount;
    }
    
    void debitAmount(double amount) {
        balance -= amount;
    }
    
    void addTransaction(const string& transactionId) {
        transactionHistory.push_back(transactionId);
    }
    
    void displayInfo() const {
        cout << "\n========== MERCHANT ==========" << endl;
        cout << "ID: " << merchantId << endl;
        cout << "Name: " << name << endl;
        cout << "Balance: $" << fixed << setprecision(2) << balance << endl;
        cout << "Transactions: " << transactionHistory.size() << endl;
        cout << "==============================\n" << endl;
    }
};

// ============== Payment Gateway ==============

class PaymentGateway {
private:
    map<string, unique_ptr<Merchant>> merchants;
    map<string, unique_ptr<Transaction>> transactions;
    map<PaymentMethod, unique_ptr<PaymentProcessor>> processors;
    FraudDetector fraudDetector;
    
public:
    PaymentGateway() {
        // Initialize processors
        processors[PaymentMethod::CREDIT_CARD] = make_unique<CardProcessor>();
        processors[PaymentMethod::DEBIT_CARD] = make_unique<CardProcessor>();
        processors[PaymentMethod::UPI] = make_unique<UPIProcessor>();
    }
    
    Merchant* registerMerchant(const string& id, const string& name) {
        auto merchant = make_unique<Merchant>(id, name);
        Merchant* ptr = merchant.get();
        merchants[id] = move(merchant);
        
        cout << "✓ Merchant registered: " << name << endl;
        cout << "  API Key: " << ptr->getApiKey() << endl;
        
        return ptr;
    }
    
    Transaction* processPayment(const string& merchantId, const string& customerId,
                               const Money& amount, unique_ptr<PaymentDetails> details,
                               const string& description) {
        
        Merchant* merchant = getMerchant(merchantId);
        if (!merchant) {
            cout << "Invalid merchant!" << endl;
            return nullptr;
        }
        
        // Create transaction
        auto transaction = make_unique<Transaction>(merchantId, customerId, amount,
                                                    move(details), description);
        Transaction* txnPtr = transaction.get();
        
        cout << "\n=== Processing Payment ===" << endl;
        txnPtr->display();
        
        // Fraud detection
        double fraudScore = fraudDetector.calculateFraudScore(txnPtr);
        txnPtr->setFraudScore(fraudScore);
        
        if (fraudDetector.shouldBlock(fraudScore)) {
            cout << "❌ Transaction blocked due to high fraud score!" << endl;
            txnPtr->setStatus(TransactionStatus::FAILED);
            string txnId = txnPtr->getId();
            transactions[txnId] = move(transaction);
            return txnPtr;
        }
        
        if (fraudDetector.requiresVerification(fraudScore)) {
            cout << "⚠ Transaction requires additional verification" << endl;
            // In real system, trigger 2FA or manual review
        }
        
        // Process payment
        PaymentMethod method = txnPtr->getPaymentDetails()->getMethod();
        PaymentProcessor* processor = processors[method].get();
        
        if (processor->processPayment(txnPtr)) {
            txnPtr->setStatus(TransactionStatus::SUCCESS);
            
            // Credit merchant account (minus fees)
            double fee = amount.getAmount() * 0.029 + 0.30; // 2.9% + $0.30
            double netAmount = amount.getAmount() - fee;
            
            merchant->creditAmount(netAmount);
            merchant->addTransaction(txnPtr->getId());
            
            cout << "✓ Payment successful!" << endl;
            cout << "  Net amount to merchant: $" << fixed << setprecision(2) << netAmount << endl;
        } else {
            txnPtr->setStatus(TransactionStatus::FAILED);
            cout << "❌ Payment failed!" << endl;
        }
        
        string txnId = txnPtr->getId();
        transactions[txnId] = move(transaction);
        
        return txnPtr;
    }
    
    bool refundPayment(const string& transactionId) {
        Transaction* transaction = getTransaction(transactionId);
        
        if (!transaction) {
            cout << "Transaction not found!" << endl;
            return false;
        }
        
        if (transaction->getStatus() != TransactionStatus::SUCCESS) {
            cout << "Cannot refund non-successful transaction!" << endl;
            return false;
        }
        
        Merchant* merchant = getMerchant(transaction->getMerchantId());
        
        PaymentMethod method = transaction->getPaymentDetails()->getMethod();
        PaymentProcessor* processor = processors[method].get();
        
        if (processor->refund(transaction)) {
            // Debit merchant account
            double amount = transaction->getAmount().getAmount();
            merchant->debitAmount(amount);
            
            cout << "✓ Refund processed successfully!" << endl;
            return true;
        }
        
        cout << "❌ Refund failed!" << endl;
        return false;
    }
    
    Merchant* getMerchant(const string& merchantId) {
        auto it = merchants.find(merchantId);
        return (it != merchants.end()) ? it->second.get() : nullptr;
    }
    
    Transaction* getTransaction(const string& transactionId) {
        auto it = transactions.find(transactionId);
        return (it != transactions.end()) ? it->second.get() : nullptr;
    }
    
    void displayTransactionReport() const {
        cout << "\n========== TRANSACTION REPORT ==========" << endl;
        
        int success = 0, failed = 0, refunded = 0;
        double totalVolume = 0;
        
        for (const auto& [id, txn] : transactions) {
            switch (txn->getStatus()) {
                case TransactionStatus::SUCCESS:
                    success++;
                    totalVolume += txn->getAmount().getAmount();
                    break;
                case TransactionStatus::FAILED:
                    failed++;
                    break;
                case TransactionStatus::REFUNDED:
                    refunded++;
                    break;
                default:
                    break;
            }
        }
        
        cout << "Total Transactions: " << transactions.size() << endl;
        cout << "Success: " << success << " | Failed: " << failed
             << " | Refunded: " << refunded << endl;
        cout << "Total Volume: $" << fixed << setprecision(2) << totalVolume << endl;
        cout << "========================================\n" << endl;
    }
};

// ============== Demo ==============

int main() {
    PaymentGateway gateway;
    
    cout << "========== Payment Gateway Demo ==========\n" << endl;
    
    // Register merchants
    cout << "=== Merchant Registration ===" << endl;
    Merchant* merchant1 = gateway.registerMerchant("M001", "TechStore Inc");
    Merchant* merchant2 = gateway.registerMerchant("M002", "BookShop Ltd");
    
    cout << endl;
    
    // Process payments
    cout << "=== Payment 1: Credit Card ===" << endl;
    auto cardDetails = make_unique<CardDetails>(
        PaymentMethod::CREDIT_CARD,
        "4532123456789012",
        "John Doe",
        "12/25",
        "123"
    );
    
    Transaction* txn1 = gateway.processPayment(
        "M001",
        "C001",
        Money(99.99, Currency::USD),
        move(cardDetails),
        "Laptop purchase"
    );
    
    // Process UPI payment
    cout << "\n=== Payment 2: UPI ===" << endl;
    auto upiDetails = make_unique<UPIDetails>("alice@upi");
    
    Transaction* txn2 = gateway.processPayment(
        "M002",
        "C002",
        Money(29.99, Currency::USD),
        move(upiDetails),
        "Book purchase"
    );
    
    // High value transaction (fraud check)
    cout << "\n=== Payment 3: High Value (Fraud Check) ===" << endl;
    auto cardDetails2 = make_unique<CardDetails>(
        PaymentMethod::CREDIT_CARD,
        "5412345678901234",
        "Jane Smith",
        "06/26",
        "456"
    );
    
    Transaction* txn3 = gateway.processPayment(
        "M001",
        "C003",
        Money(5500.00, Currency::USD),
        move(cardDetails2),
        "High-end workstation"
    );
    
    // Display merchant info
    merchant1->displayInfo();
    
    // Refund
    if (txn1) {
        cout << "=== Processing Refund ===" << endl;
        gateway.refundPayment(txn1->getId());
        txn1->display();
        merchant1->displayInfo();
    }
    
    // Transaction report
    gateway.displayTransactionReport();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Payment Method Abstraction**
- Base `PaymentDetails` class
- Specific implementations for each method
- Validation per payment type

### 2. **Fraud Detection**
- Rule-based scoring
- Transaction frequency analysis
- Amount-based risk assessment

### 3. **Multi-currency Support**
- `Money` class with currency
- Conversion rates
- Display formatting

---

## Follow-up Questions

**Q1: How to implement retry logic?**
```cpp
class RetryManager {
    int maxRetries = 3;
    
    bool processWithRetry(Transaction* txn) {
        for (int i = 0; i < maxRetries; i++) {
            if (process(txn)) return true;
            sleep(exponentialBackoff(i));
        }
        return false;
    }
};
```

**Q2: How to handle webhooks?**
```cpp
class WebhookManager {
    void notifyMerchant(Transaction* txn) {
        string url = merchant->getWebhookUrl();
        sendHTTPPost(url, txn->toJSON());
    }
};
```

**Q3: How to implement 3D Secure?**
```cpp
class ThreeDSecure {
    string redirectUrl;
    bool verifyWithBank(CardDetails* card);
    void handleCallback(string token);
};
```

---

## Compilation

```bash
g++ -std=c++17 payment_gateway.cpp -o payment
./payment
```

---

**Next**: `hard/05-notification-system.md`

