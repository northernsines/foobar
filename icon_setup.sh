#!/bin/bash
# FOOBAR Icon Setup - Ultimate Edition
# One script to rule them all
# Works on macOS, Linux, and Windows (WSL/Cygwin/Git Bash)

# Enable test mode with: TEST_MODE=1 bash setup_icon_ultimate.sh
TEST_MODE="${TEST_MODE:-0}"

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ICON_FILE="$SCRIPT_DIR/icon.png"

# Test if commands will work before executing
test_command() {
    if [ "$TEST_MODE" = "1" ]; then
        echo "[TEST] Would run: $*"
        return 0
    else
        "$@"
    fi
}

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Error handling
error_exit() {
    echo -e "${RED}❌ Error: $1${NC}" >&2
    exit 1
}

# Success message
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Warning message
warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Info message
info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

echo ""
echo -e "${BOLD}${MAGENTA}╔════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${MAGENTA}║  🎨 FOOBAR ICON SETUP - ULTIMATE 🎨    ║${NC}"
echo -e "${BOLD}${MAGENTA}║    Making Dewey Proud Since 2026       ║${NC}"
echo -e "${BOLD}${MAGENTA}╚════════════════════════════════════════╝${NC}"
echo ""

# Verify icon exists
if [ ! -f "$ICON_FILE" ]; then
    error_exit "icon.png not found in $SCRIPT_DIR"
fi

# Detect OS
detect_os() {
    case "$OSTYPE" in
        darwin*)  echo "macos" ;;
        linux*)   echo "linux" ;;
        msys*|mingw*|cygwin*|win32) echo "windows" ;;
        *)        echo "unknown" ;;
    esac
}

OS=$(detect_os)
echo -e "${BOLD}Detected OS:${NC} ${BLUE}$OS${NC}"
echo ""

if [ "$OS" = "unknown" ]; then
    error_exit "Unsupported operating system: $OSTYPE"
fi

#############################################################################
# macOS Setup
#############################################################################
setup_macos() {
    echo -e "${BOLD}${GREEN}🍎 macOS Setup${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Check for Command Line Tools
    if ! command -v sips >/dev/null 2>&1; then
        error_exit "Command Line Tools not installed. Run: xcode-select --install"
    fi
    
    # Step 1: Install fileicon if needed
    echo -e "${BOLD}[1/7]${NC} Checking for fileicon..."
    if ! command -v fileicon >/dev/null 2>&1; then
        warning "fileicon not found"
        
        if command -v brew >/dev/null 2>&1; then
            info "Installing fileicon via Homebrew..."
            if brew install fileicon 2>/dev/null; then
                success "fileicon installed"
            else
                warning "Failed to install fileicon (non-critical)"
            fi
        else
            warning "Homebrew not found. Install it for better reliability:"
            echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            echo "  brew install fileicon"
        fi
    else
        success "fileicon found"
    fi
    echo ""
    
    # Step 2: Convert icon if needed
    echo -e "${BOLD}[2/7]${NC} Preparing icon file..."
    ICON_TYPE=$(file -b --mime-type "$ICON_FILE" 2>/dev/null || echo "unknown")
    
    WORKING_ICON="$ICON_FILE"
    if [[ "$ICON_TYPE" == "image/jpeg" ]] || [[ "$ICON_TYPE" == "image/jpg" ]]; then
        info "Converting JPEG to PNG..."
        TEMP_PNG="/tmp/foobar_icon_$$.png"
        if sips -s format png "$ICON_FILE" --out "$TEMP_PNG" >/dev/null 2>&1; then
            WORKING_ICON="$TEMP_PNG"
            success "Converted to PNG"
        else
            warning "Could not convert, using original"
        fi
    else
        success "Icon format OK ($ICON_TYPE)"
    fi
    echo ""
    
    # Step 3: Create ICNS
    echo -e "${BOLD}[3/7]${NC} Creating ICNS file..."
    ICNS_FILE="$SCRIPT_DIR/foobar.icns"
    ICONSET_DIR="/tmp/foobar_icon_$$.iconset"
    
    mkdir -p "$ICONSET_DIR"
    
    # Generate all required sizes
    SIZES=(16 32 128 256 512)
    FAILED=0
    
    for size in "${SIZES[@]}"; do
        if ! sips -z $size $size "$WORKING_ICON" --out "$ICONSET_DIR/icon_${size}x${size}.png" -s format png >/dev/null 2>&1; then
            FAILED=1
            break
        fi
        
        if [ $size -ne 512 ]; then
            double=$((size * 2))
            sips -z $double $double "$WORKING_ICON" --out "$ICONSET_DIR/icon_${size}x${size}@2x.png" -s format png >/dev/null 2>&1
        fi
    done
    
    # 1024 for retina
    sips -z 1024 1024 "$WORKING_ICON" --out "$ICONSET_DIR/icon_512x512@2x.png" -s format png >/dev/null 2>&1
    
    if [ $FAILED -eq 1 ]; then
        rm -rf "$ICONSET_DIR"
        error_exit "Failed to generate icon sizes"
    fi
    
    # Convert to ICNS
    if ! iconutil -c icns "$ICONSET_DIR" -o "$ICNS_FILE" 2>/dev/null; then
        rm -rf "$ICONSET_DIR"
        error_exit "Failed to create ICNS file"
    fi
    
    rm -rf "$ICONSET_DIR"
    [ -f "$TEMP_PNG" ] && rm -f "$TEMP_PNG"
    
    success "ICNS created"
    echo ""
    
    # Step 4: Clean old registrations
    echo -e "${BOLD}[4/7]${NC} Cleaning old registrations..."
    OLD_LOCATIONS=(
        "$HOME/Library/FoobarIconHandler.app"
        "/Applications/FoobarIconHandler.app"
        "$HOME/Applications/FoobarIconHandler.app"
    )
    
    for loc in "${OLD_LOCATIONS[@]}"; do
        if [ -d "$loc" ]; then
            /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -u "$loc" 2>/dev/null || true
            rm -rf "$loc" 2>/dev/null || sudo rm -rf "$loc" 2>/dev/null || true
        fi
    done
    success "Cleaned up"
    echo ""
    
    # Step 5: Create app bundle
    echo -e "${BOLD}[5/7]${NC} Creating application bundle..."
    BUNDLE_DIR="/Applications/FoobarIconHandler.app"
    CONTENTS_DIR="$BUNDLE_DIR/Contents"
    RESOURCES_DIR="$CONTENTS_DIR/Resources"
    MACOS_DIR="$CONTENTS_DIR/MacOS"
    
    # Check if we need sudo
    NEEDS_SUDO=0
    if [ ! -w "/Applications" ]; then
        NEEDS_SUDO=1
        warning "Need admin access for /Applications"
    fi
    
    # Create directories
    if [ $NEEDS_SUDO -eq 1 ]; then
        sudo mkdir -p "$RESOURCES_DIR" "$MACOS_DIR" || error_exit "Failed to create bundle (permission denied)"
    else
        mkdir -p "$RESOURCES_DIR" "$MACOS_DIR" || error_exit "Failed to create bundle"
    fi
    
    # Copy icon
    if [ $NEEDS_SUDO -eq 1 ]; then
        sudo cp "$ICNS_FILE" "$RESOURCES_DIR/foobar.icns"
    else
        cp "$ICNS_FILE" "$RESOURCES_DIR/foobar.icns"
    fi
    
    # Create Info.plist
    cat > "/tmp/foobar_info_$$.plist" << 'PLIST_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleIdentifier</key>
    <string>com.foobar.iconhandler</string>
    <key>CFBundleName</key>
    <string>FOOBAR</string>
    <key>CFBundleDisplayName</key>
    <string>FOOBAR Icon Handler</string>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIconFile</key>
    <string>foobar.icns</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.10</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeExtensions</key>
            <array>
                <string>foob</string>
                <string>FOOB</string>
            </array>
            <key>CFBundleTypeIconFile</key>
            <string>foobar.icns</string>
            <key>CFBundleTypeName</key>
            <string>FOOBAR Source File</string>
            <key>CFBundleTypeRole</key>
            <string>Editor</string>
            <key>LSHandlerRank</key>
            <string>Owner</string>
            <key>LSItemContentTypes</key>
            <array>
                <string>com.foobar.source</string>
            </array>
        </dict>
    </array>
    <key>UTExportedTypeDeclarations</key>
    <array>
        <dict>
            <key>UTTypeIdentifier</key>
            <string>com.foobar.source</string>
            <key>UTTypeDescription</key>
            <string>FOOBAR Source File</string>
            <key>UTTypeIconFile</key>
            <string>foobar.icns</string>
            <key>UTTypeConformsTo</key>
            <array>
                <string>public.data</string>
                <string>public.content</string>
                <string>public.source-code</string>
                <string>public.plain-text</string>
                <string>public.text</string>
            </array>
            <key>UTTypeTagSpecification</key>
            <dict>
                <key>public.filename-extension</key>
                <array>
                    <string>foob</string>
                    <string>FOOB</string>
                </array>
                <key>public.mime-type</key>
                <array>
                    <string>text/x-foobar</string>
                    <string>text/plain</string>
                </array>
            </dict>
        </dict>
    </array>
</dict>
</plist>
PLIST_EOF
    
    # Create launcher
    cat > "/tmp/foobar_launcher_$$" << 'LAUNCHER_EOF'
#!/bin/bash
# Open .foob files - prefer VSCode if available
if [ $# -eq 0 ]; then
    exit 0
fi

# Try VSCode first (most common for code files)
if command -v code >/dev/null 2>&1; then
    code "$@"
# VSCodium
elif command -v codium >/dev/null 2>&1; then
    codium "$@"
# Sublime Text
elif [ -d "/Applications/Sublime Text.app" ]; then
    open -a "Sublime Text" "$@"
# Atom
elif [ -d "/Applications/Atom.app" ]; then
    open -a "Atom" "$@"
# Default text editor
else
    open -t "$@"
fi
LAUNCHER_EOF
    
    chmod +x "/tmp/foobar_launcher_$$"
    
    # Install files
    if [ $NEEDS_SUDO -eq 1 ]; then
        sudo mv "/tmp/foobar_info_$$.plist" "$CONTENTS_DIR/Info.plist"
        sudo mv "/tmp/foobar_launcher_$$" "$MACOS_DIR/launcher"
        sudo chmod +x "$MACOS_DIR/launcher"
    else
        mv "/tmp/foobar_info_$$.plist" "$CONTENTS_DIR/Info.plist"
        mv "/tmp/foobar_launcher_$$" "$MACOS_DIR/launcher"
        chmod +x "$MACOS_DIR/launcher"
    fi
    
    success "Bundle created"
    echo ""
    
    # Step 6: Register with system
    echo -e "${BOLD}[6/7]${NC} Registering with LaunchServices..."
    /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -f "$BUNDLE_DIR" 2>/dev/null
    /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user 2>/dev/null
    success "Registered"
    echo ""
    
    # Step 7: Stamp existing files and clear caches
    echo -e "${BOLD}[7/7]${NC} Applying icons to existing files..."
    
    STAMPED=0
    TOTAL=0
    
    while IFS= read -r -d '' file; do
        TOTAL=$((TOTAL + 1))
        
        # Try fileicon first
        if command -v fileicon >/dev/null 2>&1; then
            if fileicon set "$file" "$ICNS_FILE" >/dev/null 2>&1; then
                STAMPED=$((STAMPED + 1))
                continue
            fi
        fi
        
        # Fall back to DeRez/Rez
        tmpdir=$(mktemp -d)
        rsrc="$tmpdir/icon.rsrc"
        
        sips -i "$ICNS_FILE" >/dev/null 2>&1
        if DeRez -only icns "$ICNS_FILE" > "$rsrc" 2>/dev/null; then
            Rez -append "$rsrc" -o "$file" 2>/dev/null
            SetFile -a C "$file" 2>/dev/null
            STAMPED=$((STAMPED + 1))
        fi
        
        rm -rf "$tmpdir"
    done < <(find "$SCRIPT_DIR" -name "*.foob" -o -name "*.FOOB" -type f -print0 2>/dev/null)
    
    if [ $TOTAL -gt 0 ]; then
        success "Stamped $STAMPED/$TOTAL existing files"
    else
        info "No existing .foob files found"
    fi
    echo ""
    
    # Clear all caches
    info "Clearing icon caches..."
    rm -rf ~/Library/Caches/com.apple.iconservices.store 2>/dev/null || true
    sudo rm -rf /Library/Caches/com.apple.iconservices.store 2>/dev/null || true
    sudo find /private/var/folders/ -name "com.apple.dock.iconcache" -delete 2>/dev/null || true
    sudo find /private/var/folders/ -name "com.apple.iconservices*" -delete 2>/dev/null || true
    
    # Touch files
    find "$SCRIPT_DIR" -name "*.foob" -type f -exec touch {} \; 2>/dev/null || true
    
    # Restart Finder and Dock
    killall Finder 2>/dev/null || true
    killall Dock 2>/dev/null || true
    
    success "Caches cleared and Finder restarted"
    echo ""
    
    # Step 8: Set VSCode as preferred app if available
    echo -e "${BOLD}[BONUS]${NC} Setting VSCode as default editor (if available)..."
    
    if command -v code >/dev/null 2>&1; then
        # Try duti first (most reliable)
        if command -v duti >/dev/null 2>&1; then
            duti -s com.microsoft.VSCode .foob all 2>/dev/null && success "VSCode set as default (via duti)"
        else
            # Try to find VSCode bundle ID
            VSCODE_ID=$(osascript -e 'id of app "Visual Studio Code"' 2>/dev/null || echo "")
            
            if [ -n "$VSCODE_ID" ]; then
                # Write to LaunchServices preferences
                defaults write ~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure LSHandlers -array-add \
                    "{LSHandlerContentType=\"com.foobar.source\";LSHandlerRoleAll=\"$VSCODE_ID\";}" 2>/dev/null || true
                
                /System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister -kill -r -domain local -domain system -domain user 2>/dev/null
                
                success "VSCode preference set"
            else
                info "VSCode found but couldn't set as default automatically"
            fi
        fi
    else
        info "VSCode not found - files will open with default text editor"
        info "To use VSCode: Right-click .foob → Get Info → Open with: VSCode → Change All"
    fi
    echo ""
    
    # Final message
    echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${GREEN}✅ macOS Setup Complete!${NC}"
    echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BOLD}What to expect:${NC}"
    echo ""
    echo -e "  ${GREEN}✓${NC} List View: Should show Dewey immediately"
    echo -e "  ${GREEN}✓${NC} Icon View: Should show Dewey immediately"
    echo -e "  ${GREEN}✓${NC} New Files: Will automatically get icon"
    echo ""
    echo -e "${BOLD}If icons don't appear:${NC}"
    echo ""
    echo -e "  1. Close and reopen Finder windows"
    echo -e "  2. ${YELLOW}Log out and log back in${NC} (most reliable)"
    echo -e "  3. Run this script again"
    echo ""
    if ! command -v fileicon >/dev/null 2>&1; then
        echo -e "${BOLD}💡 Pro tip:${NC} Install fileicon for best results:"
        echo -e "   ${CYAN}brew install fileicon${NC}"
        echo ""
    fi
}

#############################################################################
# Linux Setup
#############################################################################
setup_linux() {
    echo -e "${BOLD}${GREEN}🐧 Linux Setup${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Directories
    ICON_DIR="$HOME/.local/share/icons/hicolor"
    MIME_DIR="$HOME/.local/share/mime"
    APP_DIR="$HOME/.local/share/applications"
    
    mkdir -p "$ICON_DIR/256x256/mimetypes"
    mkdir -p "$ICON_DIR/scalable/mimetypes"
    mkdir -p "$ICON_DIR/48x48/mimetypes"
    mkdir -p "$MIME_DIR/packages"
    mkdir -p "$APP_DIR"
    
    # Step 1: Install icon
    echo -e "${BOLD}[1/4]${NC} Installing icon..."
    
    # Try to use ImageMagick for better quality
    if command -v convert >/dev/null 2>&1; then
        convert "$ICON_FILE" -resize 256x256 "$ICON_DIR/256x256/mimetypes/text-x-foobar.png" 2>/dev/null
        convert "$ICON_FILE" -resize 48x48 "$ICON_DIR/48x48/mimetypes/text-x-foobar.png" 2>/dev/null
        success "Icon converted and installed"
    else
        cp "$ICON_FILE" "$ICON_DIR/256x256/mimetypes/text-x-foobar.png"
        warning "ImageMagick not found, icon may not scale well"
        info "Install with: sudo apt install imagemagick"
    fi
    echo ""
    
    # Step 2: Register MIME type
    echo -e "${BOLD}[2/4]${NC} Registering MIME type..."
    cat > "$MIME_DIR/packages/foobar.xml" << 'MIME_EOF'
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
    <mime-type type="text/x-foobar">
        <comment>FOOBAR Source File</comment>
        <comment xml:lang="en">FOOBAR Source File</comment>
        <icon name="text-x-foobar"/>
        <glob pattern="*.foob"/>
        <glob pattern="*.FOOB"/>
        <sub-class-type type="text/plain"/>
    </mime-type>
</mime-info>
MIME_EOF
    success "MIME type registered"
    echo ""
    
    # Step 3: Create desktop entry
    echo -e "${BOLD}[3/4]${NC} Creating desktop entry..."
    cat > "$APP_DIR/foobar.desktop" << DESKTOP_EOF
[Desktop Entry]
Type=Application
Name=FOOBAR
Comment=Open FOOBAR source files
Icon=text-x-foobar
Exec=xdg-open %f
MimeType=text/x-foobar;
NoDisplay=true
Categories=Development;TextEditor;
DESKTOP_EOF
    success "Desktop entry created"
    echo ""
    
    # Step 4: Update databases
    echo -e "${BOLD}[4/4]${NC} Updating system databases..."
    
    if update-mime-database "$MIME_DIR" 2>/dev/null; then
        success "MIME database updated"
    else
        warning "Could not update MIME database"
    fi
    
    if gtk-update-icon-cache "$HOME/.local/share/icons/hicolor" 2>/dev/null; then
        success "Icon cache updated"
    else
        warning "Could not update icon cache"
    fi
    
    if update-desktop-database "$APP_DIR" 2>/dev/null; then
        success "Desktop database updated"
    else
        warning "Could not update desktop database"
    fi
    
    # Set as default handler
    if command -v xdg-mime >/dev/null 2>&1; then
        xdg-mime default foobar.desktop text/x-foobar 2>/dev/null || true
    fi
    echo ""
    
    # Final message
    echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${GREEN}✅ Linux Setup Complete!${NC}"
    echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BOLD}Next steps:${NC}"
    echo ""
    echo -e "  1. Restart your file manager:"
    echo -e "     ${CYAN}killall nautilus && nautilus &${NC}  (GNOME)"
    echo -e "     ${CYAN}killall dolphin && dolphin &${NC}   (KDE)"
    echo -e "     ${CYAN}killall thunar && thunar &${NC}     (XFCE)"
    echo ""
    echo -e "  2. Or just log out and log back in"
    echo ""
}

#############################################################################
# Windows Setup
#############################################################################
setup_windows() {
    echo -e "${BOLD}${GREEN}🪟 Windows Setup${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    ICO_FILE="$SCRIPT_DIR/foobar.ico"
    
    # Step 1: Convert to ICO
    echo -e "${BOLD}[1/3]${NC} Creating .ico file..."
    
    if command -v magick >/dev/null 2>&1; then
        if magick "$ICON_FILE" -define icon:auto-resize=256,128,96,64,48,32,16 "$ICO_FILE" 2>/dev/null; then
            success "ICO file created with ImageMagick"
        else
            error_exit "Failed to convert icon"
        fi
    elif command -v convert >/dev/null 2>&1; then
        if convert "$ICON_FILE" -define icon:auto-resize=256,128,96,64,48,32,16 "$ICO_FILE" 2>/dev/null; then
            success "ICO file created with ImageMagick"
        else
            error_exit "Failed to convert icon"
        fi
    else
        error_exit "ImageMagick not found. Install with: choco install imagemagick"
    fi
    echo ""
    
    # Step 2: Get Windows path
    echo -e "${BOLD}[2/3]${NC} Preparing registry file..."
    
    if command -v cygpath >/dev/null 2>&1; then
        ICO_PATH=$(cygpath -w "$ICO_FILE")
    else
        # Try to convert /mnt/c/ style paths (WSL)
        ICO_PATH=$(echo "$ICO_FILE" | sed 's|/mnt/\([a-z]\)/|\U\1:/|' | sed 's|/|\\|g')
    fi
    
    # Escape for registry
    ICO_PATH_ESC=$(echo "$ICO_PATH" | sed 's|\\|\\\\|g')
    
    # Create registry file
    REG_FILE="$SCRIPT_DIR/install_foobar_icon.reg"
    
    cat > "$REG_FILE" << REG_EOF
Windows Registry Editor Version 5.00

; FOOBAR file type association

[HKEY_CURRENT_USER\\Software\\Classes\\.foob]
@="FoobarSourceFile"

[HKEY_CURRENT_USER\\Software\\Classes\\.FOOB]
@="FoobarSourceFile"

[HKEY_CURRENT_USER\\Software\\Classes\\FoobarSourceFile]
@="FOOBAR Source File"
"FriendlyTypeName"="FOOBAR Source File"

[HKEY_CURRENT_USER\\Software\\Classes\\FoobarSourceFile\\DefaultIcon]
@="$ICO_PATH_ESC,0"

[HKEY_CURRENT_USER\\Software\\Classes\\FoobarSourceFile\\shell]
@="open"

[HKEY_CURRENT_USER\\Software\\Classes\\FoobarSourceFile\\shell\\open]
@="Open"

[HKEY_CURRENT_USER\\Software\\Classes\\FoobarSourceFile\\shell\\open\\command]
@="notepad.exe \\\"%1\\\""

[HKEY_CURRENT_USER\\Software\\Classes\\FoobarSourceFile\\shell\\edit]
@="Edit"

[HKEY_CURRENT_USER\\Software\\Classes\\FoobarSourceFile\\shell\\edit\\command]
@="notepad.exe \\\"%1\\\""
REG_EOF
    
    success "Registry file created"
    echo ""
    
    # Step 3: Create installer batch
    echo -e "${BOLD}[3/3]${NC} Creating installer..."
    
    BATCH_FILE="$SCRIPT_DIR/install_foobar_icon.bat"
    cat > "$BATCH_FILE" << 'BAT_EOF'
@echo off
setlocal enabledelayedexpansion

echo =========================================
echo   FOOBAR Icon Installer for Windows
echo =========================================
echo.

:: Check if running as admin
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as Administrator
) else (
    echo Note: Not running as Administrator
    echo If this fails, right-click and "Run as Administrator"
)
echo.

:: Import registry file
echo Installing file type association...
reg import "%~dp0install_foobar_icon.reg"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [32mSuccess! Icon installed.[0m
    echo.
    echo Refreshing Explorer...
    taskkill /F /IM explorer.exe >nul 2>&1
    timeout /t 1 >nul
    start explorer.exe
    echo.
    echo All .foob files should now show the custom icon!
    echo.
    echo If icons don't appear:
    echo   1. Log out and log back in
    echo   2. Restart your computer
    echo   3. Delete icon cache:
    echo      del /a /q "%userprofile%\AppData\Local\IconCache.db"
) else (
    echo.
    echo [31mFailed to install.[0m
    echo.
    echo Try:
    echo   1. Right-click install_foobar_icon.bat
    echo   2. Select "Run as Administrator"
    echo   3. Click "Yes" to confirm
)

echo.
pause
BAT_EOF
    
    success "Installer created"
    echo ""
    
    # Final message
    echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${GREEN}✅ Windows Setup Complete!${NC}"
    echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${BOLD}Files created:${NC}"
    echo -e "  • ${CYAN}foobar.ico${NC}"
    echo -e "  • ${CYAN}install_foobar_icon.reg${NC}"
    echo -e "  • ${CYAN}install_foobar_icon.bat${NC}"
    echo ""
    echo -e "${BOLD}To install the icon:${NC}"
    echo ""
    echo -e "  ${YELLOW}Option 1 (Recommended):${NC}"
    echo -e "    Double-click: ${CYAN}install_foobar_icon.bat${NC}"
    echo ""
    echo -e "  ${YELLOW}Option 2 (Manual):${NC}"
    echo -e "    1. Double-click: ${CYAN}install_foobar_icon.reg${NC}"
    echo -e "    2. Click 'Yes' to confirm"
    echo -e "    3. Restart Explorer"
    echo ""
}

#############################################################################
# Main
#############################################################################

case $OS in
    macos)
        setup_macos
        ;;
    linux)
        setup_linux
        ;;
    windows)
        setup_windows
        ;;
esac

echo -e "${BOLD}${MAGENTA}╔════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${MAGENTA}║           🎉 ALL DONE! 🎉              ║${NC}"
echo -e "${BOLD}${MAGENTA}║     Dewey is now watching over your    ║${NC}"
echo -e "${BOLD}${MAGENTA}║         FOOBAR source files!           ║${NC}"
echo -e "${BOLD}${MAGENTA}╚════════════════════════════════════════╝${NC}"
echo ""

# Self-test verification
if [ "$OS" = "macos" ]; then
    echo -e "${BOLD}🔍 Quick verification:${NC}"
    echo ""
    
    # Check if ICNS was created
    if [ -f "$SCRIPT_DIR/foobar.icns" ]; then
        echo -e "  ${GREEN}✓${NC} foobar.icns created"
    else
        echo -e "  ${RED}✗${NC} foobar.icns missing!"
    fi
    
    # Check if bundle exists
    if [ -d "/Applications/FoobarIconHandler.app" ]; then
        echo -e "  ${GREEN}✓${NC} Application bundle installed"
    else
        echo -e "  ${YELLOW}⚠${NC}  Application bundle not in /Applications"
    fi
    
    # Check for .foob files
    FOOB_COUNT=$(find "$SCRIPT_DIR" -name "*.foob" -type f 2>/dev/null | wc -l | tr -d ' ')
    if [ "$FOOB_COUNT" -gt 0 ]; then
        echo -e "  ${GREEN}✓${NC} Found $FOOB_COUNT .foob file(s)"
    else
        echo -e "  ${CYAN}ℹ${NC}  No .foob files found yet"
    fi
    
    echo ""
fi
