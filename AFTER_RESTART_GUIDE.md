# 🔄 Panduan Setelah Restart - WSL2 Setup

## 🎯 **Langkah-Langkah Setelah Restart:**

### **1. Verifikasi WSL2 Installation**
```powershell
# Buka PowerShell atau Command Prompt
wsl --list --verbose
```

### **2. Setup Ubuntu Pertama Kali**
```powershell
# Jalankan Ubuntu
wsl
```

**Saat pertama kali, Ubuntu akan meminta:**
- ✅ **Username** (contoh: `tokosyariah`)
- ✅ **Password** (buat password yang mudah diingat)
- ✅ **Confirm password**

### **3. Update Ubuntu System**
```bash
# Di dalam WSL Ubuntu
sudo apt update && sudo apt upgrade -y
```

### **4. Transfer Project Files**
```bash
# Buat direktori project
mkdir -p ~/TokoKreditSyariah
cd ~/TokoKreditSyariah

# Copy files dari Windows ke WSL2
cp -r /mnt/c/Users/creat/Documents/trae_projects/Kredit\ App/TokoKreditSyariah_APK/* .

# Verifikasi files berhasil dicopy
ls -la
```

### **5. Setup Build Environment**
```bash
# Make scripts executable
chmod +x setup_linux.sh
chmod +x build_linux.sh

# Run setup script (install semua dependencies)
./setup_linux.sh

# Reload PATH setelah setup
source ~/.bashrc
```

### **6. Build APK**
```bash
# Build APK dengan semua fitur
./build_linux.sh
```

---

## ⏱️ **Estimasi Waktu:**

| Tahap | Waktu |
|-------|-------|
| Setup Ubuntu pertama kali | 3-5 menit |
| Update system | 5-10 menit |
| Transfer files | 2-3 menit |
| Setup dependencies | 10-15 menit |
| **First APK build** | **30-60 menit** |
| **Total** | **50-93 menit** |

---

## 🚀 **Quick Commands (Copy-Paste Ready):**

### **Setup Lengkap:**
```bash
wsl
mkdir -p ~/TokoKreditSyariah && cd ~/TokoKreditSyariah
cp -r /mnt/c/Users/creat/Documents/trae_projects/Kredit\ App/TokoKreditSyariah_APK/* .
chmod +x setup_linux.sh build_linux.sh
./setup_linux.sh
source ~/.bashrc
./build_linux.sh
```

### **Jika Ada Error:**
```bash
# Check WSL status
wsl --status

# Restart WSL jika perlu
wsl --shutdown
wsl

# Check Ubuntu version
lsb_release -a

# Check available space (minimal 5GB)
df -h
```

---

## 📱 **Hasil Akhir:**

Setelah build sukses, APK akan tersedia di:
```
~/TokoKreditSyariah/bin/TokoKreditSyariah-0.1-debug.apk
```

**Copy APK ke Windows:**
```bash
# Copy APK ke Desktop Windows
cp bin/TokoKreditSyariah-0.1-debug.apk /mnt/c/Users/creat/Desktop/
```

---

## 🎊 **Selamat!**

Aplikasi **TokoKreditSyariah** siap diinstall di Android!

**Fitur Lengkap:**
- ✅ Database SQLite terenkripsi
- ✅ UI Modern Kivy/KivyMD  
- ✅ Print Bluetooth
- ✅ Google Drive backup
- ✅ PDF reports
- ✅ Multi-user support
- ✅ Sistem kredit syariah

**Silakan restart komputer sekarang! 🔄**