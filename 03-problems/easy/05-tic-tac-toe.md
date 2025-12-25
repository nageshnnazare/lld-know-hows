# Problem 5: Tic Tac Toe Game

**Difficulty**: Easy  
**Time to Solve**: 25-30 minutes  
**Companies**: Google, Facebook, Microsoft

## Problem Statement

Design a Tic Tac Toe game that supports:
1. Two players (X and O)
2. 3x3 board
3. Win detection (row, column, diagonal)
4. Draw detection
5. Move validation
6. Game state management
7. Extensible for N×N board

### Requirements

**Functional Requirements**:
- Initialize game board
- Make a move
- Validate moves (empty cell, valid position)
- Check winner after each move
- Check draw condition
- Reset game
- Support for N×N board (extension)

**Non-Functional Requirements**:
- Clean OOP design
- Easy to extend (AI player, different board sizes)
- Efficient win checking

---

## Concepts Involved

1. **OOP**: Classes, Encapsulation
2. **Design Patterns**: Strategy (for different players), Template Method
3. **Game Logic**: Win condition checking
4. **SOLID**: SRP, OCP

---

## Class Diagram

```
┌────────────────────┐
│      Game          │
├────────────────────┤
│ - board: Board     │
│ - players[2]       │
│ - currentPlayer    │
│ - gameStatus       │
├────────────────────┤
│ + makeMove()       │
│ + checkWinner()    │
│ + isGameOver()     │
│ + reset()          │
└────────┬───────────┘
         │
         │ contains
         ▼
┌────────────────────┐
│      Board         │
├────────────────────┤
│ - cells[][]        │
│ - size: int        │
├────────────────────┤
│ + makeMove()       │
│ + isCellEmpty()    │
│ + display()        │
│ + checkWin()       │
└────────────────────┘

┌────────────────────┐
│     Player         │ ◄──── Abstract
├────────────────────┤
│ - name: string     │
│ - symbol: char     │
├────────────────────┤
│ + getMove()        │
└────────┬───────────┘
         │
    ┌────┴─────┬──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│ Human  │ │   AI   │ │ Random │
│ Player │ │ Player │ │ Player │
└────────┘ └────────┘ └────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <limits>

using namespace std;

// ============== Enums ==============

enum class GameStatus {
    IN_PROGRESS,
    PLAYER_X_WINS,
    PLAYER_O_WINS,
    DRAW
};

enum class CellState {
    EMPTY,
    X,
    O
};

// ============== Cell ==============

class Cell {
private:
    CellState state;
    
public:
    Cell() : state(CellState::EMPTY) {}
    
    bool isEmpty() const { return state == CellState::EMPTY; }
    
    void setState(CellState s) { state = s; }
    CellState getState() const { return state; }
    
    char getSymbol() const {
        switch(state) {
            case CellState::X: return 'X';
            case CellState::O: return 'O';
            default: return ' ';
        }
    }
};

// ============== Board ==============

class Board {
private:
    vector<vector<Cell>> cells;
    int size;
    int movesCount;
    
public:
    Board(int s = 3) : size(s), movesCount(0) {
        cells.resize(size, vector<Cell>(size));
    }
    
    int getSize() const { return size; }
    
    bool isCellEmpty(int row, int col) const {
        if (row < 0 || row >= size || col < 0 || col >= size) {
            return false;
        }
        return cells[row][col].isEmpty();
    }
    
    bool makeMove(int row, int col, CellState player) {
        if (!isCellEmpty(row, col)) {
            return false;
        }
        
        cells[row][col].setState(player);
        movesCount++;
        return true;
    }
    
    bool isFull() const {
        return movesCount == size * size;
    }
    
    // Check if there's a winner
    CellState checkWinner() const {
        // Check rows
        for (int i = 0; i < size; i++) {
            if (!cells[i][0].isEmpty()) {
                bool rowWin = true;
                CellState firstCell = cells[i][0].getState();
                
                for (int j = 1; j < size; j++) {
                    if (cells[i][j].getState() != firstCell) {
                        rowWin = false;
                        break;
                    }
                }
                
                if (rowWin) return firstCell;
            }
        }
        
        // Check columns
        for (int j = 0; j < size; j++) {
            if (!cells[0][j].isEmpty()) {
                bool colWin = true;
                CellState firstCell = cells[0][j].getState();
                
                for (int i = 1; i < size; i++) {
                    if (cells[i][j].getState() != firstCell) {
                        colWin = false;
                        break;
                    }
                }
                
                if (colWin) return firstCell;
            }
        }
        
        // Check main diagonal (top-left to bottom-right)
        if (!cells[0][0].isEmpty()) {
            bool diagWin = true;
            CellState firstCell = cells[0][0].getState();
            
            for (int i = 1; i < size; i++) {
                if (cells[i][i].getState() != firstCell) {
                    diagWin = false;
                    break;
                }
            }
            
            if (diagWin) return firstCell;
        }
        
        // Check anti-diagonal (top-right to bottom-left)
        if (!cells[0][size-1].isEmpty()) {
            bool antiDiagWin = true;
            CellState firstCell = cells[0][size-1].getState();
            
            for (int i = 1; i < size; i++) {
                if (cells[i][size-1-i].getState() != firstCell) {
                    antiDiagWin = false;
                    break;
                }
            }
            
            if (antiDiagWin) return firstCell;
        }
        
        return CellState::EMPTY;
    }
    
    void display() const {
        cout << "\n";
        for (int i = 0; i < size; i++) {
            // Print row
            for (int j = 0; j < size; j++) {
                cout << " " << cells[i][j].getSymbol() << " ";
                if (j < size - 1) cout << "|";
            }
            cout << "\n";
            
            // Print separator
            if (i < size - 1) {
                for (int j = 0; j < size; j++) {
                    cout << "---";
                    if (j < size - 1) cout << "+";
                }
                cout << "\n";
            }
        }
        cout << "\n";
    }
    
    void reset() {
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                cells[i][j].setState(CellState::EMPTY);
            }
        }
        movesCount = 0;
    }
};

// ============== Player ==============

class Player {
protected:
    string name;
    CellState symbol;
    
public:
    Player(const string& n, CellState s) : name(n), symbol(s) {}
    virtual ~Player() = default;
    
    string getName() const { return name; }
    CellState getSymbol() const { return symbol; }
    
    virtual pair<int, int> getMove(const Board& board) = 0;
};

// Human Player
class HumanPlayer : public Player {
public:
    HumanPlayer(const string& name, CellState symbol) 
        : Player(name, symbol) {}
    
    pair<int, int> getMove(const Board& board) override {
        int row, col;
        
        while (true) {
            cout << name << "'s turn (" << (symbol == CellState::X ? "X" : "O") << ")" << endl;
            cout << "Enter row (0-" << board.getSize()-1 << "): ";
            cin >> row;
            
            if (cin.fail()) {
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                cout << "Invalid input! Please enter a number." << endl;
                continue;
            }
            
            cout << "Enter column (0-" << board.getSize()-1 << "): ";
            cin >> col;
            
            if (cin.fail()) {
                cin.clear();
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                cout << "Invalid input! Please enter a number." << endl;
                continue;
            }
            
            if (row >= 0 && row < board.getSize() && 
                col >= 0 && col < board.getSize() &&
                board.isCellEmpty(row, col)) {
                return {row, col};
            }
            
            cout << "Invalid move! Try again." << endl;
        }
    }
};

// Simple AI Player (Random valid move)
class AIPlayer : public Player {
public:
    AIPlayer(const string& name, CellState symbol) 
        : Player(name, symbol) {}
    
    pair<int, int> getMove(const Board& board) override {
        cout << name << " (AI) is thinking..." << endl;
        
        // Find all empty cells
        vector<pair<int, int>> emptyCells;
        for (int i = 0; i < board.getSize(); i++) {
            for (int j = 0; j < board.getSize(); j++) {
                if (board.isCellEmpty(i, j)) {
                    emptyCells.push_back({i, j});
                }
            }
        }
        
        if (!emptyCells.empty()) {
            int randomIndex = rand() % emptyCells.size();
            return emptyCells[randomIndex];
        }
        
        return {-1, -1}; // Should never reach here if board has empty cells
    }
};

// ============== Game ==============

class TicTacToeGame {
private:
    unique_ptr<Board> board;
    unique_ptr<Player> player1;
    unique_ptr<Player> player2;
    Player* currentPlayer;
    GameStatus status;
    
public:
    TicTacToeGame(unique_ptr<Player> p1, unique_ptr<Player> p2, int boardSize = 3) 
        : player1(move(p1)), player2(move(p2)), status(GameStatus::IN_PROGRESS) {
        
        board = make_unique<Board>(boardSize);
        currentPlayer = player1.get();
    }
    
    void start() {
        cout << "\n========== TIC TAC TOE ==========" << endl;
        cout << player1->getName() << " (X) vs " << player2->getName() << " (O)" << endl;
        cout << "=================================\n" << endl;
        
        board->display();
        
        while (status == GameStatus::IN_PROGRESS) {
            playTurn();
        }
        
        displayResult();
    }
    
    void playTurn() {
        auto [row, col] = currentPlayer->getMove(*board);
        
        if (board->makeMove(row, col, currentPlayer->getSymbol())) {
            cout << currentPlayer->getName() << " placed " 
                 << (currentPlayer->getSymbol() == CellState::X ? "X" : "O")
                 << " at (" << row << ", " << col << ")" << endl;
            
            board->display();
            
            // Check for winner
            CellState winner = board->checkWinner();
            if (winner == CellState::X) {
                status = GameStatus::PLAYER_X_WINS;
            } else if (winner == CellState::O) {
                status = GameStatus::PLAYER_O_WINS;
            } else if (board->isFull()) {
                status = GameStatus::DRAW;
            } else {
                // Switch player
                switchPlayer();
            }
        } else {
            cout << "Invalid move! Try again." << endl;
        }
    }
    
    void switchPlayer() {
        currentPlayer = (currentPlayer == player1.get()) ? player2.get() : player1.get();
    }
    
    void displayResult() {
        cout << "\n========== GAME OVER ==========" << endl;
        
        switch(status) {
            case GameStatus::PLAYER_X_WINS:
                cout << "🎉 " << player1->getName() << " (X) WINS!" << endl;
                break;
            case GameStatus::PLAYER_O_WINS:
                cout << "🎉 " << player2->getName() << " (O) WINS!" << endl;
                break;
            case GameStatus::DRAW:
                cout << "🤝 It's a DRAW!" << endl;
                break;
            default:
                break;
        }
        
        cout << "===============================\n" << endl;
    }
    
    void reset() {
        board->reset();
        status = GameStatus::IN_PROGRESS;
        currentPlayer = player1.get();
        cout << "Game reset!" << endl;
    }
};

// ============== Demo ==============

int main() {
    srand(time(nullptr));
    
    cout << "Choose game mode:" << endl;
    cout << "1. Human vs Human" << endl;
    cout << "2. Human vs AI" << endl;
    cout << "3. AI vs AI" << endl;
    
    int choice;
    cin >> choice;
    
    unique_ptr<Player> player1, player2;
    
    switch(choice) {
        case 1:
            player1 = make_unique<HumanPlayer>("Player 1", CellState::X);
            player2 = make_unique<HumanPlayer>("Player 2", CellState::O);
            break;
        case 2:
            player1 = make_unique<HumanPlayer>("You", CellState::X);
            player2 = make_unique<AIPlayer>("Computer", CellState::O);
            break;
        case 3:
            player1 = make_unique<AIPlayer>("AI 1", CellState::X);
            player2 = make_unique<AIPlayer>("AI 2", CellState::O);
            break;
        default:
            cout << "Invalid choice! Starting Human vs Human" << endl;
            player1 = make_unique<HumanPlayer>("Player 1", CellState::X);
            player2 = make_unique<HumanPlayer>("Player 2", CellState::O);
    }
    
    TicTacToeGame game(move(player1), move(player2));
    game.start();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Separation of Concerns**
- `Board` manages game state
- `Player` handles move selection
- `Game` orchestrates gameplay

### 2. **Strategy Pattern for Players**
- Abstract `Player` class
- Different implementations (Human, AI)
- Easy to add new player types

### 3. **Extensibility**
- N×N board support
- Easy to add AI algorithms (Minimax)
- Can add different game modes

---

## Extensions & Follow-ups

### Q1: How to implement unbeatable AI (Minimax)?

```cpp
class MinimaxAI : public Player {
private:
    int minimax(Board& board, int depth, bool isMaximizing) {
        CellState winner = board.checkWinner();
        
        if (winner == this->symbol) return 10 - depth;
        if (winner != CellState::EMPTY) return depth - 10;
        if (board.isFull()) return 0;
        
        if (isMaximizing) {
            int bestScore = INT_MIN;
            // Try all moves
            for (int i = 0; i < board.getSize(); i++) {
                for (int j = 0; j < board.getSize(); j++) {
                    if (board.isCellEmpty(i, j)) {
                        board.makeMove(i, j, this->symbol);
                        int score = minimax(board, depth + 1, false);
                        // Undo move
                        bestScore = max(bestScore, score);
                    }
                }
            }
            return bestScore;
        } else {
            // Minimizing player
            // Similar logic
        }
    }
    
public:
    pair<int, int> getMove(const Board& board) override {
        // Use minimax to find best move
    }
};
```

### Q2: How to support larger boards (N×N)?
Already supported! Just pass different size to constructor:
```cpp
TicTacToeGame game(move(player1), move(player2), 5); // 5x5 board
```

### Q3: How to add undo functionality?
```cpp
class Game {
private:
    stack<pair<int, int>> moveHistory;
    
public:
    void undo() {
        if (!moveHistory.empty()) {
            auto [row, col] = moveHistory.top();
            moveHistory.pop();
            board->clearCell(row, col);
            switchPlayer();
        }
    }
};
```

### Q4: How to make it network multiplayer?
- Separate game logic from I/O
- Create `NetworkPlayer` class
- Send/receive moves via sockets
- Synchronize game state

---

## Complexity Analysis

- **Make Move**: O(1)
- **Check Winner**: O(n) where n = board size
- **Minimax AI**: O(b^d) where b = branching factor, d = depth
  - For 3×3: ~9! = 362,880 states (manageable)
  - For larger boards: Need alpha-beta pruning

---

## Compilation & Execution

```bash
g++ -std=c++17 tic_tac_toe.cpp -o tictactoe
./tictactoe
```

---

## Sample Output

```
Choose game mode:
1. Human vs Human
2. Human vs AI
3. AI vs AI
2

========== TIC TAC TOE ==========
You (X) vs Computer (O)
=================================

   |   |   
---+---+---
   |   |   
---+---+---
   |   |   

You's turn (X)
Enter row (0-2): 1
Enter column (0-2): 1
You placed X at (1, 1)

   |   |   
---+---+---
   | X |   
---+---+---
   |   |   

Computer (AI) is thinking...
Computer placed O at (0, 0)

 O |   |   
---+---+---
   | X |   
---+---+---
   |   |   

...

========== GAME OVER ==========
🎉 You (X) WINS!
===============================
```

---

**Next Problem**: `06-traffic-signal.md`

