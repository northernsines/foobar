# FOOBAR Language Specification (Complete)
**Version 1.0**

**FOOBAR** stands for **Functional Object Oriented Blended And Robust Language**.

FOOBAR is a statically typed, imperative, object-oriented programming language with functional-style data transformation utilities. The language prioritizes readability, explicitness, and predictable behavior over syntactic cleverness.

---

## Table of Contents

1. [Design Philosophy](#1-design-philosophy)
2. [Lexical Structure](#2-lexical-structure)
3. [Naming and Casing Conventions](#3-naming-and-casing-conventions)
4. [Data Types](#4-data-types)
5. [Variables](#5-variables)
6. [Operators](#6-operators)
7. [Operator Precedence](#7-operator-precedence)
8. [Arrays](#8-arrays)
9. [Comments](#9-comments)
10. [Entry Point and Program Control](#10-entry-point-and-program-control)
11. [Methods](#11-methods)
12. [Classes and Object-Oriented Programming](#12-classes-and-object-oriented-programming)
13. [Inheritance](#13-inheritance)
14. [Enumerations](#14-enumerations)
15. [Control Flow Statements](#15-control-flow-statements)
16. [Functional Programming Features](#16-functional-programming-features)
17. [Lambda Expressions](#17-lambda-expressions)
18. [Console I/O](#18-console-io)
19. [Complete Grammar Reference](#19-complete-grammar-reference)
20. [Code Examples](#20-code-examples)

---

## 1. Design Philosophy

FOOBAR is designed with the following principles:

- **Object-oriented and imperative at its core** - Classes, methods, and mutable state are first-class concepts
- **Functional features as convenience tools** - Functional programming features like `map`, `filter`, and `reduce` exist to make common array operations easier, but are not enforced paradigms
- **Explicit types and return values** - All types must be explicitly declared; no implicit type inference
- **Clean, readable syntax over brevity** - Code should be self-documenting and easy to understand
- **No implicit type inference** - Variables and method return types must always be explicitly typed
- **Mutable variables are fully allowed** - Variables can be freely modified after declaration
- **Native compilation** - FOOBAR compiles to C and then to native machine code for maximum performance

---

## 2. Lexical Structure

### 2.1 Character Set

FOOBAR source files use UTF-8 encoding and support standard ASCII characters as well as Unicode characters in string literals.

### 2.2 Whitespace

Whitespace (spaces, tabs, newlines, carriage returns) is used to separate tokens but is otherwise ignored by the compiler. Indentation is stylistic and not syntactically significant.

### 2.3 Identifiers

**Identifiers** are names used for variables, methods, classes, and enumerations.

**Rules:**
- Must start with a letter (a-z, A-Z) or underscore (_)
- Can contain letters, digits (0-9), and underscores
- Case-sensitive
- Cannot be a reserved keyword

**Examples:**
```foobar
myVariable
_privateField
Counter123
PERSON_CLASS
```

### 2.4 Keywords

The following are **reserved keywords** and cannot be used as identifiers:

**Control Flow:**
- `if`, `elseif`, `else`
- `loop`, `for`, `until`
- `return`

**Object-Oriented:**
- `class`
- `new`
- `inherits`
- `thisclass`
- `parent`
- `isa`

**Access Modifiers:**
- `public`
- `private`
- `static`

**Types:**
- `boolean`
- `integer`, `longinteger`
- `float`, `longfloat`
- `string`
- `character`
- `void`
- `enumerated`

**Literals:**
- `true`, `false`

**Operators:**
- `not`

### 2.5 Literals

**Boolean Literals:**
- `true`
- `false`

**Integer Literals:**
- Decimal: `42`, `0`, `-15`

**Floating-Point Literals:**
- Decimal with decimal point: `3.14`, `0.5`, `-2.718`

**String Literals:**
- Enclosed in double quotes: `"Hello, World!"`
- Single quotes also supported: `'Hello'`
- Escape sequences supported:
  - `\n` - newline
  - `\t` - tab
  - `\\` - backslash
  - `\"` - double quote
  - `\'` - single quote

**Character Literals:**
- Single character in single quotes: `'a'`, `'Z'`, `'5'`

**Array Literals:**
- Square brackets with comma-separated elements: `[1, 2, 3, 4, 5]`

---

## 3. Naming and Casing Conventions

These conventions are **stylistic** and not enforced by the compiler, but are strongly recommended:

| Entity Type | Convention | Example |
|------------|-----------|---------|
| **Keywords and datatypes** | flatcase | `integer`, `return`, `loop` |
| **Variables** | camelCase | `myVariable`, `personCount` |
| **Methods** | PascalCase | `GetValue()`, `PrintMessage()` |
| **Classes** | UPPER_SNAKE_CASE | `PERSON`, `BANK_ACCOUNT`, `COUNTER` |
| **Enums** | PascalCase | `Seasons`, `Colors` |
| **Enum values** | lowercase | `winter`, `spring`, `red`, `blue` |

---

## 4. Data Types

FOOBAR is **statically typed** - every variable and expression has a type known at compile time.

### 4.1 Primitive Types

| Type | Description | Size | Example Values |
|------|-------------|------|----------------|
| `boolean` | Boolean value | 1 byte | `true`, `false` |
| `character` | Single character | 1 byte | `'a'`, `'Z'`, `'5'` |
| `integer` | Signed integer | 32-bit | `42`, `-15`, `0` |
| `longinteger` | Long signed integer | 64-bit | `2147483648`, `-9223372036854775808` |
| `float` | Floating-point number | 32-bit | `3.14`, `-0.5` |
| `longfloat` | Double-precision float | 64-bit | `3.141592653589793` |
| `string` | String of characters | Variable | `"Hello"`, `'World'` |
| `void` | No value (for methods only) | N/A | N/A |

### 4.2 Array Types

Arrays are declared by adding `[]` after the base type:

```foobar
integer[] numbers;
string[] names;
boolean[] flags;
```

Arrays are **zero-indexed** and support **negative indexing** (counting from the end).

### 4.3 User-Defined Types

Classes create new types:

```foobar
class PERSON {
    private string name;
}

// PERSON is now a type
PERSON person1;
```

### 4.4 Enumerated Types

Enumerations create types with a fixed set of named values:

```foobar
enumerated Season {winter, spring, summer, autumn};

Season currentSeason = Season.summer;
```

---

## 5. Variables

### 5.1 Variable Declaration

Variables must be declared with an explicit type before use:

```foobar
integer age;
string name;
boolean isActive;
```

### 5.2 Variable Initialization

Variables can be initialized at declaration:

```foobar
integer age = 25;
string name = "Alice";
boolean isActive = true;
```

### 5.3 Variable Assignment

Variables can be assigned new values:

```foobar
age = 30;
name = "Bob";
isActive = false;
```

### 5.4 Array Variable Declaration

Arrays are declared with `[]` after the type:

```foobar
integer[] numbers = [1, 2, 3, 4, 5];
string[] names = ["Alice", "Bob", "Charlie"];
boolean[] flags = [true, false, true];
```

Empty arrays can be declared:

```foobar
integer[] emptyArray = [];
```

### 5.5 Object Variable Declaration

Object variables use the class name as the type:

```foobar
PERSON person = new PERSON("Alice");
COUNTER counter = new COUNTER(0);
```

### 5.6 Variable Scope

- **Local variables** are declared inside methods and are scoped to that method
- **Field variables** are declared inside classes and are scoped to the class instance
- Variables are scoped to the innermost block (`{}`) in which they are declared

---

## 6. Operators

### 6.1 Arithmetic Operators

| Operator | Name | Example | Description |
|----------|------|---------|-------------|
| `+` | Addition | `a + b` | Adds two numbers, or concatenates strings |
| `-` | Subtraction | `a - b` | Subtracts second number from first |
| `*` | Multiplication | `a * b` | Multiplies two numbers |
| `/` | Division | `a / b` | Divides first number by second (integer division for integers) |
| `%` | Modulus | `a % b` | Returns remainder of division |
| `^` | Power | `a ^ b` | Raises a to the power of b |
| `++` | Increment | `a++` or `++a` | Increases value by 1 (postfix or prefix) |
| `--` | Decrement | `a--` or `--a` | Decreases value by 1 (postfix or prefix) |

**Examples:**
```foobar
integer sum = 5 + 3;        // 8
integer diff = 10 - 4;      // 6
integer product = 6 * 7;    // 42
integer quotient = 20 / 4;  // 5
integer remainder = 17 % 5; // 2
integer power = 2 ^ 3;      // 8

integer x = 5;
x++;                        // x is now 6
++x;                        // x is now 7
x--;                        // x is now 6
```

**String Concatenation:**
```foobar
string greeting = "Hello, " + "World!";  // "Hello, World!"
string message = "Value: " + "42";       // "Value: 42"
```

### 6.2 Comparison Operators

| Operator | Name | Example | Description |
|----------|------|---------|-------------|
| `==` | Equal | `a == b` | True if a equals b |
| `>` | Greater than | `a > b` | True if a is greater than b |
| `<` | Less than | `a < b` | True if a is less than b |
| `>=` | Greater or equal | `a >= b` | True if a is greater than or equal to b |
| `<=` | Less or equal | `a <= b` | True if a is less than or equal to b |

**Examples:**
```foobar
boolean isEqual = (5 == 5);      // true
boolean isGreater = (10 > 5);    // true
boolean isLess = (3 < 7);        // true
boolean isGTE = (5 >= 5);        // true
boolean isLTE = (4 <= 9);        // true
```

### 6.3 Logical Operators

| Operator | Name | Example | Description |
|----------|------|---------|-------------|
| `&` | AND | `a & b` | True if both a and b are true |
| `V` | OR | `a V b` | True if either a or b (or both) are true |
| `VV` | XOR | `a VV b` | True if exactly one of a or b is true |
| `not()` | NOT | `not(a)` | True if a is false, false if a is true |

**Important:** The `V` symbol represents logical OR (from formal logic's ∨ symbol). The `VV` represents XOR.

**Examples:**
```foobar
boolean result1 = true & false;      // false
boolean result2 = true V false;      // true
boolean result3 = true VV false;     // true
boolean result4 = true VV true;      // false
boolean result5 = not(true);         // false
boolean result6 = not(false);        // true
```

### 6.4 Assignment Operator

| Operator | Name | Example | Description |
|----------|------|---------|-------------|
| `=` | Assignment | `a = b` | Assigns the value of b to a |

**Example:**
```foobar
integer x = 10;
x = 20;  // x is now 20
```

### 6.5 Special Operators

| Operator | Name | Example | Description |
|----------|------|---------|-------------|
| `isa` | Type check | `obj isa CLASS` | Returns true if obj is an instance of CLASS or inherits from it |
| `new` | Instantiation | `new CLASS(args)` | Creates a new instance of CLASS |
| `.` | Member access | `obj.field` or `obj.Method()` | Accesses a field or calls a method on an object |
| `[]` | Array access | `arr[index]` | Accesses element at index in array |
| `->` | Lambda arrow | `x -> x * 2` | Defines a lambda expression |

### 6.6 The `not` Operator - Special Rules

The `not` operator has **special syntax rules** to prevent ambiguity:

**RULE 1: `not` must ALWAYS be followed by parentheses**

```foobar
// ✓ CORRECT:
not(condition)
not(x > 5)
not(a & b)

// ✗ INCORRECT:
not condition       // SYNTAX ERROR
not x > 5          // SYNTAX ERROR
```

**RULE 2: `not` can be stacked indefinitely**

```foobar
not(not(condition))              // Valid double negation
not(not(not(x == 5)))           // Valid triple negation
```

**RULE 3: What goes inside the parentheses**

The expression inside `not()` parentheses follows normal expression parsing:

```foobar
not(x == 5)                      // Negates equality check
not(a & b)                       // Negates AND expression
not(x > 5 & y < 10)             // Negates compound condition
not((x + 5) > 10)               // Negates complex expression
```

---

## 7. Operator Precedence

Operators are evaluated in the following order (from highest to lowest precedence):

1. **Parentheses** `()`
2. **Unary operators** `not()`, `++`, `--` (prefix and postfix)
3. **Power** `^` (right-associative)
4. **Multiplicative** `*`, `/`, `%`
5. **Additive** `+`, `-`
6. **Comparison** `==`, `>`, `<`, `>=`, `<=`, `isa`
7. **Logical AND** `&`
8. **Logical OR** `V`
9. **Logical XOR** `VV`
10. **Assignment** `=` (right-associative)

**Examples:**
```foobar
integer result = 2 + 3 * 4;           // 14 (not 20)
boolean check = 5 > 3 & 10 < 20;     // true
boolean flag = not(x > 5) V y < 10;  // not has highest precedence
```

Use parentheses to override precedence:

```foobar
integer result = (2 + 3) * 4;        // 20
boolean check = (a V b) & c;         // Different from a V (b & c)
```

---

## 8. Arrays

### 8.1 Array Declaration and Initialization

Arrays must specify their element type:

```foobar
integer[] numbers = [1, 2, 3, 4, 5];
string[] names = ["Alice", "Bob", "Charlie"];
boolean[] flags = [true, false, true, false];
```

Empty arrays:

```foobar
integer[] empty = [];
```

### 8.2 Array Access

Arrays are **zero-indexed**:

```foobar
integer[] numbers = [10, 20, 30, 40, 50];

integer first = numbers[0];   // 10
integer third = numbers[2];   // 30
integer last = numbers[4];    // 50
```

**Negative indexing** (counting from end):

```foobar
integer[] numbers = [10, 20, 30, 40, 50];

integer last = numbers[-1];      // 50
integer secondLast = numbers[-2]; // 40
```

### 8.3 Array Modification

Array elements can be modified:

```foobar
integer[] numbers = [1, 2, 3];
numbers[0] = 10;         // Array is now [10, 2, 3]
numbers[2] = numbers[1]; // Array is now [10, 2, 2]
```

### 8.4 Array Slicing

FOOBAR supports three types of array slicing operators:

| Operator | Name | Example | Description |
|----------|------|---------|-------------|
| `.,` | Inclusive-Exclusive | `arr[1.,5]` | From index 1 (inclusive) to 5 (exclusive) |
| `,,` | Exclusive-Exclusive | `arr[1,,5]` | From index 1 (exclusive) to 5 (exclusive) |
| `..` | Inclusive-Inclusive | `arr[1..5]` | From index 1 (inclusive) to 5 (inclusive) |

**Examples:**
```foobar
integer[] numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];

integer[] slice1 = numbers[2.,6];   // [2, 3, 4, 5]
integer[] slice2 = numbers[2,,6];   // [3, 4, 5]
integer[] slice3 = numbers[2..6];   // [2, 3, 4, 5, 6]
```

**Slice from beginning:**
```foobar
integer[] numbers = [0, 1, 2, 3, 4, 5];

integer[] first3 = numbers[.,3];    // [0, 1, 2]
integer[] first4 = numbers[..3];    // [0, 1, 2, 3]
```

### 8.5 Array Properties

**`.length` property:**

Returns the number of elements in the array:

```foobar
integer[] numbers = [10, 20, 30, 40, 50];
integer size = numbers.length;  // 5
```

Note: `.length` is a **property**, not a method, so it can be accessed with or without parentheses:

```foobar
integer size1 = numbers.length;    // Valid
integer size2 = numbers.length();  // Also valid (but redundant)
```

### 8.6 Array Methods

Arrays have built-in methods (see [Section 16](#16-functional-programming-features) for details):

- `.map()` - Transform each element
- `.filter()` - Select elements matching a condition
- `.reduce()` - Reduce array to a single value
- `.sort()` - Sort elements
- `.unique()` - Remove duplicates
- `.find()` - Find first element matching condition
- `.print()` - Print array to console

---

## 9. Comments

### 9.1 Single-Line Comments

Single-line comments start with `//` and continue to the end of the line:

```foobar
// This is a single-line comment
integer x = 5;  // This is also a comment
```

### 9.2 Multi-Line Comments

Multi-line comments start with `/*` and end with `*/`:

```foobar
/*
 * This is a multi-line comment
 * It can span multiple lines
 * Useful for documentation
 */
integer y = 10;

/* This can also be on one line */
```

**Important:** Multi-line comments must be properly closed with `*/`. Unclosed comments will cause a syntax error.

---

## 10. Entry Point and Program Control

### 10.1 The Main() Method

Every FOOBAR program must define a `Main()` method as the entry point:

```foobar
Main() {
    // Program code here
    return true;
}
```

**Rules:**
- `Main()` must be defined exactly once
- `Main()` has no parameters
- `Main()` must return a `boolean` value
- `Main()` does not require an explicit return type declaration (it's always `boolean`)

### 10.2 Return Values

- Returning `true` indicates **successful execution** and terminates the program
- Returning `false` indicates **failure**

```foobar
Main() {
    integer result = PerformCalculation();
    if(result > 0) {
        return true;   // Success
    } else() {
        return false;  // Failure
    }
}
```

### 10.3 Program Termination

The program terminates when `Main()` returns. There is no explicit `exit()` or `quit()` function.

---

## 11. Methods

### 11.1 Method Declaration

Methods are declared with a return type, name, parameters, and body:

```foobar
returnType MethodName(paramType1 param1, paramType2 param2) {
    // Method body
    return value;
}
```

**Example:**
```foobar
integer Add(integer a, integer b) {
    return a + b;
}
```

### 11.2 Return Types

All methods (except `Main()` and constructors) must have an explicit return type:

- Primitive types: `integer`, `boolean`, `string`, etc.
- Array types: `integer[]`, `string[]`, etc.
- Class types: `PERSON`, `COUNTER`, etc.
- `void` for methods that don't return a value

**Examples:**
```foobar
integer GetAge() {
    return 25;
}

void PrintMessage() {
    CONSOLE.Print("Hello!");
}

string GetName() {
    return "Alice";
}

integer[] GetNumbers() {
    return [1, 2, 3, 4, 5];
}
```

### 11.3 Parameters

Methods can have zero or more parameters:

```foobar
void NoParameters() {
    CONSOLE.Print("No parameters!");
}

integer Square(integer x) {
    return x * x;
}

integer Add(integer a, integer b) {
    return a + b;
}

string FormatName(string firstName, string lastName) {
    return firstName + " " + lastName;
}
```

### 11.4 Method Calls

Methods are called using their name followed by parentheses with arguments:

```foobar
integer sum = Add(5, 3);
string fullName = FormatName("John", "Doe");
PrintMessage();
```

### 11.5 Access Modifiers

Methods can be `public` or `private`:

- `public` - Accessible from outside the class
- `private` - Only accessible within the class (default)

```foobar
public integer GetValue() {
    return thisclass.value;
}

private void InternalHelper() {
    // Only callable within this class
}
```

### 11.6 Method Overloading

FOOBAR does **not** support method overloading. Each method name must be unique within its scope.

---

## 12. Classes and Object-Oriented Programming

### 12.1 Class Declaration

Classes are declared using the `class` keyword:

```foobar
class CLASS_NAME {
    // Fields
    // Methods
}
```

**Example:**
```foobar
class PERSON {
    private string name;
    private integer age;
    
    public string GetName() {
        return thisclass.name;
    }
}
```

### 12.2 Fields

Fields are variables that belong to a class instance:

```foobar
class COUNTER {
    private integer count;        // Field declaration
    private string label = "Counter";  // Field with initial value
}
```

**Access modifiers:**
- `public` - Accessible from outside the class
- `private` - Only accessible within the class (default)

### 12.3 The Constructor - Initialize()

Every class can have a constructor named `Initialize()`:

```foobar
class PERSON {
    private string name;
    private integer age;
    
    public Initialize(string n, integer a) {
        thisclass.name = n;
        thisclass.age = a;
    }
}
```

**Rules:**
- Constructor must be named `Initialize`
- Constructor does **not** have a return type
- Constructor can have parameters
- Constructor can be `public` or `private`

### 12.4 Object Instantiation

Objects are created using the `new` keyword with the **class name** (not the constructor name):

```foobar
PERSON person = new PERSON("Alice", 30);
COUNTER counter = new COUNTER(0);
```

**Important:** Even though the constructor is named `Initialize`, you instantiate with `new CLASS_NAME()`, NOT `new Initialize()`.

### 12.5 The `thisclass` Keyword

`thisclass` refers to the current instance of the class:

```foobar
class RECTANGLE {
    private integer width;
    private integer height;
    
    public Initialize(integer w, integer h) {
        thisclass.width = w;   // Set this instance's width
        thisclass.height = h;  // Set this instance's height
    }
    
    public integer GetArea() {
        return thisclass.width * thisclass.height;
    }
}
```

**Use cases:**
- Accessing instance fields: `thisclass.fieldName`
- Calling instance methods: `thisclass.MethodName()`
- Distinguishing between parameters and fields with the same name

### 12.6 Member Access

Access fields and methods using the dot operator (`.`):

```foobar
PERSON person = new PERSON("Alice", 30);
string name = person.GetName();
person.SetAge(31);
```

### 12.7 Public vs Private

**Private members** (default):
- Only accessible within the class
- Not accessible from outside

**Public members**:
- Accessible from anywhere
- Can be called or accessed on instances

```foobar
class BANK_ACCOUNT {
    private integer balance;  // Cannot access from outside
    
    public integer GetBalance() {  // Can call from outside
        return thisclass.balance;
    }
    
    private void InternalAudit() {  // Cannot call from outside
        // Internal logic
    }
}
```

### 12.8 Complete Class Example

```foobar
class COUNTER {
    private integer count;
    private string label;
    
    public Initialize(integer startValue, string name) {
        thisclass.count = startValue;
        thisclass.label = name;
    }
    
    public void Increment() {
        thisclass.count = thisclass.count + 1;
    }
    
    public void Decrement() {
        thisclass.count = thisclass.count - 1;
    }
    
    public integer GetCount() {
        return thisclass.count;
    }
    
    public void Reset() {
        thisclass.count = 0;
    }
}

Main() {
    COUNTER myCounter = new COUNTER(5, "MyCounter");
    myCounter.Increment();
    myCounter.Increment();
    integer value = myCounter.GetCount();  // 7
    CONSOLE.PrintInteger(value);
    return true;
}
```

---

## 13. Inheritance

### 13.1 Single Inheritance

A class can inherit from one parent class using the `inherits` keyword:

```foobar
class ANIMAL {
    private string name;
    
    public Initialize(string n) {
        thisclass.name = n;
    }
    
    public string GetName() {
        return thisclass.name;
    }
}

class DOG inherits ANIMAL {
    private string breed;
    
    public Initialize(string n, string b) {
        parent.Initialize(n);  // Call parent constructor
        thisclass.breed = b;
    }
    
    public void Bark() {
        CONSOLE.Print("Woof!");
    }
}
```

### 13.2 Multiple Inheritance

A class can inherit from **multiple** parent classes:

```foobar
class FLYABLE {
    public void Fly() {
        CONSOLE.Print("Flying!");
    }
}

class SWIMMABLE {
    public void Swim() {
        CONSOLE.Print("Swimming!");
    }
}

class DUCK inherits FLYABLE, SWIMMABLE {
    public void Quack() {
        CONSOLE.Print("Quack!");
    }
}

Main() {
    DUCK duck = new DUCK();
    duck.Fly();    // Inherited from FLYABLE
    duck.Swim();   // Inherited from SWIMMABLE
    duck.Quack();  // Own method
    return true;
}
```

### 13.3 The `parent` Keyword

`parent` refers to the parent class and is used to call parent methods:

```foobar
class VEHICLE {
    private integer speed;
    
    public Initialize(integer s) {
        thisclass.speed = s;
    }
    
    public integer GetSpeed() {
        return thisclass.speed;
    }
}

class CAR inherits VEHICLE {
    private string model;
    
    public Initialize(integer s, string m) {
        parent.Initialize(s);  // Call parent's Initialize
        thisclass.model = m;
    }
    
    public void DisplayInfo() {
        integer speed = parent.GetSpeed();  // Call parent's method
        CONSOLE.PrintInteger(speed);
    }
}
```

**Notes on `parent` with multiple inheritance:**
- When a class inherits from multiple parents, `parent.Initialize()` calls the **first parent's** constructor
- To access methods from specific parents, the child class inherits all methods from all parents
- Method name conflicts are resolved by the order of inheritance (first parent takes precedence)

### 13.4 The `isa` Operator

The `isa` operator checks if an object is an instance of a class or inherits from it:

```foobar
class ANIMAL { }
class DOG inherits ANIMAL { }
class CAT inherits ANIMAL { }

Main() {
    DOG myDog = new DOG();
    
    if(myDog isa DOG) {
        CONSOLE.Print("Is a DOG");        // This prints
    }
    
    if(myDog isa ANIMAL) {
        CONSOLE.Print("Is an ANIMAL");    // This prints (inherited)
    }
    
    if(myDog isa CAT) {
        CONSOLE.Print("Is a CAT");        // This does NOT print
    }
    
    return true;
}
```

**Syntax:**
```foobar
object isa CLASS_NAME
```

**Returns:** `boolean` (`true` if object is instance of or inherits from CLASS_NAME)

### 13.5 Accessing Parent Fields

Child classes inherit fields from parent classes, but can only access them if they're `public` or by using inherited public methods:

```foobar
class SHAPE {
    private integer id;
    
    public Initialize(integer shapeId) {
        thisclass.id = shapeId;
    }
    
    public integer GetId() {
        return thisclass.id;
    }
}

class CIRCLE inherits SHAPE {
    private integer radius;
    
    public Initialize(integer shapeId, integer r) {
        parent.Initialize(shapeId);
        thisclass.radius = r;
    }
    
    public void PrintId() {
        // Can't directly access parent.id (it's private)
        // Must use parent's public method:
        integer id = thisclass.GetId();
        CONSOLE.PrintInteger(id);
    }
}
```

---

## 14. Enumerations

### 14.1 Enum Declaration

Enumerations define a type with a fixed set of named values:

```foobar
enumerated EnumName {value1, value2, value3};
```

**Example:**
```foobar
enumerated Season {winter, spring, summer, autumn};
enumerated Color {red, green, blue, yellow};
enumerated Status {pending, approved, rejected};
```

### 14.2 Enum Usage

Access enum values using dot notation:

```foobar
enumerated Season {winter, spring, summer, autumn};

Main() {
    Season current = Season.summer;
    Season next = Season.autumn;
    
    if(current == Season.summer) {
        CONSOLE.Print("It's summer!");
    }
    
    return true;
}
```

### 14.3 Enum Values

Enum values are **lowercase** by convention:

```foobar
enumerated DayOfWeek {monday, tuesday, wednesday, thursday, friday, saturday, sunday};
```

### 14.4 Enum Printing

Enum values can be printed:

```foobar
enumerated Color {red, green, blue};

Main() {
    Color favorite = Color.blue;
    CONSOLE.Print(Color.red);    // Prints: red
    return true;
}
```

---

## 15. Control Flow Statements

### 15.1 If Statements

**Syntax:**
```foobar
if(condition) {
    // Code if condition is true
}
```

**Example:**
```foobar
integer x = 10;
if(x > 5) {
    CONSOLE.Print("x is greater than 5");
}
```

### 15.2 If-Else Statements

**Syntax:**
```foobar
if(condition) {
    // Code if condition is true
} else() {
    // Code if condition is false
}
```

**Important:** The `else` clause must have empty parentheses `else()`.

**Example:**
```foobar
integer x = 3;
if(x > 5) {
    CONSOLE.Print("x is greater than 5");
} else() {
    CONSOLE.Print("x is not greater than 5");
}
```

### 15.3 If-Elseif-Else Statements

**Syntax:**
```foobar
if(condition1) {
    // Code if condition1 is true
} elseif(condition2) {
    // Code if condition2 is true
} elseif(condition3) {
    // Code if condition3 is true
} else() {
    // Code if all conditions are false
}
```

**Example:**
```foobar
integer score = 85;

if(score >= 90) {
    CONSOLE.Print("Grade: A");
} elseif(score >= 80) {
    CONSOLE.Print("Grade: B");
} elseif(score >= 70) {
    CONSOLE.Print("Grade: C");
} elseif(score >= 60) {
    CONSOLE.Print("Grade: D");
} else() {
    CONSOLE.Print("Grade: F");
}
```

### 15.4 Loop For Statement

**Syntax:**
```foobar
loop for(count) {
    // Code to repeat
}
```

The `count` can be:
- A literal number: `loop for(10)`
- A variable: `loop for(repetitions)`
- An expression: `loop for(x + 5)`

**Examples:**
```foobar
// Loop exactly 5 times
loop for(5) {
    CONSOLE.Print("Iteration");
}

// Loop using a variable
integer times = 3;
loop for(times) {
    CONSOLE.Print("Hello");
}

// Loop with expression
integer x = 2;
loop for(x * 5) {  // Loops 10 times
    CONSOLE.Print("Loop");
}
```

### 15.5 Loop Until Statement

**Syntax:**
```foobar
loop until(condition) {
    // Code to repeat until condition becomes true
}
```

The loop continues **until** the condition becomes `true`.

**Examples:**
```foobar
integer counter = 0;
loop until(counter >= 5) {
    counter++;
}
// counter is now 5

integer x = 1;
loop until(x > 100) {
    x = x * 2;
}
// x is now 128
```

**Important:** The condition is checked **before** each iteration, so the loop body may never execute if the condition is initially true.

### 15.6 Break and Continue

FOOBAR does **not** support `break` or `continue` statements. Use conditional logic and loop conditions instead.

---

## 16. Functional Programming Features

FOOBAR includes functional programming features for array transformations. These features use lambda expressions and method chaining.

### 16.1 The `map()` Method

**Purpose:** Transform each element of an array

**Syntax:**
```foobar
newArray = array.map(lambda)
```

**Examples:**
```foobar
integer[] numbers = [1, 2, 3, 4, 5];

// Double each number
integer[] doubled = numbers.map(x -> x * 2);
// Result: [2, 4, 6, 8, 10]

// Square each number
integer[] squared = numbers.map(x -> x * x);
// Result: [1, 4, 9, 16, 25]

// Add 10 to each number
integer[] added = numbers.map(x -> x + 10);
// Result: [11, 12, 13, 14, 15]
```

### 16.2 The `filter()` Method

**Purpose:** Select elements that satisfy a condition

**Syntax:**
```foobar
newArray = array.filter(lambda)
```

**Examples:**
```foobar
integer[] numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// Keep only even numbers
integer[] evens = numbers.filter(x -> x - (x / 2 * 2) == 0);
// Result: [2, 4, 6, 8, 10]

// Keep only numbers greater than 5
integer[] large = numbers.filter(x -> x > 5);
// Result: [6, 7, 8, 9, 10]

// Keep only odd numbers
integer[] odds = numbers.filter(x -> x - (x / 2 * 2) > 0);
// Result: [1, 3, 5, 7, 9]
```

### 16.3 The `reduce()` Method

**Purpose:** Reduce an array to a single value

**Syntax:**
```foobar
// With initial value
result = array.reduce((accumulator, element) -> expression, initialValue)

// Without initial value (uses first element)
result = array.reduce((accumulator, element) -> expression)
```

**Examples:**
```foobar
integer[] numbers = [1, 2, 3, 4, 5];

// Sum all numbers
integer sum = numbers.reduce((acc, x) -> acc + x, 0);
// Result: 15

// Product of all numbers
integer product = numbers.reduce((acc, x) -> acc * x, 1);
// Result: 120

// Find maximum
integer max = numbers.reduce((acc, x) -> acc > x ? acc : x);
// Result: 5 (assuming ternary operator, otherwise use if-then logic)
```

**Note:** When `reduce()` is called without an initial value, it uses the first element as the initial accumulator.

### 16.4 The `sort()` Method

**Purpose:** Sort array elements in ascending order

**Syntax:**
```foobar
sortedArray = array.sort()
```

**Example:**
```foobar
integer[] unsorted = [5, 2, 8, 1, 9, 3];
integer[] sorted = unsorted.sort();
// Result: [1, 2, 3, 5, 8, 9]
```

**Note:** `sort()` creates a new sorted array; it does not modify the original array.

### 16.5 The `unique()` Method

**Purpose:** Remove duplicate elements

**Syntax:**
```foobar
uniqueArray = array.unique()
```

**Example:**
```foobar
integer[] withDupes = [1, 2, 2, 3, 3, 3, 4, 5, 5];
integer[] unique = withDupes.unique();
// Result: [1, 2, 3, 4, 5]
```

### 16.6 The `find()` Method

**Purpose:** Find the first element matching a condition

**Syntax:**
```foobar
element = array.find(lambda)
```

**Example:**
```foobar
integer[] numbers = [1, 2, 3, 8, 9, 10];

integer found = numbers.find(x -> x > 7);
// Result: 8 (first element greater than 7)
```

**Note:** If no element matches, the behavior depends on implementation (may return 0, -1, or throw error).

### 16.7 The `print()` Method

**Purpose:** Print the array to console

**Syntax:**
```foobar
array.print()
```

**Example:**
```foobar
integer[] numbers = [1, 2, 3, 4, 5];
numbers.print();
// Output: [1, 2, 3, 4, 5]
```

### 16.8 Method Chaining

Functional methods can be **chained** together:

```foobar
integer[] numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

integer[] result = numbers
    .filter(x -> x - (x / 2 * 2) > 0)  // Keep odds
    .map(x -> x * 3)                    // Triple them
    .sort();                             // Sort

// Result: [3, 9, 15, 21, 27]
```

**More examples:**
```foobar
integer[] data = [10, 5, 8, 3, 9, 1, 7];

integer[] processed = data
    .filter(x -> x > 4)   // [10, 5, 8, 9, 7]
    .map(x -> x * 2)      // [20, 10, 16, 18, 14]
    .sort()               // [10, 14, 16, 18, 20]
    .unique();            // [10, 14, 16, 18, 20] (no change in this case)
```

---

## 17. Lambda Expressions

Lambda expressions are anonymous functions used primarily with array transformation methods.

### 17.1 Lambda Syntax

**Single parameter:**
```foobar
x -> expression
```

**Multiple parameters:**
```foobar
(x, y) -> expression
```

**Examples:**
```foobar
x -> x * 2
x -> x > 5
x -> x + 10
(acc, x) -> acc + x
(a, b) -> a * b
```

### 17.2 Lambda Parameters

Parameter types are **inferred** from the context (the array being operated on):

```foobar
integer[] numbers = [1, 2, 3];
integer[] doubled = numbers.map(x -> x * 2);  // x is inferred as integer
```

### 17.3 Lambda Body

The body of a lambda is an **expression**, not a statement block:

```foobar
// ✓ CORRECT (expression):
x -> x * 2
x -> x > 5
x -> x + y

// ✗ INCORRECT (trying to use statements):
x -> { return x * 2; }    // NOT SUPPORTED
x -> { integer y = x * 2; return y; }  // NOT SUPPORTED
```

### 17.4 Using Lambdas

Lambdas are used with array methods:

```foobar
// With map
numbers.map(x -> x * 2)

// With filter
numbers.filter(x -> x > 5)

// With reduce
numbers.reduce((acc, x) -> acc + x, 0)

// With find
numbers.find(x -> x == 7)
```

### 17.5 Complex Lambda Expressions

Lambda bodies can be complex expressions:

```foobar
// Arithmetic expression
numbers.map(x -> (x * 2) + 5)

// Comparison expression
numbers.filter(x -> (x > 5) & (x < 10))

// Nested expression
numbers.map(x -> x * x - (x * 2))
```

---

## 18. Console I/O

FOOBAR provides a default `CONSOLE` class for input and output operations.

### 18.1 CONSOLE.Print()

**Purpose:** Print a string to the console

**Syntax:**
```foobar
CONSOLE.Print(stringValue)
```

**Examples:**
```foobar
CONSOLE.Print("Hello, World!");
CONSOLE.Print("This is a message");

string message = "Welcome to FOOBAR";
CONSOLE.Print(message);
```

### 18.2 CONSOLE.PrintInteger()

**Purpose:** Print an integer to the console

**Syntax:**
```foobar
CONSOLE.PrintInteger(integerValue)
```

**Examples:**
```foobar
CONSOLE.PrintInteger(42);
CONSOLE.PrintInteger(-15);

integer x = 100;
CONSOLE.PrintInteger(x);
```

### 18.3 Array Printing

Arrays can be printed using the `.print()` method:

```foobar
integer[] numbers = [1, 2, 3, 4, 5];
numbers.print();  // Output: [1, 2, 3, 4, 5]
```

### 18.4 Enum Printing

Enum values can be printed using `CONSOLE.Print()`:

```foobar
enumerated Color {red, green, blue};

Main() {
    CONSOLE.Print(Color.red);    // Output: red
    Color current = Color.blue;
    CONSOLE.Print(current);      // Output: blue
    return true;
}
```

### 18.5 CONSOLE.Scan()

**Note:** Input functionality is mentioned in the original spec but implementation details may vary. Consult implementation documentation for usage.

---

## 19. Complete Grammar Reference

### 19.1 Program Structure

```
Program := Declaration*

Declaration := ClassDecl
            | EnumDecl
            | MethodDecl
```

### 19.2 Class Declaration

```
ClassDecl := 'class' IDENTIFIER ('inherits' IDENTIFIER (',' IDENTIFIER)*)? '{' ClassMember* '}'

ClassMember := AccessModifier? FieldDecl
            | AccessModifier? MethodDecl
            | AccessModifier? ConstructorDecl

AccessModifier := 'public' | 'private'

FieldDecl := Type IDENTIFIER ('=' Expression)? ';'

MethodDecl := Type IDENTIFIER '(' ParameterList? ')' Block

ConstructorDecl := 'Initialize' '(' ParameterList? ')' Block

ParameterList := Parameter (',' Parameter)*

Parameter := Type IDENTIFIER
```

### 19.3 Enumeration Declaration

```
EnumDecl := 'enumerated' IDENTIFIER '{' IDENTIFIER (',' IDENTIFIER)* '}' ';'
```

### 19.4 Method Declaration (Top-Level)

```
MethodDecl := Type IDENTIFIER '(' ParameterList? ')' Block
           | 'Main' '(' ')' Block

Type := PrimitiveType ('[' ']')?
     | IDENTIFIER ('[' ']')?

PrimitiveType := 'boolean' | 'integer' | 'longinteger' | 'float' | 'longfloat' | 'string' | 'character' | 'void'
```

### 19.5 Statements

```
Block := '{' Statement* '}'

Statement := VarDecl
          | ExpressionStmt
          | ReturnStmt
          | IfStmt
          | LoopStmt

VarDecl := Type IDENTIFIER ('=' Expression)? ';'

ExpressionStmt := Expression ';'

ReturnStmt := 'return' Expression? ';'

IfStmt := 'if' '(' Expression ')' Block
          ('elseif' '(' Expression ')' Block)*
          ('else' '(' ')' Block)?

LoopStmt := 'loop' 'for' '(' Expression ')' Block
         | 'loop' 'until' '(' Expression ')' Block
```

### 19.6 Expressions

```
Expression := Assignment

Assignment := LogicalXOR ('=' Assignment)?

LogicalXOR := LogicalOR ('VV' LogicalOR)*

LogicalOR := LogicalAND ('V' LogicalAND)*

LogicalAND := Comparison ('&' Comparison)*

Comparison := Additive (('==' | '>' | '<' | '>=' | '<=') Additive)*
           | Additive 'isa' IDENTIFIER

Additive := Multiplicative (('+' | '-') Multiplicative)*

Multiplicative := Power (('*' | '/' | '%') Power)*

Power := Unary ('^' Power)?

Unary := 'not' '(' Expression ')'
      | ('++' | '--') Postfix
      | Postfix

Postfix := Primary (PostfixOp)*

PostfixOp := '[' Expression ']'                          // Array access
          | '[' Expression SliceOp Expression ']'        // Array slice
          | '[' SliceOp Expression ']'                   // Slice from 0
          | '.' IDENTIFIER                               // Member access
          | '.' IDENTIFIER '(' ArgumentList? ')'         // Method call
          | '++' | '--'                                  // Postfix increment/decrement

SliceOp := '.,' | ',,' | '..'

Primary := 'new' IDENTIFIER '(' ArgumentList? ')'        // Object creation
        | 'thisclass'                                    // This reference
        | 'parent'                                       // Parent reference
        | Literal
        | IDENTIFIER
        | IDENTIFIER '(' ArgumentList? ')'               // Function call
        | '[' ElementList? ']'                           // Array literal
        | '(' Expression ')'                             // Parenthesized expression

ArgumentList := Argument (',' Argument)*

Argument := Lambda | Expression

Lambda := IDENTIFIER '->' Expression                     // Single parameter
       | '(' IDENTIFIER (',' IDENTIFIER)* ')' '->' Expression  // Multiple parameters

ElementList := Expression (',' Expression)*

Literal := INTEGER | FLOAT | STRING | CHARACTER | 'true' | 'false'
```

---

## 20. Code Examples

### 20.1 Hello World

```foobar
Main() {
    CONSOLE.Print("Hello, World!");
    return true;
}
```

### 20.2 Variables and Arithmetic

```foobar
Main() {
    integer x = 10;
    integer y = 5;
    
    integer sum = x + y;
    integer product = x * y;
    integer power = x ^ 2;
    
    CONSOLE.Print("Sum:");
    CONSOLE.PrintInteger(sum);
    
    CONSOLE.Print("Product:");
    CONSOLE.PrintInteger(product);
    
    CONSOLE.Print("Power:");
    CONSOLE.PrintInteger(power);
    
    return true;
}
```

### 20.3 Simple Class

```foobar
class COUNTER {
    private integer count;
    
    public Initialize(integer startValue) {
        thisclass.count = startValue;
    }
    
    public void Increment() {
        thisclass.count++;
    }
    
    public void Decrement() {
        thisclass.count--;
    }
    
    public integer GetCount() {
        return thisclass.count;
    }
}

Main() {
    COUNTER counter = new COUNTER(5);
    counter.Increment();
    counter.Increment();
    counter.Increment();
    
    integer value = counter.GetCount();
    CONSOLE.PrintInteger(value);  // Prints: 8
    
    return true;
}
```

### 20.4 Inheritance

```foobar
class ANIMAL {
    private string name;
    
    public Initialize(string n) {
        thisclass.name = n;
    }
    
    public string GetName() {
        return thisclass.name;
    }
}

class DOG inherits ANIMAL {
    private string breed;
    
    public Initialize(string n, string b) {
        parent.Initialize(n);
        thisclass.breed = b;
    }
    
    public void Bark() {
        CONSOLE.Print("Woof! My name is:");
        CONSOLE.Print(thisclass.GetName());
    }
}

Main() {
    DOG myDog = new DOG("Rex", "Golden Retriever");
    myDog.Bark();
    
    if(myDog isa DOG) {
        CONSOLE.Print("Is a dog!");
    }
    
    if(myDog isa ANIMAL) {
        CONSOLE.Print("Is an animal!");
    }
    
    return true;
}
```

### 20.5 Functional Programming

```foobar
Main() {
    integer[] numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    
    CONSOLE.Print("Original:");
    numbers.print();
    
    // Filter evens only
    integer[] evens = numbers.filter(x -> x - (x / 2 * 2) == 0);
    CONSOLE.Print("Evens:");
    evens.print();
    
    // Double all numbers
    integer[] doubled = numbers.map(x -> x * 2);
    CONSOLE.Print("Doubled:");
    doubled.print();
    
    // Sum all numbers
    integer sum = numbers.reduce((acc, x) -> acc + x, 0);
    CONSOLE.Print("Sum:");
    CONSOLE.PrintInteger(sum);
    
    // Chained operations
    integer[] result = numbers
        .filter(x -> x > 5)
        .map(x -> x * 3)
        .sort();
    
    CONSOLE.Print("Chained result:");
    result.print();
    
    return true;
}
```

### 20.6 Control Flow

```foobar
Main() {
    integer score = 85;
    
    // If-elseif-else
    if(score >= 90) {
        CONSOLE.Print("Grade: A");
    } elseif(score >= 80) {
        CONSOLE.Print("Grade: B");
    } elseif(score >= 70) {
        CONSOLE.Print("Grade: C");
    } else() {
        CONSOLE.Print("Grade: F");
    }
    
    // Loop for
    CONSOLE.Print("Counting:");
    loop for(5) {
        CONSOLE.Print("Iteration");
    }
    
    // Loop until
    integer counter = 0;
    loop until(counter >= 3) {
        CONSOLE.PrintInteger(counter);
        counter++;
    }
    
    return true;
}
```

### 20.7 Multiple Inheritance

```foobar
class ENGINE {
    private integer horsepower;
    
    public Initialize(integer hp) {
        thisclass.horsepower = hp;
    }
    
    public integer GetHorsepower() {
        return thisclass.horsepower;
    }
}

class BATTERY {
    private integer capacity;
    
    public Initialize(integer cap) {
        thisclass.capacity = cap;
    }
    
    public integer GetCapacity() {
        return thisclass.capacity;
    }
}

class HYBRID_CAR inherits ENGINE, BATTERY {
    private string model;
    
    public Initialize(integer hp, integer cap, string m) {
        parent.Initialize(hp);
        thisclass.capacity = cap;
        thisclass.model = m;
    }
    
    public void DisplayStats() {
        CONSOLE.Print("Hybrid Car Stats:");
        CONSOLE.Print("Horsepower:");
        CONSOLE.PrintInteger(thisclass.GetHorsepower());
        CONSOLE.Print("Battery:");
        CONSOLE.PrintInteger(thisclass.GetCapacity());
    }
}

Main() {
    HYBRID_CAR car = new HYBRID_CAR(300, 85, "Model X");
    car.DisplayStats();
    
    if(car isa HYBRID_CAR) {
        CONSOLE.Print("Is a hybrid car");
    }
    
    if(car isa ENGINE) {
        CONSOLE.Print("Has an engine");
    }
    
    if(car isa BATTERY) {
        CONSOLE.Print("Has a battery");
    }
    
    return true;
}
```

### 20.8 Enumerations

```foobar
enumerated Season {winter, spring, summer, autumn};
enumerated Color {red, green, blue};

Main() {
    Season current = Season.summer;
    
    if(current == Season.summer) {
        CONSOLE.Print("It's summer!");
    }
    
    CONSOLE.Print("Current season:");
    CONSOLE.Print(current);
    
    Color favorite = Color.blue;
    CONSOLE.Print("Favorite color:");
    CONSOLE.Print(favorite);
    
    return true;
}
```

### 20.9 Array Operations

```foobar
Main() {
    integer[] numbers = [5, 2, 8, 1, 9, 3, 2, 5];
    
    CONSOLE.Print("Original:");
    numbers.print();
    
    // Sort
    integer[] sorted = numbers.sort();
    CONSOLE.Print("Sorted:");
    sorted.print();
    
    // Unique
    integer[] unique = numbers.unique();
    CONSOLE.Print("Unique:");
    unique.print();
    
    // Find
    integer found = numbers.find(x -> x > 7);
    CONSOLE.Print("First > 7:");
    CONSOLE.PrintInteger(found);
    
    // Array slicing
    integer[] slice1 = numbers[1.,4];  // Inclusive-exclusive
    CONSOLE.Print("Slice [1.,4]:");
    slice1.print();
    
    integer[] slice2 = numbers[2..5];  // Inclusive-inclusive
    CONSOLE.Print("Slice [2..5]:");
    slice2.print();
    
    return true;
}
```

### 20.10 Complete Program Example

```foobar
// Student gradebook system

class STUDENT {
    private string name;
    private integer[] grades;
    
    public Initialize(string n) {
        thisclass.name = n;
        thisclass.grades = [];
    }
    
    public void AddGrade(integer grade) {
        // Note: Array append not directly supported, would need implementation
        CONSOLE.Print("Adding grade...");
    }
    
    public string GetName() {
        return thisclass.name;
    }
}

class GRADEBOOK {
    private string courseName;
    
    public Initialize(string course) {
        thisclass.courseName = course;
    }
    
    public void DisplayCourse() {
        CONSOLE.Print("Course: ");
        CONSOLE.Print(thisclass.courseName);
    }
}

Main() {
    CONSOLE.Print("=== Student Gradebook System ===");
    
    GRADEBOOK book = new GRADEBOOK("Computer Science 101");
    book.DisplayCourse();
    
    STUDENT alice = new STUDENT("Alice");
    STUDENT bob = new STUDENT("Bob");
    
    CONSOLE.Print("Student 1:");
    CONSOLE.Print(alice.GetName());
    
    CONSOLE.Print("Student 2:");
    CONSOLE.Print(bob.GetName());
    
    // Process some grades
    integer[] grades = [85, 90, 78, 92, 88];
    integer average = grades.reduce((acc, x) -> acc + x, 0) / grades.length;
    
    CONSOLE.Print("Average grade:");
    CONSOLE.PrintInteger(average);
    
    return true;
}
```

---

## Appendix A: Reserved Keywords

Complete list of reserved keywords:

```
and          boolean      character    class        else
elseif       enumerated   false        float        for
if           inherits     integer      longfloat    longinteger
loop         new          not          parent       private
public       return       static       string       thisclass
true         until        void         isa
```

---

## Appendix B: Operators Summary

| Category | Operators |
|----------|-----------|
| Arithmetic | `+` `-` `*` `/` `%` `^` `++` `--` |
| Comparison | `==` `>` `<` `>=` `<=` |
| Logical | `&` `V` `VV` `not()` |
| Assignment | `=` |
| Member Access | `.` |
| Array Access | `[]` |
| Array Slicing | `.,` `,,` `..` |
| Type Check | `isa` |
| Object Creation | `new` |
| Lambda | `->` |

---

## Appendix C: Escape Sequences

Supported escape sequences in strings:

| Escape | Meaning |
|--------|---------|
| `\n` | Newline |
| `\t` | Tab |
| `\\` | Backslash |
| `\"` | Double quote |
| `\'` | Single quote |

---

## Appendix D: Compiler Error Messages

FOOBAR provides helpful error messages:

**Syntax Errors:**
- "Expected semicolon (;) at the end of the statement"
- "Expected closing parenthesis )"
- "Expected closing brace }"
- "Unclosed multi-line comment starting at line X"
- "Unterminated string starting at line X"

**Type Errors:**
- "Expected a type (like integer, boolean, string, or a class name)"
- "Type mismatch: cannot assign X to Y"

**Semantic Errors:**
- "Undefined variable: X"
- "Method X not found in class Y"
- "Cannot access private member X"

---

**END OF SPECIFICATION**

---

This specification covers all features of the FOOBAR programming language in comprehensive detail. For examples and tutorials, see the `examples/` directory in the FOOBAR compiler distribution.
