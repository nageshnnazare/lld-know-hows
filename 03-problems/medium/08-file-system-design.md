# Problem 8: File System Design

**Difficulty**: Medium  
**Time to Solve**: 45-55 minutes  
**Companies**: Google, Dropbox, Amazon

## Problem Statement

Design an in-memory file system that supports:
1. Create/Delete files and directories
2. Navigate through directories (cd, ls)
3. Read/Write file content
4. Move/Copy files
5. Search functionality
6. Permission management (bonus)

---

## Class Diagram

```
┌────────────────────────┐
│    FileSystem          │
├────────────────────────┤
│ - root: Directory      │
│ - current: Directory   │
├────────────────────────┤
│ + mkdir()              │
│ + touch()              │
│ + cd()                 │
│ + ls()                 │
│ + rm()                 │
│ + cat()                │
│ + write()              │
│ + find()               │
└───────┬────────────────┘
        │
    ┌───┴──────┐
    │  Entry   │ (abstract)
    ├──────────┤
    │ - name   │
    │ - parent │
    │ - created│
    └───┬──────┘
        △
   ┌────┴─────┐
   │          │
┌──▽────┐ ┌──▽────┐
│  File │ │  Dir  │
├───────┤ ├───────┤
│-content││-children│
│-size  │ │       │
└───────┘ └───────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <vector>
#include <map>
#include <memory>
#include <string>
#include <sstream>
#include <algorithm>
#include <ctime>

using namespace std;

// ============== Entry (Base class) ==============

enum class EntryType { FILE, DIRECTORY };

class Entry {
protected:
    string name;
    Entry* parent;
    time_t created;
    time_t modified;
    EntryType type;
    
public:
    Entry(const string& n, Entry* p, EntryType t)
        : name(n), parent(p), type(t) {
        created = modified = time(nullptr);
    }
    
    virtual ~Entry() = default;
    
    string getName() const { return name; }
    Entry* getParent() const { return parent; }
    EntryType getType() const { return type; }
    
    bool isFile() const { return type == EntryType::FILE; }
    bool isDirectory() const { return type == EntryType::DIRECTORY; }
    
    virtual void display(int indent = 0) const = 0;
    virtual size_t getSize() const = 0;
    
    string getPath() const {
        if (parent == nullptr) return "/";
        
        vector<string> parts;
        const Entry* current = this;
        
        while (current->parent != nullptr) {
            parts.push_back(current->name);
            current = current->parent;
        }
        
        if (parts.empty()) return "/";
        
        reverse(parts.begin(), parts.end());
        string path = "/";
        for (size_t i = 0; i < parts.size(); i++) {
            path += parts[i];
            if (i < parts.size() - 1) path += "/";
        }
        return path;
    }
};

// ============== File ==============

class File : public Entry {
private:
    string content;
    
public:
    File(const string& name, Entry* parent)
        : Entry(name, parent, EntryType::FILE), content("") {}
    
    string getContent() const { return content; }
    
    void write(const string& data) {
        content = data;
        modified = time(nullptr);
    }
    
    void append(const string& data) {
        content += data;
        modified = time(nullptr);
    }
    
    size_t getSize() const override {
        return content.size();
    }
    
    void display(int indent = 0) const override {
        for (int i = 0; i < indent; i++) cout << "  ";
        cout << name << " (" << content.size() << " bytes)" << endl;
    }
};

// ============== Directory ==============

class Directory : public Entry {
private:
    map<string, unique_ptr<Entry>> children;
    
public:
    Directory(const string& name, Entry* parent)
        : Entry(name, parent, EntryType::DIRECTORY) {}
    
    bool hasChild(const string& name) const {
        return children.find(name) != children.end();
    }
    
    Entry* getChild(const string& name) const {
        auto it = children.find(name);
        return (it != children.end()) ? it->second.get() : nullptr;
    }
    
    File* addFile(const string& name) {
        if (hasChild(name)) {
            cout << "Error: '" << name << "' already exists" << endl;
            return nullptr;
        }
        
        auto file = make_unique<File>(name, this);
        File* filePtr = file.get();
        children[name] = move(file);
        return filePtr;
    }
    
    Directory* addDirectory(const string& name) {
        if (hasChild(name)) {
            cout << "Error: '" << name << "' already exists" << endl;
            return nullptr;
        }
        
        auto dir = make_unique<Directory>(name, this);
        Directory* dirPtr = dir.get();
        children[name] = move(dir);
        return dirPtr;
    }
    
    bool remove(const string& name) {
        auto it = children.find(name);
        if (it != children.end()) {
            children.erase(it);
            return true;
        }
        return false;
    }
    
    vector<Entry*> listContents() const {
        vector<Entry*> contents;
        for (const auto& [name, entry] : children) {
            contents.push_back(entry.get());
        }
        return contents;
    }
    
    size_t getSize() const override {
        size_t total = 0;
        for (const auto& [name, entry] : children) {
            total += entry->getSize();
        }
        return total;
    }
    
    void display(int indent = 0) const override {
        for (int i = 0; i < indent; i++) cout << "  ";
        cout << name << "/" << endl;
        
        for (const auto& [childName, child] : children) {
            child->display(indent + 1);
        }
    }
};

// ============== File System ==============

class FileSystem {
private:
    unique_ptr<Directory> root;
    Directory* currentDir;
    
    vector<string> splitPath(const string& path) {
        vector<string> parts;
        stringstream ss(path);
        string part;
        
        while (getline(ss, part, '/')) {
            if (!part.empty() && part != ".") {
                parts.push_back(part);
            }
        }
        
        return parts;
    }
    
    Directory* navigateToDirectory(const string& path) {
        if (path.empty() || path == ".") {
            return currentDir;
        }
        
        Directory* dir = (path[0] == '/') ? root.get() : currentDir;
        
        vector<string> parts = splitPath(path);
        for (const string& part : parts) {
            if (part == "..") {
                if (dir->getParent() && dir->getParent()->isDirectory()) {
                    dir = static_cast<Directory*>(dir->getParent());
                }
            } else {
                Entry* entry = dir->getChild(part);
                if (!entry || !entry->isDirectory()) {
                    return nullptr;
                }
                dir = static_cast<Directory*>(entry);
            }
        }
        
        return dir;
    }
    
    File* navigateToFile(const string& path) {
        size_t lastSlash = path.find_last_of('/');
        
        Directory* dir;
        string fileName;
        
        if (lastSlash == string::npos) {
            dir = currentDir;
            fileName = path;
        } else {
            string dirPath = path.substr(0, lastSlash);
            fileName = path.substr(lastSlash + 1);
            dir = navigateToDirectory(dirPath.empty() ? "/" : dirPath);
        }
        
        if (!dir) return nullptr;
        
        Entry* entry = dir->getChild(fileName);
        if (entry && entry->isFile()) {
            return static_cast<File*>(entry);
        }
        
        return nullptr;
    }
    
public:
    FileSystem() {
        root = make_unique<Directory>("root", nullptr);
        currentDir = root.get();
    }
    
    // Create directory
    bool mkdir(const string& path) {
        size_t lastSlash = path.find_last_of('/');
        
        Directory* dir;
        string dirName;
        
        if (lastSlash == string::npos) {
            dir = currentDir;
            dirName = path;
        } else {
            string parentPath = path.substr(0, lastSlash);
            dirName = path.substr(lastSlash + 1);
            dir = navigateToDirectory(parentPath.empty() ? "/" : parentPath);
        }
        
        if (!dir) {
            cout << "Error: Parent directory not found" << endl;
            return false;
        }
        
        Directory* newDir = dir->addDirectory(dirName);
        if (newDir) {
            cout << "✓ Created directory: " << newDir->getPath() << endl;
            return true;
        }
        return false;
    }
    
    // Create file
    bool touch(const string& path) {
        size_t lastSlash = path.find_last_of('/');
        
        Directory* dir;
        string fileName;
        
        if (lastSlash == string::npos) {
            dir = currentDir;
            fileName = path;
        } else {
            string parentPath = path.substr(0, lastSlash);
            fileName = path.substr(lastSlash + 1);
            dir = navigateToDirectory(parentPath.empty() ? "/" : parentPath);
        }
        
        if (!dir) {
            cout << "Error: Parent directory not found" << endl;
            return false;
        }
        
        File* file = dir->addFile(fileName);
        if (file) {
            cout << "✓ Created file: " << file->getPath() << endl;
            return true;
        }
        return false;
    }
    
    // Change directory
    bool cd(const string& path) {
        Directory* dir = navigateToDirectory(path);
        
        if (dir) {
            currentDir = dir;
            cout << "✓ Changed to: " << getCurrentPath() << endl;
            return true;
        }
        
        cout << "Error: Directory not found" << endl;
        return false;
    }
    
    // List contents
    void ls(const string& path = ".") {
        Directory* dir = (path == ".") ? currentDir : navigateToDirectory(path);
        
        if (!dir) {
            cout << "Error: Directory not found" << endl;
            return;
        }
        
        cout << "\n========== " << dir->getPath() << " ==========" << endl;
        
        vector<Entry*> contents = dir->listContents();
        
        if (contents.empty()) {
            cout << "(empty)" << endl;
        } else {
            for (Entry* entry : contents) {
                if (entry->isDirectory()) {
                    cout << "[DIR]  " << entry->getName() << "/" << endl;
                } else {
                    File* file = static_cast<File*>(entry);
                    cout << "[FILE] " << file->getName()
                         << " (" << file->getSize() << " bytes)" << endl;
                }
            }
        }
        
        cout << "======================================\n" << endl;
    }
    
    // Remove file or directory
    bool rm(const string& path) {
        size_t lastSlash = path.find_last_of('/');
        
        Directory* dir;
        string name;
        
        if (lastSlash == string::npos) {
            dir = currentDir;
            name = path;
        } else {
            string parentPath = path.substr(0, lastSlash);
            name = path.substr(lastSlash + 1);
            dir = navigateToDirectory(parentPath.empty() ? "/" : parentPath);
        }
        
        if (!dir) {
            cout << "Error: Parent directory not found" << endl;
            return false;
        }
        
        if (dir->remove(name)) {
            cout << "✓ Removed: " << name << endl;
            return true;
        }
        
        cout << "Error: Not found" << endl;
        return false;
    }
    
    // Read file
    void cat(const string& path) {
        File* file = navigateToFile(path);
        
        if (!file) {
            cout << "Error: File not found" << endl;
            return;
        }
        
        cout << "\n========== " << file->getName() << " ==========" << endl;
        cout << file->getContent() << endl;
        cout << "==========================================\n" << endl;
    }
    
    // Write to file
    bool write(const string& path, const string& content) {
        File* file = navigateToFile(path);
        
        if (!file) {
            cout << "Error: File not found" << endl;
            return false;
        }
        
        file->write(content);
        cout << "✓ Written to " << file->getName() << " (" << content.size() << " bytes)" << endl;
        return true;
    }
    
    // Display tree
    void tree() {
        cout << "\n========== File System Tree ==========" << endl;
        root->display();
        cout << "======================================\n" << endl;
    }
    
    string getCurrentPath() const {
        return currentDir->getPath();
    }
    
    string pwd() const {
        return getCurrentPath();
    }
};

// ============== Demo ==============

int main() {
    FileSystem fs;
    
    cout << "========== File System Demo ==========\n" << endl;
    
    // Current directory
    cout << "Current: " << fs.pwd() << "\n" << endl;
    
    // Create directories
    cout << "=== Creating Directory Structure ===" << endl;
    fs.mkdir("home");
    fs.mkdir("home/user");
    fs.mkdir("home/user/documents");
    fs.mkdir("home/user/downloads");
    
    // Create files
    cout << "\n=== Creating Files ===" << endl;
    fs.touch("home/user/readme.txt");
    fs.touch("home/user/documents/notes.txt");
    
    // Write to files
    cout << "\n=== Writing to Files ===" << endl;
    fs.write("home/user/readme.txt", "Welcome to the file system!\nThis is a demo.");
    fs.write("home/user/documents/notes.txt", "Meeting notes:\n1. Design review\n2. Implementation");
    
    // Display tree
    fs.tree();
    
    // Navigate
    cout << "=== Navigation ===" << endl;
    fs.cd("home/user");
    fs.ls();
    
    fs.cd("documents");
    fs.ls();
    
    // Read file
    cout << "=== Reading File ===" << endl;
    fs.cat("notes.txt");
    
    // Go back
    fs.cd("..");
    fs.cat("readme.txt");
    
    // List home
    fs.cd("/home");
    fs.ls();
    
    // Remove file
    cout << "=== Removing File ===" << endl;
    fs.rm("user/readme.txt");
    
    // Final tree
    cout << "\n=== Final State ===" << endl;
    fs.tree();
    
    cout << "Current: " << fs.pwd() << endl;
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Composite Pattern**
- Entry base class for File and Directory
- Unified interface for tree operations
- Recursive size calculation

### 2. **Path Resolution**
- Absolute paths (start with /)
- Relative paths from current directory
- Parent navigation (..)

### 3. **Current Directory**
- Stateful navigation (cd)
- Relative operations default to current

---

## Follow-up Questions

**Q1: How to implement file permissions?**
```cpp
enum Permission { READ = 1, WRITE = 2, EXECUTE = 4 };

class Entry {
    int permissions; // rwx format
    string owner;
    bool checkPermission(int perm);
};
```

**Q2: How to support symbolic links?**
```cpp
class SymLink : public Entry {
    Entry* target;
    Entry* resolve();
};
```

**Q3: How to implement file search?**
```cpp
vector<Entry*> find(const string& pattern) {
    // Recursive DFS with pattern matching
    // Support wildcards (* and ?)
}
```

---

## Compilation

```bash
g++ -std=c++17 file_system.cpp -o fs
./fs
```

---

**Next**: `medium/09-chess-game.md`

