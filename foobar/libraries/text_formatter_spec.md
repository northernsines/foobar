# TEXT_FORMATTER Library Specification

**Version:** 2.0  
**Language:** FOOBAR  
**Purpose:** Text formatting and console UI utilities for creating professional-looking terminal output

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Initialization](#initialization)
4. [Basic String Utilities](#basic-string-utilities)
5. [Box Drawing Methods](#box-drawing-methods)
6. [Headers and Dividers](#headers-and-dividers)
7. [Text Alignment](#text-alignment)
8. [Configuration](#configuration)
9. [Usage Examples](#usage-examples)
10. [Method Reference](#method-reference)

---

## Overview

The TEXT_FORMATTER library provides a comprehensive set of text formatting utilities for creating well-structured console output. It handles text alignment, box drawing, headers, dividers, and spacing with configurable width settings.

**Key Features:**
- Automatic width management (defaults to 80 columns)
- Auto-sizing boxes that adapt to content
- Multiple box and border styles
- Text alignment (left, center, right)
- Customizable dividers and section headers
- No manual width calculations needed

---

## Installation

1. Place `text_formatter.foob` in your project's `libraries/` directory
2. Import in your FOOBAR file:

```foobar
import "libraries/text_formatter.foob";
```

---

## Initialization

### Default Initialization (80 columns)

```foobar
TEXT_FORMATTER fmt = new TEXT_FORMATTER();
```

Creates a formatter with default width of 80 columns (standard terminal width).

### Custom Width Initialization

```foobar
TEXT_FORMATTER narrow = new TEXT_FORMATTER(40);
TEXT_FORMATTER wide = new TEXT_FORMATTER(120);
```

Creates a formatter with a custom default width.

---

## Basic String Utilities

### Repeat
**Signature:** `string Repeat(string text, integer times)`  
**Returns:** String with `text` repeated `times` times

```foobar
string stars = fmt.Repeat("*", 10);  // "**********"
string dashes = fmt.Repeat("-", 5);  // "-----"
```

**Use cases:**
- Creating borders
- Building dividers
- Repeating decorative characters

---

### PadLeft
**Signature:** `string PadLeft(string text, integer width)`  
**Returns:** String with left padding (spaces) to reach `width`

```foobar
string aligned = fmt.PadLeft("Right", 20);
// "               Right"
```

**Use cases:**
- Right-aligning text
- Creating columns
- Adding indentation

---

### PadRight
**Signature:** `string PadRight(string text, integer width)`  
**Returns:** String with right padding (spaces) to reach `width`

```foobar
string aligned = fmt.PadRight("Left", 20);
// "Left                "
```

**Use cases:**
- Left-aligning text in a fixed width
- Creating uniform-width strings
- Building table columns

---

### Center
**Signature:** `string Center(string text, integer width)`  
**Returns:** String centered in `width` with equal padding on both sides

```foobar
string centered = fmt.Center("Hello", 20);
// "       Hello        "
```

**Note:** If padding is odd, the extra space goes on the right side.

**Use cases:**
- Centering titles
- Creating balanced layouts
- Menu options

---

## Box Drawing Methods

### PrintBox
**Signature:** `void PrintBox(string message)`  
**Output:** Draws a box that auto-sizes to message content (minimum 20 chars wide)

```foobar
fmt.PrintBox("Hello!");
```

**Output:**
```
********************
* Hello!           *
********************
```

**Features:**
- Auto-sizes to content
- Minimum width of 20 characters
- Properly padded on both sides

---

### PrintBoxCentered
**Signature:** `void PrintBoxCentered(string message)`  
**Output:** Draws a box at default width with centered message

```foobar
fmt.PrintBoxCentered("Important!");
```

**Output (80 columns):**
```
********************************************************************************
*                                  Important!                                  *
********************************************************************************
```

**Use cases:**
- Highlighting important messages
- Creating centered alerts
- Emphasis in full-width layouts

---

### PrintBoxMultiline
**Signature:** `void PrintBoxMultiline(string message, integer width)`  
**Output:** Draws a box with custom width

```foobar
fmt.PrintBoxMultiline("Custom width box", 30);
```

**Output:**
```
******************************
* Custom width box          *
******************************
```

**Use cases:**
- Creating boxes of specific sizes
- Matching existing layout widths
- Building complex UIs

---

### PrintFancyBox
**Signature:** `void PrintFancyBox(string message)`  
**Output:** Draws a box with double-line style borders

```foobar
fmt.PrintFancyBox("Fancy!");
```

**Output:**
```
====================
| Fancy!           |
====================
```

**Use cases:**
- Distinguishing different box types
- Creating visual hierarchy
- Special notices or warnings

---

## Headers and Dividers

### PrintHeader
**Signature:** `void PrintHeader(string title)`  
**Output:** Full-width header with centered title and decorative borders

```foobar
fmt.PrintHeader("Section 1");
```

**Output (80 columns):**
```

================================================================================
                                  Section 1                                    
================================================================================

```

**Features:**
- Blank lines above and below
- Centered title
- Full default width

**Use cases:**
- Section headings
- Major divisions in output
- Program titles

---

### PrintDivider
**Signature:** `void PrintDivider()`  
**Output:** Horizontal line of dashes at default width

```foobar
fmt.PrintDivider();
```

**Output:**
```
--------------------------------------------------------------------------------
```

---

### PrintDivider (Custom Character)
**Signature:** `void PrintDivider(string character)`  
**Output:** Horizontal line using custom character

```foobar
fmt.PrintDivider("=");
fmt.PrintDivider("*");
fmt.PrintDivider("-");
```

**Use cases:**
- Separating content sections
- Creating visual breaks
- Different emphasis levels

---

### PrintSection
**Signature:** `void PrintSection(string title)`  
**Output:** Section title with underline matching title length

```foobar
fmt.PrintSection("Configuration");
```

**Output:**
```

Configuration
-------------

```

**Features:**
- Blank lines above and below
- Underline matches title length
- Less prominent than PrintHeader

**Use cases:**
- Subsection headings
- Grouping related content
- Creating hierarchy

---

### PrintTitle
**Signature:** `void PrintTitle(string title)`  
**Output:** Large centered title with thick borders

```foobar
fmt.PrintTitle("MY PROGRAM");
```

**Output:**
```

================================================================================
                                  MY PROGRAM                                   
================================================================================

```

**Use cases:**
- Program startup banners
- Major announcements
- Welcome screens

---

## Text Alignment

### PrintCentered
**Signature:** `void PrintCentered(string text)`  
**Output:** Prints text centered at default width

```foobar
fmt.PrintCentered("Centered text");
```

**Use cases:**
- Menu options
- Centered messages
- Balanced layouts

---

### PrintRightAligned
**Signature:** `void PrintRightAligned(string text)`  
**Output:** Prints text right-aligned at default width

```foobar
fmt.PrintRightAligned("Right side");
```

**Use cases:**
- Timestamps
- Version numbers
- Status indicators

---

## Configuration

### SetDefaultWidth
**Signature:** `void SetDefaultWidth(integer width)`  
**Effect:** Changes the default width for all future operations

```foobar
fmt.SetDefaultWidth(100);  // Now all operations use 100 columns
```

**Use cases:**
- Adapting to different terminal sizes
- Creating responsive layouts
- Switching between wide and narrow modes

---

### GetDefaultWidth
**Signature:** `integer GetDefaultWidth()`  
**Returns:** Current default width setting

```foobar
integer currentWidth = fmt.GetDefaultWidth();
CONSOLE.PrintInteger(currentWidth);  // 80
```

**Use cases:**
- Querying current settings
- Saving/restoring width configurations
- Debugging layout issues

---

## Usage Examples

### Example 1: Simple Program Banner

```foobar
import "libraries/text_formatter.foob";

Main() {
    TEXT_FORMATTER fmt = new TEXT_FORMATTER();
    
    fmt.PrintTitle("CALCULATOR v1.0");
    fmt.PrintDivider();
    
    CONSOLE.Print("Ready for input...");
    
    return true;
}
```

**Output:**
```

================================================================================
                              CALCULATOR v1.0                                  
================================================================================

--------------------------------------------------------------------------------
Ready for input...
```

---

### Example 2: Menu System

```foobar
import "libraries/text_formatter.foob";

Main() {
    TEXT_FORMATTER fmt = new TEXT_FORMATTER();
    
    fmt.PrintHeader("Main Menu");
    fmt.PrintCentered("1. New Game");
    fmt.PrintCentered("2. Load Game");
    fmt.PrintCentered("3. Settings");
    fmt.PrintCentered("4. Exit");
    fmt.PrintDivider();
    
    return true;
}
```

---

### Example 3: Structured Report

```foobar
import "libraries/text_formatter.foob";

Main() {
    TEXT_FORMATTER fmt = new TEXT_FORMATTER();
    
    fmt.PrintTitle("SALES REPORT");
    
    fmt.PrintSection("Q1 Results");
    CONSOLE.Print("  Revenue: $50,000");
    CONSOLE.Print("  Expenses: $30,000");
    fmt.PrintDivider("-");
    
    fmt.PrintSection("Q2 Results");
    CONSOLE.Print("  Revenue: $60,000");
    CONSOLE.Print("  Expenses: $32,000");
    fmt.PrintDivider("-");
    
    fmt.PrintBox("Total Profit: $48,000");
    
    return true;
}
```

---

### Example 4: Alert/Warning System

```foobar
import "libraries/text_formatter.foob";

Main() {
    TEXT_FORMATTER fmt = new TEXT_FORMATTER();
    
    // Info message
    fmt.PrintBox("Info: Process started");
    CONSOLE.Print("");
    
    // Warning message
    fmt.PrintFancyBox("Warning: Low disk space");
    CONSOLE.Print("");
    
    // Critical message
    fmt.PrintBoxCentered("ERROR: Connection failed");
    
    return true;
}
```

---

### Example 5: Narrow Layout

```foobar
import "libraries/text_formatter.foob";

Main() {
    // Create narrow formatter for small displays
    TEXT_FORMATTER mini = new TEXT_FORMATTER(40);
    
    mini.PrintHeader("Compact");
    mini.PrintBox("Small box");
    mini.PrintDivider();
    mini.PrintCentered("Centered");
    
    return true;
}
```

---

## Method Reference

### Quick Reference Table

| Method | Parameters | Returns | Purpose |
|--------|------------|---------|---------|
| `Initialize()` | none | void | Default 80-column formatter |
| `Initialize(width)` | integer | void | Custom width formatter |
| `Repeat(text, times)` | string, integer | string | Repeat string N times |
| `PadLeft(text, width)` | string, integer | string | Left-pad to width |
| `PadRight(text, width)` | string, integer | string | Right-pad to width |
| `Center(text, width)` | string, integer | string | Center in width |
| `PrintBox(message)` | string | void | Auto-sized box |
| `PrintBoxCentered(message)` | string | void | Centered box |
| `PrintBoxMultiline(message, width)` | string, integer | void | Custom width box |
| `PrintFancyBox(message)` | string | void | Double-line box |
| `PrintHeader(title)` | string | void | Full-width header |
| `PrintDivider()` | none | void | Dash divider |
| `PrintDivider(character)` | string | void | Custom divider |
| `PrintSection(title)` | string | void | Section header |
| `PrintTitle(title)` | string | void | Large title |
| `PrintCentered(text)` | string | void | Print centered |
| `PrintRightAligned(text)` | string | void | Print right-aligned |
| `SetDefaultWidth(width)` | integer | void | Change default width |
| `GetDefaultWidth()` | none | integer | Get current width |

---

## Design Philosophy

### Auto-sizing vs. Fixed Width

The library uses two approaches:

**Auto-sizing methods** (adapt to content):
- `PrintBox()` - Grows with message
- `PrintFancyBox()` - Grows with message
- `PrintSection()` - Underline matches title

**Fixed-width methods** (use default width):
- `PrintHeader()` - Full width
- `PrintBoxCentered()` - Full width
- `PrintDivider()` - Full width
- `PrintCentered()` - Full width
- `PrintRightAligned()` - Full width

### Width Hierarchy

1. **Explicit width parameters** (highest priority)
   - `PrintBoxMultiline(message, 50)` uses 50
   - `Center(text, 30)` uses 30

2. **Default width** (set at initialization or via `SetDefaultWidth()`)
   - `PrintHeader()` uses default
   - `PrintDivider()` uses default

3. **Auto-calculated width** (lowest priority)
   - `PrintBox()` calculates from message length
   - Minimum width constraints apply (e.g., 20 chars)

---

## Best Practices

### 1. Choose Appropriate Width

```foobar
// For standard terminals
TEXT_FORMATTER fmt = new TEXT_FORMATTER();  // 80 columns

// For wide displays
TEXT_FORMATTER wide = new TEXT_FORMATTER(120);

// For mobile/narrow
TEXT_FORMATTER narrow = new TEXT_FORMATTER(40);
```

### 2. Consistent Formatting

```foobar
// Use the same formatter instance for consistent width
TEXT_FORMATTER fmt = new TEXT_FORMATTER();

fmt.PrintHeader("Section 1");
fmt.PrintDivider();
// All output maintains 80-column width
```

### 3. Visual Hierarchy

```foobar
fmt.PrintTitle("Application Name");      // Largest - program title
fmt.PrintHeader("Major Section");         // Large - main sections
fmt.PrintSection("Subsection");           // Medium - subsections
fmt.PrintDivider();                       // Small - separators
```

### 4. Box Usage

```foobar
// Short messages - auto-size
fmt.PrintBox("OK");

// Important messages - centered
fmt.PrintBoxCentered("Warning: Action required");

// Different styles for different purposes
fmt.PrintBox("Info");           // Standard
fmt.PrintFancyBox("Warning");   // Emphasis
```

### 5. Avoiding Common Mistakes

```foobar
// DON'T: Mix formatters with different widths inconsistently
TEXT_FORMATTER fmt1 = new TEXT_FORMATTER(80);
TEXT_FORMATTER fmt2 = new TEXT_FORMATTER(40);
fmt1.PrintHeader("Title");
fmt2.PrintDivider();  // Will be narrower - looks broken

// DO: Use consistent formatter
TEXT_FORMATTER fmt = new TEXT_FORMATTER();
fmt.PrintHeader("Title");
fmt.PrintDivider();  // Matches width
```

---

## Version History

### Version 2.0 (Current)
- Complete rewrite with configurable width
- Added auto-sizing boxes
- Proper padding on both sides of boxes
- Multiple box styles (standard, fancy)
- Text alignment utilities
- Section headers
- Custom dividers
- Width configuration methods

### Version 1.0 (Legacy)
- Basic `Repeat()`, `Center()`, `PrintBox()`, `PrintHeader()`
- Fixed functionality
- No width configuration
- Unbalanced box padding

---

## License

This library is part of the FOOBAR standard library collection.

---

**END OF SPECIFICATION**
