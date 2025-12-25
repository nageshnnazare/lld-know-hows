# Problem 10: Snakes and Ladders Game

**Difficulty**: Easy  
**Time to Solve**: 30-35 minutes  
**Companies**: Amazon, Flipkart, PayTM

## Problem Statement

Design a Snakes and Ladders board game that supports:
1. N x N board (default 10x10)
2. Multiple players
3. Snakes and ladders placement
4. Dice rolling
5. Player movement
6. Win condition detection

---

## Class Diagram

```
┌──────────────────┐
│      Game        │
├──────────────────┤
│- board           │
│- players         │
│- dice            │
│- currentPlayer   │
├──────────────────┤
│+ startGame()     │
│+ playTurn()      │
│+ isGameOver()    │
└──────┬───────────┘
       │
   ┌───┴────┬──────────┬──────────┐
   ▼        ▼          ▼          ▼
┌──────┐┌──────┐  ┌──────┐   ┌──────┐
│Board ││Player│  │ Dice │   │Jump  │
├──────┤├──────┤  ├──────┤   ├──────┤
│-size ││-name │  │-faces│   │-start│
│-jumps││-pos  │  │+roll()│  │-end  │
└──────┘└──────┘  └──────┘   └──────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <cstdlib>
#include <ctime>

using namespace std;

// ============== Jump (Snake or Ladder) ==============

class Jump {
private:
    int start;
    int end;
    
public:
    Jump(int s, int e) : start(s), end(e) {}
    
    int getStart() const { return start; }
    int getEnd() const { return end; }
    
    bool isSnake() const { return end < start; }
    bool isLadder() const { return end > start; }
};

// ============== Dice ==============

class Dice {
private:
    int faces;
    
public:
    Dice(int f = 6) : faces(f) {
        srand(time(nullptr));
    }
    
    int roll() {
        int value = (rand() % faces) + 1;
        cout << "🎲 Rolled: " << value << endl;
        return value;
    }
};

// ============== Player ==============

class Player {
private:
    string name;
    int position;
    
public:
    Player(const string& n) : name(n), position(0) {}
    
    string getName() const { return name; }
    int getPosition() const { return position; }
    
    void setPosition(int pos) { position = pos; }
    
    void move(int steps) {
        position += steps;
    }
};

// ============== Board ==============

class Board {
private:
    int size;
    map<int, Jump> jumps;  // position -> Jump
    
public:
    Board(int s = 100) : size(s) {}
    
    int getSize() const { return size; }
    
    void addSnake(int head, int tail) {
        if (head > tail && head <= size && tail >= 1) {
            jumps[head] = Jump(head, tail);
            cout << "🐍 Snake added: " << head << " → " << tail << endl;
        }
    }
    
    void addLadder(int bottom, int top) {
        if (top > bottom && top <= size && bottom >= 1) {
            jumps[bottom] = Jump(bottom, top);
            cout << "🪜 Ladder added: " << bottom << " → " << top << endl;
        }
    }
    
    int checkJump(int position) {
        if (jumps.find(position) != jumps.end()) {
            Jump jump = jumps[position];
            if (jump.isSnake()) {
                cout << "   🐍 Oops! Snake bite! Sliding down to " << jump.getEnd() << endl;
            } else {
                cout << "   🪜 Yay! Ladder! Climbing up to " << jump.getEnd() << endl;
            }
            return jump.getEnd();
        }
        return position;
    }
    
    void display() const {
        cout << "\n========== Board Setup ==========" << endl;
        cout << "Board Size: " << size << " squares" << endl;
        cout << "Snakes:" << endl;
        for (const auto& [pos, jump] : jumps) {
            if (jump.isSnake()) {
                cout << "  🐍 " << jump.getStart() << " → " << jump.getEnd() << endl;
            }
        }
        cout << "Ladders:" << endl;
        for (const auto& [pos, jump] : jumps) {
            if (jump.isLadder()) {
                cout << "  🪜 " << jump.getStart() << " → " << jump.getEnd() << endl;
            }
        }
        cout << "=================================\n" << endl;
    }
};

// ============== Game ==============

class Game {
private:
    Board board;
    vector<Player> players;
    Dice dice;
    int currentPlayerIndex;
    bool gameOver;
    
public:
    Game(int boardSize = 100) : board(boardSize), currentPlayerIndex(0), gameOver(false) {}
    
    void addPlayer(const string& name) {
        players.emplace_back(name);
        cout << "✓ Player added: " << name << endl;
    }
    
    void setupSnakesAndLadders() {
        // Add snakes
        board.addSnake(99, 54);
        board.addSnake(70, 55);
        board.addSnake(52, 42);
        board.addSnake(25, 2);
        board.addSnake(95, 72);
        
        // Add ladders
        board.addLadder(6, 25);
        board.addLadder(11, 40);
        board.addLadder(60, 85);
        board.addLadder(46, 90);
        board.addLadder(17, 69);
    }
    
    void startGame() {
        if (players.size() < 2) {
            cout << "Need at least 2 players to start!" << endl;
            return;
        }
        
        cout << "\n========== Game Started! ==========" << endl;
        board.display();
        
        while (!gameOver) {
            playTurn();
        }
    }
    
    void playTurn() {
        Player& currentPlayer = players[currentPlayerIndex];
        
        cout << "\n--- " << currentPlayer.getName() << "'s turn ---" << endl;
        cout << "Current position: " << currentPlayer.getPosition() << endl;
        cout << "Press Enter to roll the dice...";
        cin.get();
        
        int diceValue = dice.roll();
        int newPosition = currentPlayer.getPosition() + diceValue;
        
        // Check if position exceeds board size
        if (newPosition > board.getSize()) {
            cout << "Cannot move! Need exact roll to win." << endl;
            newPosition = currentPlayer.getPosition();
        } else {
            cout << "Moving from " << currentPlayer.getPosition() 
                 << " to " << newPosition << endl;
            currentPlayer.setPosition(newPosition);
            
            // Check for snake or ladder
            int finalPosition = board.checkJump(newPosition);
            currentPlayer.setPosition(finalPosition);
            
            cout << "Final position: " << currentPlayer.getPosition() << endl;
            
            // Check win condition
            if (currentPlayer.getPosition() == board.getSize()) {
                announceWinner(currentPlayer);
                return;
            }
        }
        
        // Move to next player
        currentPlayerIndex = (currentPlayerIndex + 1) % players.size();
    }
    
    void announceWinner(const Player& winner) {
        cout << "\n🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉" << endl;
        cout << "🎉 " << winner.getName() << " WINS! 🎉" << endl;
        cout << "🎉🎉🎉🎉🎉🎉🎉🎉🎉🎉\n" << endl;
        gameOver = true;
    }
    
    void displayStatus() const {
        cout << "\n========== Current Status ==========" << endl;
        for (const auto& player : players) {
            cout << player.getName() << ": Position " << player.getPosition() << endl;
        }
        cout << "====================================\n" << endl;
    }
};

// ============== Demo ==============

int main() {
    Game game(100);
    
    cout << "========== Snakes and Ladders ==========\n" << endl;
    
    // Add players
    game.addPlayer("Alice");
    game.addPlayer("Bob");
    game.addPlayer("Charlie");
    
    // Setup board
    game.setupSnakesAndLadders();
    
    // Start game
    game.startGame();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Jump Abstraction**
- Single class handles both snakes and ladders
- Determined by start vs end position
- Cleaner than separate classes

### 2. **Game Loop**
- Turn-based gameplay
- Automatic player rotation
- Win condition checking

### 3. **Board Independence**
- Board doesn't know about players
- Board only manages jumps
- Easy to create different board configurations

---

## Follow-up Questions

**Q1: How to support different board sizes?**
```cpp
class BoardFactory {
    static Board* createBoard(int size) {
        Board* board = new Board(size);
        // Setup snakes and ladders proportionally
        return board;
    }
};
```

**Q2: How to add power-ups or special squares?**
```cpp
class SpecialSquare {
    int position;
    virtual void activate(Player* player) = 0;
};

class ExtraTurn : public SpecialSquare {
    void activate(Player* player) {
        // Give player another turn
    }
};
```

**Q3: How to save/load game state?**
```cpp
class GameState {
    vector<PlayerData> playerStates;
    int currentPlayer;
    
    void save(const string& filename);
    static Game* load(const string& filename);
};
```

---

## Compilation

```bash
g++ -std=c++17 snakes_and_ladders.cpp -o snakes
./snakes
```

---

**Next**: `easy/11-deck-of-cards.md`

