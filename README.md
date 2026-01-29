# FOOBAR Programming Language

**F**unctional **O**bject **O**riented **B**lended **A**nd **R**obust

A statically-typed programming language that combines object-oriented principles with functional programming features and compiles to native C code.

---

## Overview

FOOBAR is designed to be **readable, explicit, and predictable**. It provides the structure of object-oriented programming with the expressiveness of functional transformations, all while maintaining static type safety and native performance.

### Design Principles

**Object-Oriented at its Core**
- Classes with single and multiple inheritance
- Full encapsulation (`public`, `private`)
- Clear object semantics with `thisclass`, `parent`, and `isa` keywords

**Functional Features as Tools**
- Lambda expressions and method chaining
- Array transformations: `map`, `filter`, `reduce`, `sort`, `unique`, `find`
- Functional utilities complement imperative style

**Statically Typed**
- Explicit type declarations required
- No implicit type inference
- Compile-time type checking

**Readable Syntax**
- `loop for(10)` and `loop until(condition)`
- Logical operators based on formal logic: `&` (AND), `V` (OR), `VV` (XOR)
- Self-documenting keywords

**Native Compilation**
- Compiles to C, then to native machine code
- No interpreter overhead
- Performance comparable to C

---

## Quick Example

```foobar
class COUNTER {
    private integer count;
    
    public Initialize(integer start) {
        thisclass.count = start;
    }
    
    public void Increment() {
        thisclass.count++;
    }
}

Main() {
    COUNTER c = new COUNTER(5);
    c.Increment();
    
    integer[] numbers = [1, 2, 3, 4, 5];
    integer sum = numbers
        .filter(x -> x > 2)
        .reduce((acc, x) -> acc + x, 0);
    
    return true;
}
```

---

## Installation

### Requirements
- **Python 3** (usually pre-installed on macOS/Linux, included with WSL on Windows)
- **GCC** (C compiler)

### macOS & Linux

1. Install dependencies:
   - **macOS**: 
     ```bash
     xcode-select --install  # Installs GCC
     # Python 3 is usually pre-installed. Check with: python3 --version
     ```
   - **Linux**: 
     ```bash
     sudo apt-get install gcc python3  # Ubuntu/Debian
     # Or: sudo yum install gcc python3  # RedHat/CentOS
     ```

2. Make the compile script executable:
   ```bash
   chmod +x compile.sh
   ```

3. Compile and run (easiest way):
   ```bash
   ./compile.sh
   ```
   Then just type the filename of your `.foob` file when prompted!

   *Alternatively, you can compile directly:*
   ```bash
   cd compiler
   python3 foobar.py compile myprogram.foob
   ./myprogram
   ```

### Windows

FOOBAR compiles to C and needs GCC (a C compiler) and Python 3. The easiest way to get these on Windows is through WSL (Windows Subsystem for Linux), which gives you a full Linux environment where everything works seamlessly.

1. Install WSL (one-time setup):
   - Open PowerShell as Administrator
   - Run: `wsl --install`
   - Restart your computer
   - Ubuntu will automatically install (includes GCC and Python 3)

2. Open Ubuntu from the Start menu

3. Navigate to your FOOBAR folder and use it like Linux:
   ```bash
   cd /mnt/c/Users/YourName/path/to/foobar
   chmod +x compile.sh
   ./compile.sh
   ```

**That's it!** The `compile.sh` script works perfectly in WSL - just type your filename when prompted. You get the full easy FOOBAR experience on Windows.

*Note for advanced users: You can use MinGW or other Windows C compilers, but you'll need to handle PATH configuration and dependencies yourself. Make sure you have Python 3 installed.*

---

## VSCode Extension

Get syntax highlighting, IntelliSense, code completion, and snippets for `.foob` files!

### Installation

The VSIX package is already built and ready to install: `foobar-vscode-extension/foobar-language-2.0.0.vsix`

**Option 1: Quick Install (Recommended)**

1. Navigate to the extension folder:
   ```bash
   cd foobar-vscode-extension
   ```

2. Run the install script:
   ```bash
   bash install.sh
   ```

3. Restart VSCode (or reload: `Cmd+Shift+P` → "Reload Window")

**Option 2: Manual Install**

1. Open VSCode
2. Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
3. Type "Install from VSIX" and select it
4. Navigate to `foobar-vscode-extension/foobar-language-2.0.0.vsix` and select it
5. Restart VSCode

### Features

Once installed, open any `.foob` file and enjoy:
- **Syntax Highlighting** - Keywords, types, strings, and operators beautifully colored
- **IntelliSense** - Smart auto-completion for CONSOLE methods, classes, and more
- **Parameter Hints** - See function signatures as you type
- **Code Snippets** - Type `class` and press Tab for instant templates
- **Hover Documentation** - Hover over `map`, `filter`, `reduce` to see usage docs
- **FOOBAR Theme** - Optional custom color theme designed for FOOBAR

Try typing `CONSOLE.` or starting a `class` declaration to see it in action!

---

## Documentation

- **Language Specification**: See `FOOBAR_Specification_Complete.md`
- **Examples**: Check the `examples/` directory
- **Installation**: See `INSTALL_MAC.md` and compiler README

---

## License

FOOBAR Programming Language  
Copyright © 2026 Sonja Wilberding

This program is free software: you can redistribute it and/or modify it under the terms of the **GNU General Public License** as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

---

## Author

**Sonja Wilberding** - 2026

---
