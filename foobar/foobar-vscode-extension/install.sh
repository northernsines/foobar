#!/bin/bash

# FOOBAR VSCode Extension Installation Script

echo "╔════════════════════════════════════════╗"
echo "║  FOOBAR VSCode Extension Installer     ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check if vsce is installed
if ! command -v vsce &> /dev/null; then
    echo "📦 Installing vsce (VSCode Extension Manager)..."
    npm install -g @vscode/vsce
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install vsce"
        echo "Try running: sudo npm install -g @vscode/vsce"
        exit 1
    fi
    echo "✓ vsce installed"
    echo ""
fi

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Must be run from the extension directory"
    echo "Usage: cd foobar-vscode-extension && bash install.sh"
    exit 1
fi

echo "📦 Packaging extension..."
vsce package

if [ $? -ne 0 ]; then
    echo "❌ Failed to package extension"
    exit 1
fi

VSIX_FILE=$(ls *.vsix 2>/dev/null | head -n 1)

if [ -z "$VSIX_FILE" ]; then
    echo "❌ No .vsix file found"
    exit 1
fi

echo "✓ Extension packaged: $VSIX_FILE"
echo ""

echo "📥 Installing extension in VSCode..."
code --install-extension "$VSIX_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "════════════════════════════════════════"
    echo "✅ INSTALLATION COMPLETE!"
    echo "════════════════════════════════════════"
    echo ""
    echo "Next steps:"
    echo "1. Restart VSCode (or reload window: Cmd+Shift+P → 'Reload Window')"
    echo "2. Open any .foob file"
    echo "3. Enjoy IntelliSense! 🎉"
    echo ""
    echo "Try these features:"
    echo "  - Type 'CONSOLE.' to see auto-complete"
    echo "  - Type 'class' and press Tab for a template"
    echo "  - Hover over 'map' or 'filter' to see docs"
    echo "  - Start typing 'CONSOLE.Print(' to see parameter hints"
    echo ""
else
    echo ""
    echo "❌ Installation failed"
    echo ""
    echo "Manual installation:"
    echo "1. Open VSCode"
    echo "2. Press Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows/Linux)"
    echo "3. Type 'Install from VSIX'"
    echo "4. Select: $VSIX_FILE"
    echo ""
fi
