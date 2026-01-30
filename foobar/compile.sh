#!/bin/bash

# FOOBAR - Easy Compiler Script
# Just run: ./compile.sh

echo "╔════════════════════════════════════════╗"
echo "║             FOOBAR Compiler            ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Find the compiler relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPILER_DIR="$SCRIPT_DIR/foobar_compiler/compiler"

if [ ! -f "$COMPILER_DIR/foobar.py" ]; then
    echo "❌ Error: Compiler not found at $COMPILER_DIR"
    echo "Expected structure:"
    echo "  foobar/"
    echo "  ├── compile.sh (this script)"
    echo "  └── foobar_compiler/compiler/foobar.py"
    exit 1
fi

# Ask for the file
echo "Enter the path to your .foob file:"
echo "(or just the filename if it's in the current directory)"
read -r FOOB_FILE

# Check if file exists
if [ ! -f "$FOOB_FILE" ]; then
    # Try adding .foob extension if they didn't include it
    if [ -f "${FOOB_FILE}.foob" ]; then
        FOOB_FILE="${FOOB_FILE}.foob"
    else
        echo "❌ Error: File not found: $FOOB_FILE"
        exit 1
    fi
fi

echo ""
echo "Compiling: $FOOB_FILE"
echo ""

# Clear Python cache
rm -rf "$COMPILER_DIR/__pycache__" 2>/dev/null

# Compile
python3 "$COMPILER_DIR/foobar.py" compile "$FOOB_FILE"

if [ $? -eq 0 ]; then
    # Get the executable name (same as .foob file without extension)
    EXECUTABLE="${FOOB_FILE%.foob}"
    
    echo ""
    echo "════════════════════════════════════════"
    echo "✅ Compilation successful!"
    echo "════════════════════════════════════════"
    echo ""
    echo "Run your program:"
    echo "  $EXECUTABLE"
    echo ""
    
    # Ask if they want to run it now
    read -p "Run it now? (y/n): " RUN_NOW
    if [ "$RUN_NOW" = "y" ] || [ "$RUN_NOW" = "Y" ]; then
        echo ""
        echo "--- Output ---"
        "$EXECUTABLE"
        echo "--- End ---"
    fi
else
    echo ""
    echo "❌ Compilation failed"
fi