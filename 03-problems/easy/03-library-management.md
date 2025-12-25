# Problem 3: Library Management System

**Difficulty**: Easy  
**Time to Solve**: 30-40 minutes  
**Companies**: Microsoft, Flipkart, Amazon

## Problem Statement

Design a library management system that can:
1. Manage books (add, remove, search)
2. Manage members (register, remove)
3. Issue books to members
4. Return books
5. Track book availability
6. Fine calculation for late returns
7. Reservation system

### Requirements

**Functional Requirements**:
- Add/remove books and members
- Search books by title, author, ISBN
- Issue book to member (max 5 books)
- Return book and calculate fine if late
- Reserve books that are currently issued
- View member borrowing history

**Non-Functional Requirements**:
- Simple and extensible design
- Track book copies (multiple copies of same book)
- Handle late return penalties

---

## Concepts Involved

1. **OOP**: Classes, Inheritance, Encapsulation
2. **Design Patterns**: 
   - **Factory** (Book creation)
   - **Strategy** (Fine calculation)
   - **Observer** (Reservation notifications)
3. **SOLID**: SRP, OCP

---

## Class Diagram

```
┌────────────────────┐
│   Library          │ ◄──── Singleton
├────────────────────┤
│ - books: map       │
│ - members: map     │
│ - catalog: Catalog │
├────────────────────┤
│ + addBook()        │
│ + registerMember() │
│ + issueBook()      │
│ + returnBook()     │
└────────┬───────────┘
         │
         ├──────────┬──────────┐
         ▼          ▼          ▼
┌────────────┐ ┌────────┐ ┌─────────┐
│   Book     │ │ Member │ │BookItem │
├────────────┤ ├────────┤ ├─────────┤
│ - isbn     │ │ - id   │ │ -barcode│
│ - title    │ │ - name │ │ -status │
│ - author   │ │ - books│ │ -book   │
│ - subject  │ └────────┘ └─────────┘
└────────────┘

┌────────────────────┐
│   Lending          │
├────────────────────┤
│ - bookItem         │
│ - member           │
│ - issueDate        │
│ - dueDate          │
│ - returnDate       │
├────────────────────┤
│ + calculateFine()  │
└────────────────────┘

┌────────────────────┐
│  FineStrategy      │ ◄──── Strategy
├────────────────────┤
│ + calculate()      │
└────────┬───────────┘
         │
    ┌────┴─────┐
    ▼          ▼
┌─────────┐ ┌─────────┐
│Standard │ │ Premium │
│  Fine   │ │  Fine   │
└─────────┘ └─────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <ctime>
#include <algorithm>

using namespace std;

// ============== Enums ==============

enum class BookStatus {
    AVAILABLE,
    ISSUED,
    RESERVED,
    LOST
};

enum class MembershipType {
    STANDARD,
    PREMIUM
};

// ============== Book ==============

class Book {
private:
    string isbn;
    string title;
    string author;
    string subject;
    string publisher;
    int totalCopies;
    
public:
    Book(const string& i, const string& t, const string& a, 
         const string& s, int copies = 1)
        : isbn(i), title(t), author(a), subject(s), totalCopies(copies) {}
    
    string getISBN() const { return isbn; }
    string getTitle() const { return title; }
    string getAuthor() const { return author; }
    string getSubject() const { return subject; }
    int getTotalCopies() const { return totalCopies; }
    
    void addCopy() { totalCopies++; }
    
    void display() const {
        cout << "ISBN: " << isbn << " | Title: " << title 
             << " | Author: " << author << " | Copies: " << totalCopies << endl;
    }
};

// ============== Book Item (Physical Copy) ==============

class BookItem {
private:
    string barcode;
    Book* book;
    BookStatus status;
    
public:
    BookItem(const string& bc, Book* b)
        : barcode(bc), book(b), status(BookStatus::AVAILABLE) {}
    
    string getBarcode() const { return barcode; }
    Book* getBook() const { return book; }
    BookStatus getStatus() const { return status; }
    
    void setStatus(BookStatus s) { status = s; }
    
    bool isAvailable() const {
        return status == BookStatus::AVAILABLE;
    }
    
    void display() const {
        cout << "Barcode: " << barcode << " | ";
        book->display();
        cout << "Status: " << (int)status << endl;
    }
};

// ============== Member ==============

class Member {
private:
    string memberId;
    string name;
    string email;
    string phone;
    MembershipType membershipType;
    vector<string> issuedBooks; // Barcodes
    time_t membershipDate;
    
public:
    Member(const string& id, const string& n, const string& e, 
           MembershipType type = MembershipType::STANDARD)
        : memberId(id), name(n), email(e), membershipType(type) {
        membershipDate = time(nullptr);
    }
    
    string getMemberId() const { return memberId; }
    string getName() const { return name; }
    MembershipType getMembershipType() const { return membershipType; }
    
    int getIssuedBooksCount() const { return issuedBooks.size(); }
    
    bool canIssueBook() const {
        int maxBooks = (membershipType == MembershipType::PREMIUM) ? 10 : 5;
        return issuedBooks.size() < maxBooks;
    }
    
    void issueBook(const string& barcode) {
        issuedBooks.push_back(barcode);
    }
    
    void returnBook(const string& barcode) {
        auto it = find(issuedBooks.begin(), issuedBooks.end(), barcode);
        if (it != issuedBooks.end()) {
            issuedBooks.erase(it);
        }
    }
    
    void display() const {
        cout << "ID: " << memberId << " | Name: " << name 
             << " | Type: " << (membershipType == MembershipType::PREMIUM ? "Premium" : "Standard")
             << " | Issued Books: " << issuedBooks.size() << endl;
    }
};

// ============== Fine Strategy ==============

class FineStrategy {
public:
    virtual ~FineStrategy() = default;
    virtual double calculateFine(int daysLate) const = 0;
};

class StandardFineStrategy : public FineStrategy {
public:
    double calculateFine(int daysLate) const override {
        return daysLate * 1.0; // $1 per day
    }
};

class PremiumFineStrategy : public FineStrategy {
public:
    double calculateFine(int daysLate) const override {
        return daysLate * 0.5; // $0.5 per day for premium members
    }
};

// ============== Lending ==============

class Lending {
private:
    string lendingId;
    BookItem* bookItem;
    Member* member;
    time_t issueDate;
    time_t dueDate;
    time_t returnDate;
    unique_ptr<FineStrategy> fineStrategy;
    
    static int counter;
    
public:
    Lending(BookItem* item, Member* mem, int dueDays = 14)
        : bookItem(item), member(mem), returnDate(0) {
        
        lendingId = "LEND" + to_string(++counter);
        issueDate = time(nullptr);
        dueDate = issueDate + (dueDays * 24 * 3600);
        
        // Set fine strategy based on membership
        if (mem->getMembershipType() == MembershipType::PREMIUM) {
            fineStrategy = make_unique<PremiumFineStrategy>();
        } else {
            fineStrategy = make_unique<StandardFineStrategy>();
        }
    }
    
    string getLendingId() const { return lendingId; }
    BookItem* getBookItem() const { return bookItem; }
    Member* getMember() const { return member; }
    time_t getIssueDate() const { return issueDate; }
    time_t getDueDate() const { return dueDate; }
    
    void setReturnDate() {
        returnDate = time(nullptr);
    }
    
    bool isReturned() const {
        return returnDate != 0;
    }
    
    double calculateFine() const {
        if (returnDate == 0) return 0.0;
        
        if (returnDate > dueDate) {
            int daysLate = (returnDate - dueDate) / (24 * 3600);
            return fineStrategy->calculateFine(daysLate);
        }
        return 0.0;
    }
    
    void display() const {
        cout << "\n--- Lending: " << lendingId << " ---" << endl;
        cout << "Member: " << member->getName() << endl;
        cout << "Book: " << bookItem->getBook()->getTitle() << endl;
        
        char issueStr[26], dueStr[26];
        ctime_r(&issueDate, issueStr);
        ctime_r(&dueDate, dueStr);
        
        cout << "Issued: " << issueStr;
        cout << "Due: " << dueStr;
        
        if (returnDate != 0) {
            char returnStr[26];
            ctime_r(&returnDate, returnStr);
            cout << "Returned: " << returnStr;
            cout << "Fine: $" << calculateFine() << endl;
        } else {
            cout << "Status: Not returned" << endl;
        }
    }
};

int Lending::counter = 0;

// ============== Library (Singleton) ==============

class Library {
private:
    static Library* instance;
    
    string name;
    unordered_map<string, unique_ptr<Book>> books;          // ISBN -> Book
    unordered_map<string, unique_ptr<BookItem>> bookItems;  // Barcode -> BookItem
    unordered_map<string, unique_ptr<Member>> members;      // MemberID -> Member
    unordered_map<string, unique_ptr<Lending>> lendings;    // LendingID -> Lending
    unordered_map<string, vector<string>> activeLendings;   // MemberID -> LendingIDs
    
    int bookItemCounter;
    
    Library(const string& n) : name(n), bookItemCounter(0) {}
    
public:
    static Library* getInstance(const string& name = "City Library") {
        if (instance == nullptr) {
            instance = new Library(name);
        }
        return instance;
    }
    
    // Add book to library
    void addBook(const string& isbn, const string& title, const string& author,
                 const string& subject, int copies = 1) {
        
        auto it = books.find(isbn);
        if (it != books.end()) {
            // Book exists, add more copies
            it->second->addCopy();
            for (int i = 0; i < copies; i++) {
                string barcode = isbn + "-" + to_string(++bookItemCounter);
                bookItems[barcode] = make_unique<BookItem>(barcode, it->second.get());
            }
            cout << "Added " << copies << " more copies of: " << title << endl;
        } else {
            // New book
            auto book = make_unique<Book>(isbn, title, author, subject, copies);
            Book* bookPtr = book.get();
            books[isbn] = move(book);
            
            for (int i = 0; i < copies; i++) {
                string barcode = isbn + "-" + to_string(++bookItemCounter);
                bookItems[barcode] = make_unique<BookItem>(barcode, bookPtr);
            }
            cout << "Added new book: " << title << " with " << copies << " copies" << endl;
        }
    }
    
    // Register member
    void registerMember(const string& id, const string& name, const string& email,
                       MembershipType type = MembershipType::STANDARD) {
        if (members.find(id) != members.end()) {
            cout << "Member already registered!" << endl;
            return;
        }
        
        members[id] = make_unique<Member>(id, name, email, type);
        cout << "Member registered: " << name << endl;
    }
    
    // Search books
    vector<Book*> searchByTitle(const string& title) const {
        vector<Book*> results;
        for (const auto& [isbn, book] : books) {
            if (book->getTitle().find(title) != string::npos) {
                results.push_back(book.get());
            }
        }
        return results;
    }
    
    vector<Book*> searchByAuthor(const string& author) const {
        vector<Book*> results;
        for (const auto& [isbn, book] : books) {
            if (book->getAuthor().find(author) != string::npos) {
                results.push_back(book.get());
            }
        }
        return results;
    }
    
    // Issue book
    bool issueBook(const string& memberId, const string& isbn) {
        // Check member exists
        auto memberIt = members.find(memberId);
        if (memberIt == members.end()) {
            cout << "Member not found!" << endl;
            return false;
        }
        
        Member* member = memberIt->second.get();
        
        // Check if member can issue more books
        if (!member->canIssueBook()) {
            cout << "Member has reached maximum book limit!" << endl;
            return false;
        }
        
        // Find available book item
        BookItem* availableItem = nullptr;
        for (auto& [barcode, item] : bookItems) {
            if (item->getBook()->getISBN() == isbn && item->isAvailable()) {
                availableItem = item.get();
                break;
            }
        }
        
        if (availableItem == nullptr) {
            cout << "No available copy of this book!" << endl;
            return false;
        }
        
        // Create lending record
        auto lending = make_unique<Lending>(availableItem, member);
        string lendingId = lending->getLendingId();
        
        // Update states
        availableItem->setStatus(BookStatus::ISSUED);
        member->issueBook(availableItem->getBarcode());
        activeLendings[memberId].push_back(lendingId);
        
        cout << "\nBook issued successfully!" << endl;
        lending->display();
        
        lendings[lendingId] = move(lending);
        
        return true;
    }
    
    // Return book
    bool returnBook(const string& memberId, const string& barcode) {
        auto memberIt = members.find(memberId);
        if (memberIt == members.end()) {
            cout << "Member not found!" << endl;
            return false;
        }
        
        Member* member = memberIt->second.get();
        
        // Find the lending record
        Lending* lendingRecord = nullptr;
        string lendingId;
        
        for (const auto& lid : activeLendings[memberId]) {
            if (lendings[lid]->getBookItem()->getBarcode() == barcode) {
                lendingRecord = lendings[lid].get();
                lendingId = lid;
                break;
            }
        }
        
        if (lendingRecord == nullptr) {
            cout << "No lending record found!" << endl;
            return false;
        }
        
        // Process return
        lendingRecord->setReturnDate();
        lendingRecord->getBookItem()->setStatus(BookStatus::AVAILABLE);
        member->returnBook(barcode);
        
        // Remove from active lendings
        auto& lendings = activeLendings[memberId];
        lendings.erase(remove(lendings.begin(), lendings.end(), lendingId), lendings.end());
        
        cout << "\nBook returned successfully!" << endl;
        lendingRecord->display();
        
        double fine = lendingRecord->calculateFine();
        if (fine > 0) {
            cout << "⚠️  Late return fine: $" << fine << endl;
        }
        
        return true;
    }
    
    // Display available books
    void displayAvailableBooks() const {
        cout << "\n========== AVAILABLE BOOKS ==========" << endl;
        
        unordered_map<string, int> availableCount;
        
        for (const auto& [barcode, item] : bookItems) {
            if (item->isAvailable()) {
                string isbn = item->getBook()->getISBN();
                availableCount[isbn]++;
            }
        }
        
        for (const auto& [isbn, count] : availableCount) {
            books.at(isbn)->display();
            cout << "Available copies: " << count << endl << endl;
        }
        cout << "=====================================" << endl;
    }
    
    // Display member info
    void displayMemberInfo(const string& memberId) const {
        auto it = members.find(memberId);
        if (it == members.end()) {
            cout << "Member not found!" << endl;
            return;
        }
        
        cout << "\n========== MEMBER INFO ==========" << endl;
        it->second->display();
        
        // Show active lendings
        auto lendIt = activeLendings.find(memberId);
        if (lendIt != activeLendings.end() && !lendIt->second.empty()) {
            cout << "\nActive Lendings:" << endl;
            for (const auto& lendingId : lendIt->second) {
                lendings.at(lendingId)->display();
            }
        }
        cout << "=================================" << endl;
    }
    
    static void cleanup() {
        delete instance;
        instance = nullptr;
    }
};

Library* Library::instance = nullptr;

// ============== Demo ==============

int main() {
    Library* library = Library::getInstance("Central Library");
    
    // Add books
    library->addBook("978-0132350884", "Clean Code", "Robert Martin", "Programming", 3);
    library->addBook("978-0201633610", "Design Patterns", "Gang of Four", "Programming", 2);
    library->addBook("978-0596007126", "Head First Design Patterns", "Freeman", "Programming", 2);
    
    // Register members
    library->registerMember("M001", "Alice Johnson", "alice@email.com", MembershipType::STANDARD);
    library->registerMember("M002", "Bob Smith", "bob@email.com", MembershipType::PREMIUM);
    
    // Display available books
    library->displayAvailableBooks();
    
    // Search books
    cout << "\nSearching for 'Design':" << endl;
    auto results = library->searchByTitle("Design");
    for (auto* book : results) {
        book->display();
    }
    
    // Issue books
    cout << "\n=== Issuing Books ===" << endl;
    library->issueBook("M001", "978-0132350884");
    library->issueBook("M002", "978-0201633610");
    
    // Display member info
    library->displayMemberInfo("M001");
    
    // Return book (simulate late return)
    cout << "\n=== Returning Book ===" << endl;
    library->returnBook("M001", "978-0132350884-1");
    
    // Display updated available books
    library->displayAvailableBooks();
    
    Library::cleanup();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Book vs BookItem**
- `Book`: Metadata (title, author, ISBN)
- `BookItem`: Physical copy with barcode and status
- Allows multiple copies of same book

### 2. **Fine Strategy Pattern**
- Different fine calculations for member types
- Easy to add new strategies
- Encapsulates fine logic

### 3. **Lending Record**
- Tracks complete lending lifecycle
- Calculates fines automatically
- Maintains history

---

## Follow-up Questions

**Q1: How to add book reservation?**
```cpp
class Reservation {
    Member* member;
    Book* book;
    time_t reservationDate;
    bool isNotified;
};

// When book returned, notify reserved members
```

**Q2: How to handle lost books?**
```cpp
void reportLostBook(string barcode) {
    bookItem->setStatus(BookStatus::LOST);
    member->chargeFine(bookItem->getBook()->getPrice());
}
```

**Q3: How to add different book categories?**
```cpp
enum class BookCategory {
    REFERENCE,  // Cannot be issued
    GENERAL,    // Normal lending
    RESTRICTED  // Special permission needed
};
```

**Q4: How to generate reports?**
```cpp
class ReportGenerator {
    void generateMostIssuedBooks();
    void generateOverdueReport();
    void generateMemberActivity();
};
```

---

## Compilation & Execution

```bash
g++ -std=c++17 library_management.cpp -o library
./library
```

---

**Next Problem**: `04-vending-machine.md`

