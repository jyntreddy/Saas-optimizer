#!/bin/bash

# Desktop App Installation Script
# Supports macOS, Windows (via Git Bash), and Linux

set -e

echo "🖥️  SaaS Optimizer Desktop App - Installation"
echo "=============================================="
echo ""

# Detect OS
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
fi

echo "Detected OS: $OS"
echo ""

# Check Node.js
echo "Checking prerequisites..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found!"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version must be 18 or higher (found: $(node -v))"
    exit 1
fi

echo "✅ Node.js $(node -v)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found!"
    exit 1
fi

echo "✅ npm $(npm -v)"
echo ""

# Install dependencies
echo "Installing dependencies..."
cd "$(dirname "$0")"
npm install

echo ""
echo "✅ Installation complete!"
echo ""

# Platform-specific instructions
case $OS in
    macos)
        echo "📝 macOS Setup:"
        echo "1. Grant Full Disk Access: System Preferences → Security & Privacy → Privacy → Full Disk Access"
        echo "2. Add this app to the list"
        echo "3. Run: npm run dev"
        ;;
    linux)
        echo "📝 Linux Setup:"
        echo "1. For Android SMS: sudo apt install android-tools-adb"
        echo "2. For camera: sudo usermod -a -G video $USER"
        echo "3. Run: npm run dev"
        ;;
    windows)
        echo "📝 Windows Setup:"
        echo "1. Install 'Your Phone' from Microsoft Store for SMS sync"
        echo "2. Grant camera permissions when prompted"
        echo "3. Run: npm run dev"
        ;;
esac

echo ""
echo "🚀 To start the app in development mode:"
echo "   npm run dev"
echo ""
echo "📦 To build for production:"
echo "   npm run build"
echo ""
echo "📚 Full documentation: ../DESKTOP_APP_SETUP.md"
