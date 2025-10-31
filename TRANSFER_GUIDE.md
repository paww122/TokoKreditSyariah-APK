# 🚀 Panduan Transfer ke Linux & Build APK

## 📋 Langkah-Langkah Lengkap

### 🎯 **OPSI 1: Menggunakan WSL2 (Windows Subsystem for Linux)**

#### 1. Install WSL2 (Jika Belum Ada)
```powershell
# Jalankan di PowerShell sebagai Administrator
wsl --install
# Restart komputer setelah selesai
```

#### 2. Setup Ubuntu di WSL2
```bash
# Buka WSL2 Ubuntu
wsl

# Update sistem
sudo apt update && sudo apt upgrade -y
```

#### 3. Transfer File ke WSL2
```bash
# Di WSL2, buat direktori
mkdir -p ~/TokoKreditSyariah
cd ~/TokoKreditSyariah

# Copy dari Windows ke WSL2
cp -r /mnt/c/Users/creat/Documents/trae_projects/Kredit\ App/TokoKreditSyariah_APK/* .

# Atau gunakan explorer Windows:
# Buka \\wsl$\Ubuntu\home\[username]\TokoKreditSyariah
# Copy paste folder TokoKreditSyariah_APK
```

#### 4. Setup Environment
```bash
# Make scripts executable
chmod +x setup_linux.sh
chmod +x build_linux.sh

# Run setup (sekali saja)
./setup_linux.sh

# Restart terminal atau reload PATH
source ~/.bashrc
```

#### 5. Build APK
```bash
# Build APK dengan semua fitur
./build_linux.sh
```

---

### 🎯 **OPSI 2: Menggunakan Linux VM atau Dual Boot**

#### 1. Transfer File
```bash
# Gunakan USB drive, scp, atau shared folder
# Copy folder TokoKreditSyariah_APK ke Linux

# Contoh dengan USB:
sudo mkdir /mnt/usb
sudo mount /dev/sdb1 /mnt/usb
cp -r /mnt/usb/TokoKreditSyariah_APK ~/
cd ~/TokoKreditSyariah_APK
```

#### 2. Setup & Build
```bash
chmod +x setup_linux.sh build_linux.sh
./setup_linux.sh
source ~/.bashrc
./build_linux.sh
```

---

### 🎯 **OPSI 3: Menggunakan GitHub (Recommended untuk Kolaborasi)**

#### 1. Upload ke GitHub
```bash
# Di Windows, buat repo GitHub baru
# Upload folder TokoKreditSyariah_APK
```

#### 2. Clone di Linux
```bash
# Di Linux
git clone https://github.com/[username]/TokoKreditSyariah.git
cd TokoKreditSyariah
chmod +x setup_linux.sh build_linux.sh
./setup_linux.sh
source ~/.bashrc
./build_linux.sh
```

---

## ⏱️ **Estimasi Waktu Total**

| Tahap | WSL2 | Linux VM | GitHub |
|-------|------|----------|--------|
| **Setup Environment** | 10-15 menit | 10-15 menit | 5-10 menit |
| **Transfer Files** | 2-5 menit | 5-10 menit | 3-5 menit |
| **First Build** | 30-60 menit | 30-60 menit | 30-60 menit |
| **Total** | **45-80 menit** | **45-85 menit** | **40-75 menit** |

---

## 🔧 **Troubleshooting Umum**

### ❌ **"Permission denied"**
```bash
chmod +x setup_linux.sh build_linux.sh
```

### ❌ **"buildozer: command not found"**
```bash
source ~/.bashrc
# atau
export PATH=$PATH:~/.local/bin
```

### ❌ **"Java not found"**
```bash
sudo apt install openjdk-8-jdk
sudo update-alternatives --config java
```

### ❌ **"No space left on device"**
```bash
# Butuh minimal 5GB free space
df -h
# Bersihkan space jika perlu
```

### ❌ **"Internet connection required"**
```bash
# First build butuh internet untuk download:
# - Android SDK (~1GB)
# - Android NDK (~1GB)  
# - Python packages (~500MB)
```

---

## 📱 **Hasil Akhir**

Setelah build sukses, APK akan tersedia di:
```
bin/TokoKreditSyariah-0.1-debug.apk
```

**Fitur Lengkap yang Termasuk:**
- ✅ Database SQLite dengan enkripsi
- ✅ UI Modern dengan Kivy/KivyMD
- ✅ Print Bluetooth untuk struk
- ✅ Google Drive backup otomatis
- ✅ Local backup terenkripsi
- ✅ Generate PDF reports
- ✅ Hardware access (camera, GPS, dll)
- ✅ Serial communication
- ✅ Multi-user support
- ✅ Sistem kredit syariah lengkap

---

## 🚀 **Quick Start Commands**

### Untuk WSL2:
```bash
wsl
mkdir -p ~/TokoKreditSyariah && cd ~/TokoKreditSyariah
cp -r /mnt/c/Users/creat/Documents/trae_projects/Kredit\ App/TokoKreditSyariah_APK/* .
chmod +x setup_linux.sh build_linux.sh
./setup_linux.sh
source ~/.bashrc
./build_linux.sh
```

### Untuk Linux Native:
```bash
cd ~/TokoKreditSyariah_APK
chmod +x setup_linux.sh build_linux.sh
./setup_linux.sh
source ~/.bashrc
./build_linux.sh
```

---

## 🎉 **Setelah Build Selesai**

1. **Copy APK ke Android:**
   ```bash
   # APK location: bin/TokoKreditSyariah-0.1-debug.apk
   # Copy via USB, email, atau cloud storage
   ```

2. **Install di Android:**
   - Enable "Unknown Sources" di Settings
   - Install APK
   - Buka aplikasi TokoKreditSyariah

3. **Setup Awal:**
   - Buat password master
   - Setup backup Google Drive (opsional)
   - Mulai input data toko

**Selamat! Aplikasi TokoKreditSyariah siap digunakan! 🎊**