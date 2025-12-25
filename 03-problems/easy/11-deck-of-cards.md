# Problem 11: Deck of Cards

**Difficulty**: Easy  
**Time to Solve**: 20-25 minutes  
**Companies**: Amazon, Microsoft, Adobe

## Problem Statement

Design a deck of playing cards that supports:
1. Standard 52-card deck
2. Shuffle deck
3. Deal cards
4. Multiple card games (Poker, Blackjack)
5. Card comparison

---

## Class Diagram

```
┌──────────────────┐
│      Deck        │
├──────────────────┤
│- cards           │
├──────────────────┤
│+ shuffle()       │
│+ dealCard()      │
│+ reset()         │
└──────┬───────────┘
       │ contains
       ▼
┌──────────────────┐
│      Card        │
├──────────────────┤
│- suit            │
│- rank            │
├──────────────────┤
│+ getValue()      │
│+ display()       │
└──────────────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <algorithm>
#include <random>
#include <ctime>

using namespace std;

// ============== Enums ==============

enum class Suit { HEARTS, DIAMONDS, CLUBS, SPADES };
enum class Rank {
    TWO = 2, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN,
    JACK, QUEEN, KING, ACE
};

// ============== Card ==============

class Card {
private:
    Suit suit;
    Rank rank;
    
public:
    Card(Suit s, Rank r) : suit(s), rank(r) {}
    
    Suit getSuit() const { return suit; }
    Rank getRank() const { return rank; }
    
    int getValue() const {
        return static_cast<int>(rank);
    }
    
    string getSuitString() const {
        switch (suit) {
            case Suit::HEARTS: return "♥";
            case Suit::DIAMONDS: return "♦";
            case Suit::CLUBS: return "♣";
            case Suit::SPADES: return "♠";
        }
        return "";
    }
    
    string getRankString() const {
        switch (rank) {
            case Rank::TWO: return "2";
            case Rank::THREE: return "3";
            case Rank::FOUR: return "4";
            case Rank::FIVE: return "5";
            case Rank::SIX: return "6";
            case Rank::SEVEN: return "7";
            case Rank::EIGHT: return "8";
            case Rank::NINE: return "9";
            case Rank::TEN: return "10";
            case Rank::JACK: return "J";
            case Rank::QUEEN: return "Q";
            case Rank::KING: return "K";
            case Rank::ACE: return "A";
        }
        return "";
    }
    
    void display() const {
        cout << "[" << getRankString() << getSuitString() << "]";
    }
    
    bool operator<(const Card& other) const {
        return getValue() < other.getValue();
    }
};

// ============== Deck ==============

class Deck {
private:
    vector<Card> cards;
    int currentCardIndex;
    
public:
    Deck() : currentCardIndex(0) {
        initialize();
    }
    
    void initialize() {
        cards.clear();
        currentCardIndex = 0;
        
        // Create all 52 cards
        for (int s = 0; s < 4; s++) {
            Suit suit = static_cast<Suit>(s);
            for (int r = 2; r <= 14; r++) {
                Rank rank = static_cast<Rank>(r);
                cards.push_back(Card(suit, rank));
            }
        }
    }
    
    void shuffle() {
        random_device rd;
        mt19937 g(rd());
        std::shuffle(cards.begin(), cards.end(), g);
        currentCardIndex = 0;
        cout << "🔀 Deck shuffled!" << endl;
    }
    
    Card* dealCard() {
        if (currentCardIndex >= cards.size()) {
            cout << "⚠ No more cards in deck!" << endl;
            return nullptr;
        }
        return &cards[currentCardIndex++];
    }
    
    vector<Card*> dealCards(int count) {
        vector<Card*> dealt;
        for (int i = 0; i < count; i++) {
            Card* card = dealCard();
            if (card) {
                dealt.push_back(card);
            }
        }
        return dealt;
    }
    
    int remainingCards() const {
        return cards.size() - currentCardIndex;
    }
    
    void reset() {
        currentCardIndex = 0;
        cout << "🔄 Deck reset" << endl;
    }
    
    void display() const {
        cout << "\n========== Deck Contents ==========" << endl;
        for (size_t i = currentCardIndex; i < cards.size(); i++) {
            cards[i].display();
            cout << " ";
            if ((i - currentCardIndex + 1) % 13 == 0) cout << endl;
        }
        cout << "\nRemaining: " << remainingCards() << " cards" << endl;
        cout << "===================================\n" << endl;
    }
};

// ============== Hand ==============

class Hand {
private:
    vector<Card*> cards;
    string playerName;
    
public:
    Hand(const string& name) : playerName(name) {}
    
    void addCard(Card* card) {
        cards.push_back(card);
    }
    
    void clear() {
        cards.clear();
    }
    
    int getTotal() const {
        int total = 0;
        for (const Card* card : cards) {
            total += card->getValue();
        }
        return total;
    }
    
    // Blackjack scoring
    int getBlackjackValue() const {
        int total = 0;
        int aces = 0;
        
        for (const Card* card : cards) {
            int value = card->getValue();
            if (value > 10 && value < 14) {  // J, Q, K
                total += 10;
            } else if (value == 14) {  // Ace
                aces++;
                total += 11;
            } else {
                total += value;
            }
        }
        
        // Adjust for aces
        while (total > 21 && aces > 0) {
            total -= 10;
            aces--;
        }
        
        return total;
    }
    
    void display() const {
        cout << playerName << "'s hand: ";
        for (const Card* card : cards) {
            card->display();
            cout << " ";
        }
        cout << "| Value: " << getBlackjackValue() << endl;
    }
    
    size_t size() const {
        return cards.size();
    }
};

// ============== Blackjack Game ==============

class BlackjackGame {
private:
    Deck deck;
    Hand playerHand;
    Hand dealerHand;
    
public:
    BlackjackGame() : playerHand("Player"), dealerHand("Dealer") {}
    
    void start() {
        cout << "\n========== Blackjack Game ==========\n" << endl;
        
        deck.shuffle();
        
        // Deal initial cards
        cout << "Dealing initial cards..." << endl;
        playerHand.addCard(deck.dealCard());
        dealerHand.addCard(deck.dealCard());
        playerHand.addCard(deck.dealCard());
        dealerHand.addCard(deck.dealCard());
        
        // Show hands
        playerHand.display();
        cout << "Dealer's visible card: ";
        dealerHand.display();  // In real game, show only one card
        cout << endl;
        
        // Check for blackjack
        if (playerHand.getBlackjackValue() == 21) {
            cout << "🎉 BLACKJACK! Player wins!" << endl;
            return;
        }
        
        // Player's turn
        cout << "\n=== Player's Turn ===" << endl;
        while (playerHand.getBlackjackValue() < 21) {
            cout << "Hit or Stand? (h/s): ";
            char choice;
            cin >> choice;
            
            if (choice == 'h' || choice == 'H') {
                playerHand.addCard(deck.dealCard());
                playerHand.display();
                
                if (playerHand.getBlackjackValue() > 21) {
                    cout << "💥 BUST! Dealer wins!" << endl;
                    return;
                }
            } else {
                break;
            }
        }
        
        // Dealer's turn
        cout << "\n=== Dealer's Turn ===" << endl;
        dealerHand.display();
        
        while (dealerHand.getBlackjackValue() < 17) {
            cout << "Dealer hits..." << endl;
            dealerHand.addCard(deck.dealCard());
            dealerHand.display();
            
            if (dealerHand.getBlackjackValue() > 21) {
                cout << "💥 Dealer BUSTS! Player wins!" << endl;
                return;
            }
        }
        
        // Compare hands
        int playerValue = playerHand.getBlackjackValue();
        int dealerValue = dealerHand.getBlackjackValue();
        
        cout << "\n=== Result ===" << endl;
        if (playerValue > dealerValue) {
            cout << "🎉 Player wins! (" << playerValue << " vs " << dealerValue << ")" << endl;
        } else if (dealerValue > playerValue) {
            cout << "Dealer wins! (" << dealerValue << " vs " << playerValue << ")" << endl;
        } else {
            cout << "Push! (Tie at " << playerValue << ")" << endl;
        }
    }
};

// ============== Demo ==============

int main() {
    cout << "========== Deck of Cards Demo ==========\n" << endl;
    
    // Demo 1: Basic deck operations
    cout << "=== Demo 1: Basic Deck Operations ===" << endl;
    Deck deck;
    deck.shuffle();
    
    cout << "\nDealing 5 cards:" << endl;
    auto cards = deck.dealCards(5);
    for (Card* card : cards) {
        card->display();
        cout << " ";
    }
    cout << "\n\nRemaining cards: " << deck.remainingCards() << endl;
    
    // Demo 2: Blackjack game
    cout << "\n\n=== Demo 2: Blackjack Game ===" << endl;
    BlackjackGame game;
    game.start();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Card Representation**
- Enums for Suit and Rank
- Type-safe card creation
- Easy comparison

### 2. **Deck Management**
- Standard 52-card deck
- Efficient shuffling with modern C++ random
- Track dealt cards with index

### 3. **Game Flexibility**
- Hand class can be reused for any card game
- Different scoring methods (standard, blackjack)
- Easy to extend for other games

---

## Follow-up Questions

**Q1: How to support multiple decks?**
```cpp
class MultiDeck : public Deck {
    int deckCount;
    
    void initialize() override {
        for (int i = 0; i < deckCount; i++) {
            // Add 52 cards
        }
    }
};
```

**Q2: How to implement poker hand evaluation?**
```cpp
enum class PokerHand {
    HIGH_CARD, PAIR, TWO_PAIR, THREE_KIND,
    STRAIGHT, FLUSH, FULL_HOUSE, FOUR_KIND, STRAIGHT_FLUSH
};

class PokerEvaluator {
    PokerHand evaluate(const Hand& hand);
    bool isFlush(const vector<Card*>& cards);
    bool isStraight(const vector<Card*>& cards);
};
```

**Q3: How to add Jokers?**
```cpp
enum class Rank {
    TWO = 2, ..., ACE = 14, JOKER = 15
};

class Deck {
    void addJokers(int count = 2);
};
```

---

## Compilation

```bash
g++ -std=c++17 deck_of_cards.cpp -o cards
./cards
```

---

**Next**: `medium/11-splitwise.md`

