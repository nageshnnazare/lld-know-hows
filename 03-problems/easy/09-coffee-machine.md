# Problem 9: Coffee Machine

**Difficulty**: Easy  
**Time to Solve**: 25-30 minutes  
**Companies**: Amazon, Google

## Problem Statement

Design a coffee machine that supports:
1. Different coffee types (Espresso, Latte, Cappuccino)
2. Ingredient management (Coffee, Milk, Water, Sugar)
3. Check ingredient availability
4. Make coffee
5. Refill ingredients

---

## Class Diagram

```
┌─────────────────────┐
│   CoffeeMachine     │
├─────────────────────┤
│- ingredients        │
│- recipes            │
├─────────────────────┤
│+ makeCoffee()       │
│+ checkIngredients() │
│+ refill()           │
└──────┬──────────────┘
       │
       │ uses
       ▼
┌─────────────────────┐         ┌─────────────────┐
│      Recipe         │         │   Ingredient    │
├─────────────────────┤         ├─────────────────┤
│- name               │         │- name           │
│- ingredients        │◆───────>│- quantity       │
├─────────────────────┤         │- unit           │
│+ getIngredients()   │         └─────────────────┘
└─────────────────────┘
```

---

## Complete C++ Implementation

```cpp
#include <iostream>
#include <map>
#include <string>
#include <memory>

using namespace std;

// ============== Ingredient ==============

class Ingredient {
private:
    string name;
    int quantity;  // in ml or grams
    string unit;
    
public:
    Ingredient(const string& n, int q, const string& u)
        : name(n), quantity(q), unit(u) {}
    
    string getName() const { return name; }
    int getQuantity() const { return quantity; }
    
    void add(int amount) {
        quantity += amount;
        cout << "Added " << amount << unit << " of " << name << endl;
    }
    
    bool use(int amount) {
        if (quantity >= amount) {
            quantity -= amount;
            return true;
        }
        return false;
    }
    
    void display() const {
        cout << name << ": " << quantity << unit << endl;
    }
};

// ============== Coffee Recipe ==============

class Recipe {
private:
    string coffeeName;
    map<string, int> ingredients;  // ingredient name -> quantity needed
    
public:
    Recipe(const string& name) : coffeeName(name) {}
    
    void addIngredient(const string& ingredient, int quantity) {
        ingredients[ingredient] = quantity;
    }
    
    string getName() const { return coffeeName; }
    
    const map<string, int>& getIngredients() const {
        return ingredients;
    }
    
    void display() const {
        cout << "\n=== " << coffeeName << " Recipe ===" << endl;
        for (const auto& [ingredient, quantity] : ingredients) {
            cout << "  " << ingredient << ": " << quantity << endl;
        }
    }
};

// ============== Coffee Machine ==============

class CoffeeMachine {
private:
    map<string, unique_ptr<Ingredient>> ingredients;
    map<string, unique_ptr<Recipe>> recipes;
    
public:
    CoffeeMachine() {
        // Initialize ingredients
        ingredients["Coffee"] = make_unique<Ingredient>("Coffee", 500, "g");
        ingredients["Milk"] = make_unique<Ingredient>("Milk", 1000, "ml");
        ingredients["Water"] = make_unique<Ingredient>("Water", 2000, "ml");
        ingredients["Sugar"] = make_unique<Ingredient>("Sugar", 200, "g");
        
        // Initialize recipes
        setupRecipes();
    }
    
    void setupRecipes() {
        // Espresso
        auto espresso = make_unique<Recipe>("Espresso");
        espresso->addIngredient("Coffee", 20);
        espresso->addIngredient("Water", 50);
        recipes["Espresso"] = move(espresso);
        
        // Latte
        auto latte = make_unique<Recipe>("Latte");
        latte->addIngredient("Coffee", 20);
        latte->addIngredient("Milk", 150);
        latte->addIngredient("Water", 50);
        recipes["Latte"] = move(latte);
        
        // Cappuccino
        auto cappuccino = make_unique<Recipe>("Cappuccino");
        cappuccino->addIngredient("Coffee", 20);
        cappuccino->addIngredient("Milk", 100);
        cappuccino->addIngredient("Water", 50);
        recipes["Cappuccino"] = move(cappuccino);
        
        // Black Coffee
        auto black = make_unique<Recipe>("Black Coffee");
        black->addIngredient("Coffee", 15);
        black->addIngredient("Water", 100);
        recipes["Black Coffee"] = move(black);
    }
    
    bool checkIngredients(const Recipe& recipe) {
        for (const auto& [ingredientName, quantityNeeded] : recipe.getIngredients()) {
            if (ingredients.find(ingredientName) == ingredients.end()) {
                cout << "Missing ingredient: " << ingredientName << endl;
                return false;
            }
            
            if (ingredients[ingredientName]->getQuantity() < quantityNeeded) {
                cout << "Insufficient " << ingredientName << endl;
                return false;
            }
        }
        return true;
    }
    
    bool makeCoffee(const string& coffeeType) {
        cout << "\n=== Making " << coffeeType << " ===" << endl;
        
        if (recipes.find(coffeeType) == recipes.end()) {
            cout << "Unknown coffee type: " << coffeeType << endl;
            return false;
        }
        
        Recipe* recipe = recipes[coffeeType].get();
        
        // Check ingredients
        if (!checkIngredients(*recipe)) {
            cout << "Cannot make " << coffeeType << ". Please refill ingredients." << endl;
            return false;
        }
        
        // Use ingredients
        for (const auto& [ingredientName, quantityNeeded] : recipe->getIngredients()) {
            ingredients[ingredientName]->use(quantityNeeded);
            cout << "Using " << quantityNeeded << " of " << ingredientName << endl;
        }
        
        cout << "✓ Your " << coffeeType << " is ready! Enjoy!" << endl;
        return true;
    }
    
    void refill(const string& ingredientName, int amount) {
        if (ingredients.find(ingredientName) != ingredients.end()) {
            ingredients[ingredientName]->add(amount);
        } else {
            cout << "Unknown ingredient: " << ingredientName << endl;
        }
    }
    
    void displayInventory() const {
        cout << "\n=== Coffee Machine Inventory ===" << endl;
        for (const auto& [name, ingredient] : ingredients) {
            ingredient->display();
        }
        cout << "================================\n" << endl;
    }
    
    void displayMenu() const {
        cout << "\n=== Coffee Menu ===" << endl;
        for (const auto& [name, recipe] : recipes) {
            cout << "  - " << name << endl;
        }
        cout << "====================\n" << endl;
    }
};

// ============== Demo ==============

int main() {
    CoffeeMachine machine;
    
    cout << "========== Coffee Machine Demo ==========\n" << endl;
    
    // Display menu
    machine.displayMenu();
    
    // Display initial inventory
    machine.displayInventory();
    
    // Make some coffee
    machine.makeCoffee("Espresso");
    machine.makeCoffee("Latte");
    machine.makeCoffee("Cappuccino");
    
    // Check inventory after making coffee
    machine.displayInventory();
    
    // Make more coffee
    machine.makeCoffee("Latte");
    machine.makeCoffee("Latte");
    machine.makeCoffee("Latte");
    machine.makeCoffee("Latte");
    machine.makeCoffee("Latte");
    machine.makeCoffee("Latte");
    
    // Check inventory - milk should be low
    machine.displayInventory();
    
    // Try to make more latte - should fail
    machine.makeCoffee("Latte");
    
    // Refill
    cout << "\n=== Refilling Ingredients ===" << endl;
    machine.refill("Milk", 500);
    machine.refill("Coffee", 200);
    
    machine.displayInventory();
    
    // Now we can make more
    machine.makeCoffee("Latte");
    machine.makeCoffee("Cappuccino");
    
    // Final inventory
    machine.displayInventory();
    
    return 0;
}
```

---

## Key Design Decisions

### 1. **Ingredient Management**
- Track quantity for each ingredient
- Check availability before making coffee
- Support refilling

### 2. **Recipe Pattern**
- Each coffee type has a recipe
- Recipes define ingredient requirements
- Easy to add new coffee types

### 3. **Simple State**
- No complex state machine needed
- Just ingredient tracking
- Clear success/failure feedback

---

## Follow-up Questions

**Q1: How to add pricing?**
```cpp
class Recipe {
    double price;
    double getPrice() const { return price; }
};

class Payment {
    bool acceptPayment(double amount);
};
```

**Q2: How to track sales/statistics?**
```cpp
class CoffeeMachine {
    map<string, int> salesCount;
    double totalRevenue;
    
    void recordSale(const string& coffeeType, double price);
    void displayStatistics();
};
```

**Q3: How to add customization (extra sugar, less milk)?**
```cpp
class CustomOrder {
    string coffeeType;
    map<string, int> modifications;  // ingredient -> adjustment
    
    void addExtra(string ingredient, int amount);
};
```

---

## Compilation

```bash
g++ -std=c++17 coffee_machine.cpp -o coffee
./coffee
```

---

**Next**: `easy/10-snakes-and-ladders.md`

