#!/bin/bash
echo "🚀 Starting APK Build on Linux"
echo "================================"

# Set environment variables for optimal performance
export BUILDOZER_LOG_LEVEL=2
export MAKEFLAGS=-j$(nproc)
export GRADLE_OPTS="-Xmx4g -Dorg.gradle.parallel=true -Dorg.gradle.daemon=true"

echo "📱 Building TokoKreditSyariah APK with ALL features..."
echo "⏱️ First build: 30-60 minutes (downloads SDK, NDK)"
echo "⏱️ Subsequent builds: 5-15 minutes"
echo "🐧 Running on Linux (native buildozer support)"
echo ""

# Check if buildozer is installed
if ! command -v buildozer &> /dev/null; then
    echo "❌ Buildozer not found. Installing..."
    pip3 install --user buildozer cython
    export PATH=$PATH:~/.local/bin
fi

# Build APK with verbose output
buildozer android debug --verbose

# Check build result
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ BUILD SUCCESS"
    echo "================================"
    echo "🎉 APK built successfully with ALL features:"
    echo "   ✅ Database & UI (SQLite + Kivy/KivyMD)"
    echo "   ✅ Print Bluetooth (pybluez)"
    echo "   ✅ Google Drive Backup (google-api-python-client)"
    echo "   ✅ Local Backup Encrypted (cryptography)"
    echo "   ✅ PDF Reports (reportlab)"
    echo "   ✅ Hardware Access (plyer)"
    echo "   ✅ Serial Communication (pyserial)"
    echo ""
    echo "📱 APK Location: bin/TokoKreditSyariah-*-debug.apk"
    echo "📂 You can now install this APK on your Android device"
    echo ""
    echo "🔥 Next steps:"
    echo "   1. Copy APK to your Android device"
    echo "   2. Enable 'Unknown Sources' in Android settings"
    echo "   3. Install the APK"
    echo "   4. Enjoy your TokoKreditSyariah app!"
else
    echo ""
    echo "❌ BUILD FAILED"
    echo "================================"
    echo "🔍 Check the error messages above"
    echo "💡 Common solutions:"
    echo "   - Try: buildozer android clean"
    echo "   - Check internet connection"
    echo "   - Ensure all dependencies are installed"
    echo "   - Check available disk space (need ~5GB)"
fi