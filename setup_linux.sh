#!/bin/bash
echo "🐧 Setting up Linux environment for TokoKreditSyariah APK build"
echo "================================================================"

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install basic dependencies
echo "🔧 Installing basic dependencies..."
sudo apt install -y python3 python3-pip python3-venv git curl wget

# Install build tools
echo "🛠️ Installing build tools..."
sudo apt install -y build-essential ccache autoconf libtool pkg-config

# Install Java 8 (required for Android builds)
echo "☕ Installing Java 8..."
sudo apt install -y openjdk-8-jdk

# Install 32-bit libraries (required for Android SDK)
echo "📚 Installing 32-bit libraries..."
sudo apt install -y libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 \
    libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 \
    zlib1g-dev zlib1g:i386

# Install Python development libraries
echo "🐍 Installing Python development libraries..."
sudo apt install -y python3-dev libffi-dev libssl-dev libbz2-dev \
    libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev liblzma-dev

# Install Cython
echo "⚙️ Installing Cython..."
sudo apt install -y cython3

# Install buildozer and Python dependencies
echo "🚀 Installing buildozer and Python dependencies..."
pip3 install --user buildozer cython

# Install project-specific Python packages
echo "📱 Installing project dependencies..."
pip3 install --user kivy kivymd pybluez google-api-python-client \
    cryptography reportlab plyer pyserial

# Add local bin to PATH
echo "🛤️ Adding ~/.local/bin to PATH..."
if ! grep -q 'export PATH=$PATH:~/.local/bin' ~/.bashrc; then
    echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
fi

# Set Java 8 as default
echo "☕ Setting Java 8 as default..."
sudo update-alternatives --install /usr/bin/java java /usr/lib/jvm/java-8-openjdk-amd64/bin/java 1
sudo update-alternatives --install /usr/bin/javac javac /usr/lib/jvm/java-8-openjdk-amd64/bin/javac 1

# Create Android directory
echo "📁 Creating Android directory..."
mkdir -p ~/Android

# Make build script executable
echo "🔐 Making build script executable..."
chmod +x build_linux.sh

echo ""
echo "✅ SETUP COMPLETE"
echo "================="
echo "🎉 Linux environment is ready for APK building!"
echo ""
echo "📋 What was installed:"
echo "   ✅ Python 3 + pip + development libraries"
echo "   ✅ Build tools (gcc, make, autoconf, etc.)"
echo "   ✅ Java 8 (required for Android)"
echo "   ✅ 32-bit libraries (Android SDK compatibility)"
echo "   ✅ Buildozer + Cython"
echo "   ✅ All project dependencies"
echo ""
echo "🚀 Next steps:"
echo "   1. Restart terminal or run: source ~/.bashrc"
echo "   2. Copy your project files to this Linux system"
echo "   3. Run: ./build_linux.sh"
echo ""
echo "💡 Tips:"
echo "   - First build will take 30-60 minutes (downloads SDK/NDK)"
echo "   - Subsequent builds will be much faster (5-15 minutes)"
echo "   - Make sure you have at least 5GB free disk space"
echo "   - Stable internet connection is required for first build"
echo ""
echo "🔄 Please restart your terminal or run 'source ~/.bashrc' to update PATH"