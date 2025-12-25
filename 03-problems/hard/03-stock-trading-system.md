# Problem 3: Stock Trading System

**Difficulty**: Hard  
**Time to Solve**: 80-100 minutes  
**Companies**: Bloomberg, Goldman Sachs, E-Trade, Robinhood

## Problem Statement

Design a stock trading platform that supports:
1. Order placement (Market, Limit orders)
2. Order matching engine
3. Portfolio management
4. Real-time price updates
5. Trade execution
6. Order book management

---

## Class Diagram

```
┌────────────────────────┐
│  TradingSystem         │
├────────────────────────┤
│ - stocks               │
│ - traders              │
│ - orderBooks           │
│ - matchingEngine       │
├────────────────────────┤
│ + placeOrder()         │
│ + cancelOrder()        │
│ + matchOrders()        │
│ + getMarketPrice()     │
│ + getPortfolio()       │
└──────┬─────────────────┘
       │
   ┌───┴────┬────────┬──────────┐
   ▼        ▼        ▼          ▼
┌────────┐┌────────┐┌──────────┐┌──────────┐
│ Stock  ││ Trader ││  Order   ││OrderBook │
├────────┤├────────┤├──────────┤├──────────┤
│- symbol││-portfolio│- type   ││- bids    │
│- price ││- balance│- quantity││- asks    │
│- volume││        ││- price   ││          │
└────────┘└────────┘└──────────┘└──────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <map>
#include <set>
#include <memory>
#include <string>
#include <queue>
#include <algorithm>
#include <ctime>
#include <iomanip>

using namespace std;

// ============== Enums ==============

enum class OrderType { MARKET, LIMIT };
enum class OrderSide { BUY, SELL };
enum class OrderStatus { PENDING, PARTIALLY_FILLED, FILLED, CANCELLED };

// ============== Stock ==============

class Stock {
private:
    string symbol;
    string companyName;
    double currentPrice;
    double openPrice;
    double highPrice;
    double lowPrice;
    long long volume;
    
public:
    Stock(const string& sym, const string& name, double price)
        : symbol(sym), companyName(name), currentPrice(price),
          openPrice(price), highPrice(price), lowPrice(price), volume(0) {}
    
    string getSymbol() const { return symbol; }
    string getCompanyName() const { return companyName; }
    double getCurrentPrice() const { return currentPrice; }
    long long getVolume() const { return volume; }
    
    void updatePrice(double price, long long qty) {
        currentPrice = price;
        volume += qty;
        
        if (price > highPrice) highPrice = price;
        if (price < lowPrice) lowPrice = price;
    }
    
    void display() const {
        cout << symbol << " - " << companyName << endl;
        cout << "Price: $" << fixed << setprecision(2) << currentPrice
             << " | Volume: " << volume << endl;
        cout << "High: $" << highPrice << " | Low: $" << lowPrice << endl;
    }
};

// ============== Order ==============

class Order {
private:
    string orderId;
    string traderId;
    string symbol;
    OrderType type;
    OrderSide side;
    int quantity;
    int filledQuantity;
    double price; // For limit orders
    OrderStatus status;
    time_t timestamp;
    static int orderCounter;
    
public:
    Order(const string& tId, const string& sym, OrderType t, OrderSide s,
          int qty, double p = 0)
        : traderId(tId), symbol(sym), type(t), side(s), quantity(qty),
          filledQuantity(0), price(p), status(OrderStatus::PENDING),
          timestamp(time(nullptr)) {
        orderId = "ORD" + to_string(++orderCounter);
    }
    
    string getId() const { return orderId; }
    string getTraderId() const { return traderId; }
    string getSymbol() const { return symbol; }
    OrderType getType() const { return type; }
    OrderSide getSide() const { return side; }
    int getQuantity() const { return quantity; }
    int getFilledQuantity() const { return filledQuantity; }
    int getRemainingQuantity() const { return quantity - filledQuantity; }
    double getPrice() const { return price; }
    OrderStatus getStatus() const { return status; }
    time_t getTimestamp() const { return timestamp; }
    
    void fill(int qty) {
        filledQuantity += qty;
        
        if (filledQuantity >= quantity) {
            status = OrderStatus::FILLED;
        } else if (filledQuantity > 0) {
            status = OrderStatus::PARTIALLY_FILLED;
        }
    }
    
    void cancel() {
        status = OrderStatus::CANCELLED;
    }
    
    void display() const {
        cout << orderId << " | " << symbol << " | "
             << (side == OrderSide::BUY ? "BUY" : "SELL") << " | "
             << (type == OrderType::MARKET ? "MARKET" : "LIMIT") << " | "
             << quantity << " @ $" << fixed << setprecision(2) << price << " | "
             << "Status: " << (int)status << endl;
    }
};

int Order::orderCounter = 0;

// ============== Trade ==============

class Trade {
private:
    string tradeId;
    string buyOrderId;
    string sellOrderId;
    string symbol;
    int quantity;
    double price;
    time_t timestamp;
    static int tradeCounter;
    
public:
    Trade(const string& buyId, const string& sellId, const string& sym,
          int qty, double p)
        : buyOrderId(buyId), sellOrderId(sellId), symbol(sym),
          quantity(qty), price(p), timestamp(time(nullptr)) {
        tradeId = "TRD" + to_string(++tradeCounter);
    }
    
    string getSymbol() const { return symbol; }
    int getQuantity() const { return quantity; }
    double getPrice() const { return price; }
    
    void display() const {
        cout << "Trade " << tradeId << ": " << quantity << " shares of "
             << symbol << " @ $" << fixed << setprecision(2) << price << endl;
    }
};

int Trade::tradeCounter = 0;

// ============== Portfolio ==============

class Portfolio {
private:
    map<string, int> holdings; // symbol -> quantity
    double cashBalance;
    
public:
    Portfolio(double initialCash) : cashBalance(initialCash) {}
    
    double getCashBalance() const { return cashBalance; }
    
    int getHolding(const string& symbol) const {
        auto it = holdings.find(symbol);
        return (it != holdings.end()) ? it->second : 0;
    }
    
    bool canBuy(int quantity, double price) const {
        return cashBalance >= (quantity * price);
    }
    
    bool canSell(const string& symbol, int quantity) const {
        return getHolding(symbol) >= quantity;
    }
    
    void buy(const string& symbol, int quantity, double price) {
        cashBalance -= quantity * price;
        holdings[symbol] += quantity;
    }
    
    void sell(const string& symbol, int quantity, double price) {
        cashBalance += quantity * price;
        holdings[symbol] -= quantity;
        
        if (holdings[symbol] == 0) {
            holdings.erase(symbol);
        }
    }
    
    double getTotalValue(const map<string, Stock*>& stocks) const {
        double total = cashBalance;
        
        for (const auto& [symbol, quantity] : holdings) {
            auto it = stocks.find(symbol);
            if (it != stocks.end()) {
                total += quantity * it->second->getCurrentPrice();
            }
        }
        
        return total;
    }
    
    void display(const map<string, Stock*>& stocks) const {
        cout << "\n========== PORTFOLIO ==========" << endl;
        cout << "Cash Balance: $" << fixed << setprecision(2) << cashBalance << endl;
        cout << "Holdings:" << endl;
        
        if (holdings.empty()) {
            cout << "  (none)" << endl;
        } else {
            for (const auto& [symbol, quantity] : holdings) {
                auto it = stocks.find(symbol);
                double currentPrice = (it != stocks.end()) ? it->second->getCurrentPrice() : 0;
                double value = quantity * currentPrice;
                cout << "  " << symbol << ": " << quantity << " shares @ $"
                     << currentPrice << " = $" << value << endl;
            }
        }
        
        cout << "Total Value: $" << getTotalValue(stocks) << endl;
        cout << "===============================\n" << endl;
    }
};

// ============== Order Book ==============

struct BidComparator {
    bool operator()(Order* a, Order* b) const {
        // Higher price first, then earlier timestamp
        if (a->getPrice() != b->getPrice()) {
            return a->getPrice() < b->getPrice();
        }
        return a->getTimestamp() > b->getTimestamp();
    }
};

struct AskComparator {
    bool operator()(Order* a, Order* b) const {
        // Lower price first, then earlier timestamp
        if (a->getPrice() != b->getPrice()) {
            return a->getPrice() > b->getPrice();
        }
        return a->getTimestamp() > b->getTimestamp();
    }
};

class OrderBook {
private:
    string symbol;
    priority_queue<Order*, vector<Order*>, BidComparator> bids;
    priority_queue<Order*, vector<Order*>, AskComparator> asks;
    
public:
    OrderBook(const string& sym) : symbol(sym) {}
    
    void addBid(Order* order) {
        bids.push(order);
    }
    
    void addAsk(Order* order) {
        asks.push(order);
    }
    
    Order* getTopBid() {
        while (!bids.empty() && bids.top()->getStatus() != OrderStatus::PENDING &&
               bids.top()->getStatus() != OrderStatus::PARTIALLY_FILLED) {
            bids.pop();
        }
        return bids.empty() ? nullptr : bids.top();
    }
    
    Order* getTopAsk() {
        while (!asks.empty() && asks.top()->getStatus() != OrderStatus::PENDING &&
               asks.top()->getStatus() != OrderStatus::PARTIALLY_FILLED) {
            asks.pop();
        }
        return asks.empty() ? nullptr : asks.top();
    }
    
    void display() const {
        cout << "\n========== ORDER BOOK: " << symbol << " ==========" << endl;
        
        // Note: Can't display priority_queue directly without copying
        cout << "Bids: " << bids.size() << " orders" << endl;
        cout << "Asks: " << asks.size() << " orders" << endl;
        
        cout << "=============================================\n" << endl;
    }
};

// ============== Trader ==============

class Trader {
private:
    string traderId;
    string name;
    Portfolio portfolio;
    
public:
    Trader(const string& id, const string& n, double initialCash)
        : traderId(id), name(n), portfolio(initialCash) {}
    
    string getId() const { return traderId; }
    string getName() const { return name; }
    Portfolio& getPortfolio() { return portfolio; }
    
    void displayInfo(const map<string, Stock*>& stocks) const {
        cout << "\n========== TRADER: " << name << " ==========" << endl;
        portfolio.display(stocks);
    }
};

// ============== Matching Engine ==============

class MatchingEngine {
public:
    vector<Trade> matchOrders(OrderBook& orderBook, Stock* stock) {
        vector<Trade> trades;
        
        while (true) {
            Order* bid = orderBook.getTopBid();
            Order* ask = orderBook.getTopAsk();
            
            if (!bid || !ask) break;
            
            // Check if prices match
            if (bid->getPrice() < ask->getPrice()) break;
            
            // Execute trade
            int tradeQty = min(bid->getRemainingQuantity(), ask->getRemainingQuantity());
            double tradePrice = ask->getPrice(); // Price discovery: ask price
            
            bid->fill(tradeQty);
            ask->fill(tradeQty);
            
            trades.emplace_back(bid->getId(), ask->getId(),
                               stock->getSymbol(), tradeQty, tradePrice);
            
            stock->updatePrice(tradePrice, tradeQty);
        }
        
        return trades;
    }
};

// ============== Trading System ==============

class TradingSystem {
private:
    map<string, unique_ptr<Stock>> stocks;
    map<string, unique_ptr<Trader>> traders;
    map<string, unique_ptr<OrderBook>> orderBooks;
    map<string, unique_ptr<Order>> orders;
    MatchingEngine matchingEngine;
    vector<Trade> tradeHistory;
    
public:
    Stock* addStock(const string& symbol, const string& name, double price) {
        auto stock = make_unique<Stock>(symbol, name, price);
        Stock* ptr = stock.get();
        stocks[symbol] = move(stock);
        
        orderBooks[symbol] = make_unique<OrderBook>(symbol);
        
        cout << "✓ Stock added: " << symbol << endl;
        return ptr;
    }
    
    Trader* registerTrader(const string& id, const string& name, double initialCash) {
        auto trader = make_unique<Trader>(id, name, initialCash);
        Trader* ptr = trader.get();
        traders[id] = move(trader);
        
        cout << "✓ Trader registered: " << name << endl;
        return ptr;
    }
    
    Order* placeOrder(Trader* trader, const string& symbol, OrderType type,
                     OrderSide side, int quantity, double limitPrice = 0) {
        
        Stock* stock = getStock(symbol);
        if (!stock) {
            cout << "Stock not found!" << endl;
            return nullptr;
        }
        
        // Validate trader has sufficient funds/shares
        Portfolio& portfolio = trader->getPortfolio();
        
        if (side == OrderSide::BUY) {
            double price = (type == OrderType::MARKET) ? stock->getCurrentPrice() : limitPrice;
            if (!portfolio.canBuy(quantity, price)) {
                cout << "Insufficient funds!" << endl;
                return nullptr;
            }
        } else {
            if (!portfolio.canSell(symbol, quantity)) {
                cout << "Insufficient shares!" << endl;
                return nullptr;
            }
        }
        
        // Create order
        double orderPrice = (type == OrderType::MARKET) ? stock->getCurrentPrice() : limitPrice;
        auto order = make_unique<Order>(trader->getId(), symbol, type, side, quantity, orderPrice);
        Order* orderPtr = order.get();
        string orderId = order->getId();
        
        orders[orderId] = move(order);
        
        // Add to order book
        OrderBook* orderBook = orderBooks[symbol].get();
        if (side == OrderSide::BUY) {
            orderBook->addBid(orderPtr);
        } else {
            orderBook->addAsk(orderPtr);
        }
        
        cout << "✓ Order placed: " << orderId << endl;
        orderPtr->display();
        
        // Try to match orders
        vector<Trade> trades = matchingEngine.matchOrders(*orderBook, stock);
        
        // Execute trades
        for (const Trade& trade : trades) {
            executeTrade(trade);
            tradeHistory.push_back(trade);
        }
        
        return orderPtr;
    }
    
    void executeTrade(const Trade& trade) {
        trade.display();
        
        // Update trader portfolios
        Order* buyOrder = getOrder(trade.buyOrderId);
        Order* sellOrder = getOrder(trade.sellOrderId);
        
        if (buyOrder && sellOrder) {
            Trader* buyer = getTrader(buyOrder->getTraderId());
            Trader* seller = getTrader(sellOrder->getTraderId());
            
            if (buyer && seller) {
                buyer->getPortfolio().buy(trade.getSymbol(), trade.getQuantity(), trade.getPrice());
                seller->getPortfolio().sell(trade.getSymbol(), trade.getQuantity(), trade.getPrice());
            }
        }
    }
    
    Stock* getStock(const string& symbol) {
        auto it = stocks.find(symbol);
        return (it != stocks.end()) ? it->second.get() : nullptr;
    }
    
    Trader* getTrader(const string& traderId) {
        auto it = traders.find(traderId);
        return (it != traders.end()) ? it->second.get() : nullptr;
    }
    
    Order* getOrder(const string& orderId) {
        auto it = orders.find(orderId);
        return (it != orders.end()) ? it->second.get() : nullptr;
    }
    
    void displayMarket() const {
        cout << "\n========== MARKET OVERVIEW ==========" << endl;
        for (const auto& [symbol, stock] : stocks) {
            stock->display();
            cout << "---" << endl;
        }
        cout << "=====================================\n" << endl;
    }
};

// ============== Demo ==============

int main() {
    TradingSystem system;
    
    cout << "========== Stock Trading System Demo ==========\n" << endl;
    
    // Add stocks
    cout << "=== Adding Stocks ===" << endl;
    Stock* aapl = system.addStock("AAPL", "Apple Inc.", 150.00);
    Stock* googl = system.addStock("GOOGL", "Alphabet Inc.", 2800.00);
    Stock* msft = system.addStock("MSFT", "Microsoft Corp.", 300.00);
    
    cout << endl;
    system.displayMarket();
    
    // Register traders
    cout << "=== Registering Traders ===" << endl;
    Trader* alice = system.registerTrader("T001", "Alice", 100000.0);
    Trader* bob = system.registerTrader("T002", "Bob", 100000.0);
    
    cout << endl;
    
    // Initial portfolios
    alice->displayInfo(system.getStock("AAPL") ? 
        map<string, Stock*>{{"AAPL", aapl}, {"GOOGL", googl}, {"MSFT", msft}} :
        map<string, Stock*>{});
    
    // Place orders
    cout << "=== Placing Orders ===" << endl;
    
    // Alice buys AAPL
    system.placeOrder(alice, "AAPL", OrderType::LIMIT, OrderSide::BUY, 100, 151.00);
    
    // Bob sells AAPL
    // First, give Bob some shares by buying at market
    system.placeOrder(bob, "AAPL", OrderType::MARKET, OrderSide::BUY, 100, 150.00);
    
    // Now Bob sells
    system.placeOrder(bob, "AAPL", OrderType::LIMIT, OrderSide::SELL, 50, 151.00);
    
    cout << "\n=== After Trading ===" << endl;
    alice->displayInfo(map<string, Stock*>{{"AAPL", aapl}, {"GOOGL", googl}, {"MSFT", msft}});
    bob->displayInfo(map<string, Stock*>{{"AAPL", aapl}, {"GOOGL", googl}, {"MSFT", msft}});
    
    system.displayMarket();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Order Matching**
- Priority queues for bids/asks
- Price-time priority
- Continuous matching

### 2. **Order Types**
- Market orders: immediate execution
- Limit orders: price-specified
- Partial fills supported

### 3. **Portfolio Management**
- Real-time balance tracking
- Position validation
- Value calculation

---

## Follow-up Questions

**Q1: How to implement stop-loss orders?**
```cpp
class StopLossOrder : public Order {
    double stopPrice;
    
    bool shouldTrigger(double currentPrice) {
        return (side == BUY && currentPrice >= stopPrice) ||
               (side == SELL && currentPrice <= stopPrice);
    }
};
```

**Q2: How to handle market data feeds?**
```cpp
class MarketDataFeed {
    void subscribeToTicker(string symbol, Callback cb);
    void publishTick(string symbol, double price, long volume);
};
```

**Q3: How to implement order book depth?**
```cpp
struct BookDepth {
    vector<pair<double, int>> bids; // price, quantity
    vector<pair<double, int>> asks;
    
    void display();
};
```

---

## Compilation

```bash
g++ -std=c++17 stock_trading.cpp -o trading
./trading
```

---

**Next**: `hard/04-payment-gateway.md`

