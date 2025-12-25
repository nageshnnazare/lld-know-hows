# Problem 9: Chess Game

**Difficulty**: Medium  
**Time to Solve**: 60-70 minutes  
**Companies**: Microsoft, Amazon, Facebook

## Problem Statement

Design a chess game that supports:
1. All chess pieces and their moves
2. Move validation
3. Check/Checkmate detection
4. Castling, En Passant
5. Pawn promotion
6. Game state management

---

## Class Diagram

```
┌─────────────────┐
│   ChessGame     │
├─────────────────┤
│ - board         │
│ - currentPlayer │
│ - gameStatus    │
├─────────────────┤
│ + makeMove()    │
│ + isCheck()     │
│ + isCheckmate() │
│ + displayBoard()│
└────────┬────────┘
         │
    ┌────┴─────┐
    │  Board   │
    ├──────────┤
    │- cells[8][8]│
    ├──────────┤
    │+ getPiece()│
    │+ setPiece()│
    └────┬─────┘
         │ contains
         ▼
    ┌─────────┐
    │  Piece  │ (abstract)
    ├─────────┤
    │- color  │
    │- hasMoved│
    ├─────────┤
    │+ canMove()│
    │+ getSymbol()│
    └────△────┘
         │
   ┌─────┴─────┬──────┬──────┬────────┬──────┐
   │           │      │      │        │      │
┌──▽──┐   ┌────▽───┐┌─▽──┐┌──▽───┐ ┌──▽───┐┌─▽──┐
│King │   │ Queen  ││Rook││Bishop│ │Knight││Pawn│
└─────┘   └────────┘└────┘└──────┘ └──────┘└────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <cmath>

using namespace std;

enum class Color { WHITE, BLACK };
enum class PieceType { KING, QUEEN, ROOK, BISHOP, KNIGHT, PAWN };
enum class GameStatus { ACTIVE, CHECK, CHECKMATE, STALEMATE };

// ============== Position ==============

struct Position {
    int row, col;
    
    Position(int r = 0, int c = 0) : row(r), col(c) {}
    
    bool isValid() const {
        return row >= 0 && row < 8 && col >= 0 && col < 8;
    }
    
    bool operator==(const Position& other) const {
        return row == other.row && col == other.col;
    }
    
    string toString() const {
        char file = 'a' + col;
        char rank = '1' + row;
        return string(1, file) + rank;
    }
};

// ============== Piece (Abstract Base) ==============

class Piece {
protected:
    Color color;
    PieceType type;
    bool hasMoved;
    
public:
    Piece(Color c, PieceType t) : color(c), type(t), hasMoved(false) {}
    virtual ~Piece() = default;
    
    Color getColor() const { return color; }
    PieceType getType() const { return type; }
    bool hasMovedBefore() const { return hasMoved; }
    void setMoved() { hasMoved = true; }
    
    virtual char getSymbol() const = 0;
    virtual bool canMove(const Position& from, const Position& to,
                        const vector<vector<Piece*>>& board) const = 0;
};

// ============== King ==============

class King : public Piece {
public:
    King(Color c) : Piece(c, PieceType::KING) {}
    
    char getSymbol() const override {
        return (color == Color::WHITE) ? 'K' : 'k';
    }
    
    bool canMove(const Position& from, const Position& to,
                const vector<vector<Piece*>>& board) const override {
        int rowDiff = abs(to.row - from.row);
        int colDiff = abs(to.col - from.col);
        
        // King moves one square in any direction
        return (rowDiff <= 1 && colDiff <= 1 && (rowDiff + colDiff > 0));
    }
};

// ============== Queen ==============

class Queen : public Piece {
public:
    Queen(Color c) : Piece(c, PieceType::QUEEN) {}
    
    char getSymbol() const override {
        return (color == Color::WHITE) ? 'Q' : 'q';
    }
    
    bool canMove(const Position& from, const Position& to,
                const vector<vector<Piece*>>& board) const override {
        int rowDiff = abs(to.row - from.row);
        int colDiff = abs(to.col - from.col);
        
        // Queen moves like rook or bishop
        if (rowDiff == 0 || colDiff == 0 || rowDiff == colDiff) {
            // Check path is clear
            int rowStep = (to.row > from.row) ? 1 : (to.row < from.row ? -1 : 0);
            int colStep = (to.col > from.col) ? 1 : (to.col < from.col ? -1 : 0);
            
            int r = from.row + rowStep;
            int c = from.col + colStep;
            
            while (r != to.row || c != to.col) {
                if (board[r][c] != nullptr) return false;
                r += rowStep;
                c += colStep;
            }
            return true;
        }
        return false;
    }
};

// ============== Rook ==============

class Rook : public Piece {
public:
    Rook(Color c) : Piece(c, PieceType::ROOK) {}
    
    char getSymbol() const override {
        return (color == Color::WHITE) ? 'R' : 'r';
    }
    
    bool canMove(const Position& from, const Position& to,
                const vector<vector<Piece*>>& board) const override {
        // Rook moves horizontally or vertically
        if (from.row != to.row && from.col != to.col) return false;
        
        // Check path is clear
        int rowStep = (to.row > from.row) ? 1 : (to.row < from.row ? -1 : 0);
        int colStep = (to.col > from.col) ? 1 : (to.col < from.col ? -1 : 0);
        
        int r = from.row + rowStep;
        int c = from.col + colStep;
        
        while (r != to.row || c != to.col) {
            if (board[r][c] != nullptr) return false;
            r += rowStep;
            c += colStep;
        }
        return true;
    }
};

// ============== Bishop ==============

class Bishop : public Piece {
public:
    Bishop(Color c) : Piece(c, PieceType::BISHOP) {}
    
    char getSymbol() const override {
        return (color == Color::WHITE) ? 'B' : 'b';
    }
    
    bool canMove(const Position& from, const Position& to,
                const vector<vector<Piece*>>& board) const override {
        int rowDiff = abs(to.row - from.row);
        int colDiff = abs(to.col - from.col);
        
        // Bishop moves diagonally
        if (rowDiff != colDiff) return false;
        
        // Check path is clear
        int rowStep = (to.row > from.row) ? 1 : -1;
        int colStep = (to.col > from.col) ? 1 : -1;
        
        int r = from.row + rowStep;
        int c = from.col + colStep;
        
        while (r != to.row || c != to.col) {
            if (board[r][c] != nullptr) return false;
            r += rowStep;
            c += colStep;
        }
        return true;
    }
};

// ============== Knight ==============

class Knight : public Piece {
public:
    Knight(Color c) : Piece(c, PieceType::KNIGHT) {}
    
    char getSymbol() const override {
        return (color == Color::WHITE) ? 'N' : 'n';
    }
    
    bool canMove(const Position& from, const Position& to,
                const vector<vector<Piece*>>& board) const override {
        int rowDiff = abs(to.row - from.row);
        int colDiff = abs(to.col - from.col);
        
        // Knight moves in L-shape
        return (rowDiff == 2 && colDiff == 1) || (rowDiff == 1 && colDiff == 2);
    }
};

// ============== Pawn ==============

class Pawn : public Piece {
public:
    Pawn(Color c) : Piece(c, PieceType::PAWN) {}
    
    char getSymbol() const override {
        return (color == Color::WHITE) ? 'P' : 'p';
    }
    
    bool canMove(const Position& from, const Position& to,
                const vector<vector<Piece*>>& board) const override {
        int direction = (color == Color::WHITE) ? 1 : -1;
        int rowDiff = to.row - from.row;
        int colDiff = abs(to.col - from.col);
        
        // Move forward one square
        if (rowDiff == direction && colDiff == 0 && board[to.row][to.col] == nullptr) {
            return true;
        }
        
        // Move forward two squares from starting position
        int startRow = (color == Color::WHITE) ? 1 : 6;
        if (from.row == startRow && rowDiff == 2 * direction && colDiff == 0 &&
            board[to.row][to.col] == nullptr &&
            board[from.row + direction][from.col] == nullptr) {
            return true;
        }
        
        // Capture diagonally
        if (rowDiff == direction && colDiff == 1 && board[to.row][to.col] != nullptr) {
            return true;
        }
        
        return false;
    }
};

// ============== Board ==============

class Board {
private:
    vector<vector<Piece*>> cells;
    
public:
    Board() : cells(8, vector<Piece*>(8, nullptr)) {}
    
    ~Board() {
        for (auto& row : cells) {
            for (auto& piece : row) {
                delete piece;
            }
        }
    }
    
    Piece* getPiece(const Position& pos) const {
        if (!pos.isValid()) return nullptr;
        return cells[pos.row][pos.col];
    }
    
    void setPiece(const Position& pos, Piece* piece) {
        if (pos.isValid()) {
            cells[pos.row][pos.col] = piece;
        }
    }
    
    const vector<vector<Piece*>>& getCells() const {
        return cells;
    }
    
    void initialize() {
        // Set up pawns
        for (int col = 0; col < 8; col++) {
            cells[1][col] = new Pawn(Color::WHITE);
            cells[6][col] = new Pawn(Color::BLACK);
        }
        
        // Set up rooks
        cells[0][0] = new Rook(Color::WHITE);
        cells[0][7] = new Rook(Color::WHITE);
        cells[7][0] = new Rook(Color::BLACK);
        cells[7][7] = new Rook(Color::BLACK);
        
        // Set up knights
        cells[0][1] = new Knight(Color::WHITE);
        cells[0][6] = new Knight(Color::WHITE);
        cells[7][1] = new Knight(Color::BLACK);
        cells[7][6] = new Knight(Color::BLACK);
        
        // Set up bishops
        cells[0][2] = new Bishop(Color::WHITE);
        cells[0][5] = new Bishop(Color::WHITE);
        cells[7][2] = new Bishop(Color::BLACK);
        cells[7][5] = new Bishop(Color::BLACK);
        
        // Set up queens
        cells[0][3] = new Queen(Color::WHITE);
        cells[7][3] = new Queen(Color::BLACK);
        
        // Set up kings
        cells[0][4] = new King(Color::WHITE);
        cells[7][4] = new King(Color::BLACK);
    }
    
    void display() const {
        cout << "\n  a b c d e f g h" << endl;
        cout << " ┌─────────────────┐" << endl;
        
        for (int row = 7; row >= 0; row--) {
            cout << row + 1 << "│";
            for (int col = 0; col < 8; col++) {
                if (cells[row][col]) {
                    cout << " " << cells[row][col]->getSymbol();
                } else {
                    cout << " ·";
                }
            }
            cout << " │" << row + 1 << endl;
        }
        
        cout << " └─────────────────┘" << endl;
        cout << "  a b c d e f g h\n" << endl;
    }
};

// ============== Chess Game ==============

class ChessGame {
private:
    Board board;
    Color currentPlayer;
    GameStatus status;
    
    Position findKing(Color color) const {
        const auto& cells = board.getCells();
        for (int row = 0; row < 8; row++) {
            for (int col = 0; col < 8; col++) {
                Piece* piece = cells[row][col];
                if (piece && piece->getType() == PieceType::KING &&
                    piece->getColor() == color) {
                    return Position(row, col);
                }
            }
        }
        return Position(-1, -1);
    }
    
    bool isPositionUnderAttack(const Position& pos, Color byColor) const {
        const auto& cells = board.getCells();
        
        for (int row = 0; row < 8; row++) {
            for (int col = 0; col < 8; col++) {
                Piece* piece = cells[row][col];
                if (piece && piece->getColor() == byColor) {
                    Position from(row, col);
                    if (piece->canMove(from, pos, cells)) {
                        return true;
                    }
                }
            }
        }
        return false;
    }
    
public:
    ChessGame() : currentPlayer(Color::WHITE), status(GameStatus::ACTIVE) {
        board.initialize();
    }
    
    bool makeMove(const Position& from, const Position& to) {
        if (!from.isValid() || !to.isValid()) {
            cout << "Invalid position!" << endl;
            return false;
        }
        
        Piece* piece = board.getPiece(from);
        
        if (!piece) {
            cout << "No piece at " << from.toString() << endl;
            return false;
        }
        
        if (piece->getColor() != currentPlayer) {
            cout << "Not your piece!" << endl;
            return false;
        }
        
        Piece* targetPiece = board.getPiece(to);
        
        if (targetPiece && targetPiece->getColor() == currentPlayer) {
            cout << "Cannot capture your own piece!" << endl;
            return false;
        }
        
        if (!piece->canMove(from, to, board.getCells())) {
            cout << "Illegal move for this piece!" << endl;
            return false;
        }
        
        // Make the move
        board.setPiece(to, piece);
        board.setPiece(from, nullptr);
        piece->setMoved();
        
        // Check if own king is in check (invalid move)
        Position kingPos = findKing(currentPlayer);
        Color opponentColor = (currentPlayer == Color::WHITE) ? Color::BLACK : Color::WHITE;
        
        if (isPositionUnderAttack(kingPos, opponentColor)) {
            // Undo move
            board.setPiece(from, piece);
            board.setPiece(to, targetPiece);
            cout << "Move puts your king in check!" << endl;
            return false;
        }
        
        // Delete captured piece
        if (targetPiece) {
            delete targetPiece;
            cout << "Captured " << targetPiece->getSymbol() << "!" << endl;
        }
        
        // Switch player
        currentPlayer = opponentColor;
        
        // Check for check/checkmate
        updateGameStatus();
        
        return true;
    }
    
    void updateGameStatus() {
        Position kingPos = findKing(currentPlayer);
        Color opponentColor = (currentPlayer == Color::WHITE) ? Color::BLACK : Color::WHITE;
        
        if (isPositionUnderAttack(kingPos, opponentColor)) {
            status = GameStatus::CHECK;
            cout << "CHECK!" << endl;
        } else {
            status = GameStatus::ACTIVE;
        }
    }
    
    void display() const {
        board.display();
        cout << "Current player: " << (currentPlayer == Color::WHITE ? "White" : "Black") << endl;
        if (status == GameStatus::CHECK) {
            cout << "⚠ King is in CHECK!" << endl;
        }
        cout << endl;
    }
    
    Position parsePosition(const string& pos) const {
        if (pos.length() != 2) return Position(-1, -1);
        
        int col = pos[0] - 'a';
        int row = pos[1] - '1';
        
        return Position(row, col);
    }
};

// ============== Demo ==============

int main() {
    ChessGame game;
    
    cout << "========== Chess Game Demo ==========\n" << endl;
    
    game.display();
    
    // Example moves
    cout << "=== Move 1: White pawn e2 to e4 ===" << endl;
    game.makeMove(game.parsePosition("e2"), game.parsePosition("e4"));
    game.display();
    
    cout << "=== Move 2: Black pawn e7 to e5 ===" << endl;
    game.makeMove(game.parsePosition("e7"), game.parsePosition("e5"));
    game.display();
    
    cout << "=== Move 3: White knight g1 to f3 ===" << endl;
    game.makeMove(game.parsePosition("g1"), game.parsePosition("f3"));
    game.display();
    
    cout << "=== Move 4: Black knight b8 to c6 ===" << endl;
    game.makeMove(game.parsePosition("b8"), game.parsePosition("c6"));
    game.display();
    
    cout << "=== Move 5: White bishop f1 to c4 ===" << endl;
    game.makeMove(game.parsePosition("f1"), game.parsePosition("c4"));
    game.display();
    
    cout << "=== Attempted illegal move: White pawn e4 to e6 ===" << endl;
    game.makeMove(game.parsePosition("e4"), game.parsePosition("e6"));
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Piece Hierarchy**
- Abstract `Piece` base class
- Each piece type implements `canMove()`
- Polymorphic move validation

### 2. **Move Validation**
- Piece-specific movement rules
- Path obstruction checking
- Turn validation

### 3. **Check Detection**
- Find king position
- Test all opponent pieces for attacks
- Prevent moves that expose king

---

## Follow-up Questions

**Q1: How to implement castling?**
```cpp
bool canCastle(King* king, Rook* rook) {
    return !king->hasMovedBefore() &&
           !rook->hasMovedBefore() &&
           pathIsClear();
}
```

**Q2: How to detect checkmate?**
```cpp
bool isCheckmate() {
    if (!isCheck()) return false;
    // Try all possible moves
    // If none escape check, it's checkmate
}
```

**Q3: How to implement pawn promotion?**
```cpp
void promotePawn(Pawn* pawn, Position pos) {
    if (pos.row == 7 || pos.row == 0) {
        // Replace with Queen/Rook/Bishop/Knight
    }
}
```

---

## Compilation

```bash
g++ -std=c++17 chess.cpp -o chess
./chess
```

---

**Next**: `medium/10-social-media-feed.md`

