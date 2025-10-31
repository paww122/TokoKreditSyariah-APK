# 🐧 Panduan Build APK di Linux

## 📋 Persiapan Sistem Linux

### 1. Update Sistem
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Dependencies Dasar
```bash
# Python dan tools dasar
sudo apt install -y python3 python3-pip python3-venv git

# Dependencies untuk Android development
sudo apt install -y build-essential ccache git libncurses5:i386 libstdc++6:i386 libgtk2.0-0:i386 libpangox-1.0-0:i386 libpangoxft-1.0-0:i386 libidn11:i386 python2.7 python2.7-dev openjdk-8-jdk unzip zlib1g-dev zlib1g:i386

# Dependencies untuk Kivy
sudo apt install -y libffi-dev libssl-dev libbz2-dev libreadline-dev libsqlite3-dev libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl

# Dependencies untuk buildozer
sudo apt install -y cython3 autoconf libtool pkg-config
```

### 3. Install Android SDK (Otomatis via Buildozer)
Buildozer akan mengunduh Android SDK secara otomatis, tapi Anda bisa set manual jika perlu:
```bash
# Opsional: Set ANDROID_HOME jika sudah ada SDK
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools
```

## 🚀 Setup Project

### 1. Transfer Project ke Linux
```bash
# Buat direktori project
mkdir -p ~/TokoKreditSyariah
cd ~/TokoKreditSyariah

# Copy semua file dari Windows ke Linux
# Gunakan scp, rsync, atau USB drive
```

### 2. Install Buildozer
```bash
# Install buildozer
pip3 install --user buildozer cython

# Tambahkan ke PATH
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

### 3. Install Dependencies Python
```bash
# Install requirements untuk project
pip3 install --user kivy kivymd pybluez google-api-python-client cryptography reportlab plyer pyserial python-dateutil
```

## 🔧 Build APK

### 1. Persiapan Build
```bash
cd ~/TokoKreditSyariah

# Bersihkan cache jika perlu
buildozer android clean

# Init buildozer (jika belum ada buildozer.spec)
# buildozer init
```

### 2. Build APK (Pertama Kali - Lama)
```bash
# Build pertama akan download SDK, NDK, dll (30-60 menit)
buildozer android debug

# Atau dengan verbose untuk melihat progress
buildozer android debug --verbose
```

### 3. Build APK (Selanjutnya - Cepat)
```bash
# Build selanjutnya lebih cepat (5-15 menit)
buildozer android debug
```

## ⚡ Script Otomatis untuk Linux

### build_linux.sh
```bash
#!/bin/bash
echo "🚀 Starting APK Build on Linux"
echo "================================"

# Set environment variables
export BUILDOZER_LOG_LEVEL=2
export MAKEFLAGS=-j$(nproc)

echo "📱 Building TokoKreditSyariah APK..."
echo "⏱️ First build: 30-60 minutes"
echo "⏱️ Subsequent builds: 5-15 minutes"
echo ""

# Build APK
buildozer android debug --verbose

# Check result
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ BUILD SUCCESS"
    echo "================================"
    echo "🎉 APK built successfully!"
    echo "📱 Location: bin/TokoKreditSyariah-*-debug.apk"
    echo ""
    echo "🔥 Features included:"
    echo "   ✅ Database & UI (SQLite + Kivy/KivyMD)"
    echo "   ✅ Print Bluetooth (pybluez)"
    echo "   ✅ Google Drive Backup"
    echo "   ✅ Local Backup Encrypted"
    echo "   ✅ PDF Reports (reportlab)"
    echo "   ✅ Hardware Access (plyer)"
    echo "   ✅ Serial Communication"
else
    echo ""
    echo "❌ BUILD FAILED"
    echo "================================"
    echo "🔍 Check error messages above"
    echo "💡 Try: buildozer android clean"
fi
```

## 🐛 Troubleshooting

### Masalah Umum & Solusi:

1. **Permission denied**
   ```bash
   chmod +x build_linux.sh
   ```

2. **Java version issues**
   ```bash
   sudo update-alternatives --config java
   # Pilih OpenJDK 8
   ```

3. **Memory issues**
   ```bash
   export GRADLE_OPTS="-Xmx4g"
   ```

4. **NDK/SDK download gagal**
   ```bash
   buildozer android clean
   rm -rf ~/.buildozer
   buildozer android debug
   ```

5. **Dependencies missing**
   ```bash
   sudo apt install -y python3-dev libffi-dev libssl-dev
   ```

## 📊 Estimasi Waktu Build

| Build Type | Waktu | Keterangan |
|------------|-------|------------|
| **Pertama** | 30-60 menit | Download SDK, NDK, compile semua |
| **Kedua dst** | 5-15 menit | Hanya compile perubahan |
| **Clean build** | 20-40 menit | Compile ulang tanpa download |

## 🎯 Tips Optimasi

1. **Gunakan SSD** untuk storage project
2. **RAM minimal 8GB** untuk build yang lancar
3. **Internet stabil** untuk download dependencies
4. **Multicore CPU** akan mempercepat compile

## 📱 Hasil APK

Setelah build sukses, APK akan tersedia di:
```
bin/TokoKreditSyariah-0.1-debug.apk
```

APK ini sudah include SEMUA fitur:
- ✅ Database SQLite
- ✅ UI Kivy/KivyMD  
- ✅ Bluetooth printing
- ✅ Google Drive backup
- ✅ Local encrypted backup
- ✅ PDF reports
- ✅ Hardware access
- ✅ Serial communication

## 🚀 Quick Start Commands

```bash
# Setup lengkap (run sekali)
sudo apt update && sudo apt install -y python3 python3-pip build-essential git
pip3 install --user buildozer cython
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc

# Copy project files ke Linux
# cd ke direktori project

# Build APK
chmod +x build_linux.sh
./build_linux.sh
```

**Selamat building! 🎉**