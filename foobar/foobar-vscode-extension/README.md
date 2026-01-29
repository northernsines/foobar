# FOOBAR Language Support for VSCode v2.0

Complete IntelliSense, autocomplete, and syntax highlighting for FOOBAR v2.0.

## ✨ What You Get

### 🎯 **Tab Autocomplete for EVERYTHING**
- Type `CONSOLE.` → See all console methods
- Type `MATH.` → See all 15 math functions  
- Type `myString.` → See all 8 string methods
- Type `myArray.` → See all 7 array methods
- **With parameter hints!** Just tab through them

### 📚 **All Standard Library Classes**
- CONSOLE (9 methods)
- MATH (13 functions + 2 constants)
- STRING (4 utilities)
- DATETIME (7 functions)
- RANDOM (4 functions)
- FILE (5 functions)

### 💡 **Hover Documentation**
Hover over ANY method to see:
- Full signature
- Parameter types
- Description
- Examples (where applicable)

### 📝 **50+ Code Snippets**
Type shortcut + Tab:
- `main` → Main function template
- `class` → Full class with Initialize
- `ifelse` → If-else (new syntax!)
- `mathmin` → MATH.min()
- `fileread` → FILE.Read()
- And 45+ more!

## 📦 Installation

### Quick Install (Easiest)
```bash
code --install-extension foobar-language-2.0.0.vsix
```

### Manual Install
1. Download `foobar-language-2.0.0.vsix`
2. VSCode → Extensions → `...` menu → "Install from VSIX"
3. Select the file

## 🚀 Usage

Just open a `.foob` file and start typing!

**Try this:**
```foobar
MATH.
```
→ Autocomplete popup with all 15 MATH functions!

```foobar
string name = "test";
name.
```
→ See `.length()`, `.toUpper()`, `.trim()`, etc.

## 🆕 v2.0 Features

✅ **80+ new completions** for standard library  
✅ **Modulus operator** `%` highlighting  
✅ **else syntax** updated (no parens)  
✅ **Parameter placeholders** - tab through them  
✅ **Hover docs** for every method  
✅ **String/Array/Number** instance methods  
✅ **All FOOBAR v2.0 features** supported  

## 💻 Quick Examples

### Auto-complete MATH methods:
```foobar
integer x = MATH.min(5, 10);
float y = MATH.squareRoot(16.0);
float pi = MATH.PI;  // Constant, not function!
```

### Auto-complete String methods:
```foobar
string text = "hello";
string upper = text.toUpper();     // "HELLO"
integer len = text.length();       // 5
string sub = text.substring(0, 3); // "hel"
```

### Auto-complete Array methods:
```foobar
integer[] nums = [1, 2, 3, 4, 5];
integer[] doubled = nums.map(x -> x * 2);
integer[] evens = nums.filter(x -> x % 2 == 0);
integer sum = nums.reduce((acc, x) -> acc + x, 0);
```

## 🐛 Troubleshooting

**Not working?**
1. Make sure file ends in `.foob`
2. Reload window: `Ctrl+Shift+P` → "Reload Window"
3. Check file association: Bottom right corner should say "FOOBAR"

**Want more completions?**
This extension provides completions for the entire FOOBAR v2.0 standard library!

---

**Enjoy coding in FOOBAR! 🚀**
