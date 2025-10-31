#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toko Kredit Syariah - Aplikasi Android untuk bisnis kredit harian
Tanpa DP, tanpa denda, tanpa bunga - sesuai syariah
"""

import os
import sys
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.clock import Clock

# Import modules
from database import DatabaseManager
from printer import get_printer
from backup import get_backup_manager

# Import screen classes
from screens import (
    TambahPelangganScreen,
    JualKreditScreen,
    CatatBayarScreen,
    TagihHariIniScreen,
    LaporanScreen
)

class WizardScreen(Screen):
    """First-time setup wizard"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'wizard'
        self.step = 1
        self.password = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Title
        title = Label(
            text='Selamat Datang di\nToko Kredit Syariah',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(100),
            halign='center'
        )
        layout.add_widget(title)
        
        # Content area
        self.content_area = BoxLayout(orientation='vertical', spacing=dp(10))
        layout.add_widget(self.content_area)
        
        # Navigation buttons
        nav_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        self.back_btn = Button(
            text='Kembali',
            size_hint_x=0.3,
            disabled=True,
            on_press=self.go_back
        )
        nav_layout.add_widget(self.back_btn)
        
        nav_layout.add_widget(Label())  # Spacer
        
        self.next_btn = Button(
            text='Lanjut',
            size_hint_x=0.3,
            background_color=(0.2, 0.8, 0.2, 1),
            on_press=self.go_next
        )
        nav_layout.add_widget(self.next_btn)
        
        layout.add_widget(nav_layout)
        self.add_widget(layout)
        
        # Show first step
        self.show_step()
    
    def show_step(self):
        self.content_area.clear_widgets()
        
        if self.step == 1:
            self.show_password_step()
        elif self.step == 2:
            self.show_backup_step()
        elif self.step == 3:
            self.show_complete_step()
    
    def show_password_step(self):
        # Step 1: Password creation
        step_label = Label(
            text='Langkah 1: Buat Kata Sandi Utama',
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40)
        )
        self.content_area.add_widget(step_label)
        
        desc_label = Label(
            text='Kata sandi ini akan melindungi data Anda',
            size_hint_y=None,
            height=dp(30)
        )
        self.content_area.add_widget(desc_label)
        
        # Password input
        self.password_input = TextInput(
            hint_text='Masukkan kata sandi',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )
        self.content_area.add_widget(self.password_input)
        
        # Confirm password
        self.confirm_input = TextInput(
            hint_text='Konfirmasi kata sandi',
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(50)
        )
        self.content_area.add_widget(self.confirm_input)
        
        self.back_btn.disabled = True
        self.next_btn.text = 'Lanjut'
    
    def show_backup_step(self):
        # Step 2: Backup selection
        step_label = Label(
            text='Langkah 2: Pilih Backup',
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40)
        )
        self.content_area.add_widget(step_label)
        
        desc_label = Label(
            text='Pilih metode backup otomatis',
            size_hint_y=None,
            height=dp(30)
        )
        self.content_area.add_widget(desc_label)
        
        # Backup options
        backup_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        self.internal_backup = Button(
            text='✓ Folder Internal (Direkomendasikan)',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.8, 0.2, 1),
            on_press=self.toggle_internal_backup
        )
        backup_layout.add_widget(self.internal_backup)
        
        self.drive_backup = Button(
            text='Google Drive (Opsional)',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.6, 0.6, 0.6, 1),
            on_press=self.toggle_drive_backup
        )
        backup_layout.add_widget(self.drive_backup)
        
        self.content_area.add_widget(backup_layout)
        
        self.back_btn.disabled = False
        self.next_btn.text = 'Lanjut'
        
        # Default selections
        self.internal_enabled = True
        self.drive_enabled = False
    
    def show_complete_step(self):
        # Step 3: Complete
        step_label = Label(
            text='Langkah 3: Siap Pakai!',
            font_size=dp(18),
            size_hint_y=None,
            height=dp(40)
        )
        self.content_area.add_widget(step_label)
        
        success_label = Label(
            text='🎉 Aplikasi berhasil dikonfigurasi!\n\nAnda dapat mulai:\n• Menambah pelanggan\n• Jual kredit\n• Catat pembayaran\n• Cetak struk',
            font_size=dp(16),
            halign='center'
        )
        self.content_area.add_widget(success_label)
        
        self.back_btn.disabled = False
        self.next_btn.text = 'Mulai'
    
    def toggle_internal_backup(self, instance):
        self.internal_enabled = not self.internal_enabled
        if self.internal_enabled:
            instance.text = '✓ Folder Internal (Direkomendasikan)'
            instance.background_color = (0.2, 0.8, 0.2, 1)
        else:
            instance.text = 'Folder Internal (Direkomendasikan)'
            instance.background_color = (0.6, 0.6, 0.6, 1)
    
    def toggle_drive_backup(self, instance):
        self.drive_enabled = not self.drive_enabled
        if self.drive_enabled:
            instance.text = '✓ Google Drive (Opsional)'
            instance.background_color = (0.2, 0.8, 0.2, 1)
        else:
            instance.text = 'Google Drive (Opsional)'
            instance.background_color = (0.6, 0.6, 0.6, 1)
    
    def go_back(self, instance):
        if self.step > 1:
            self.step -= 1
            self.show_step()
    
    def go_next(self, instance):
        if self.step == 1:
            # Validasi password
            password = self.password_input.text
            confirm = self.confirm_input.text
            
            if len(password) < 4:
                self.show_error("Kata sandi minimal 4 karakter")
                return
            
            if password != confirm:
                self.show_error("Konfirmasi kata sandi tidak cocok")
                return
            
            self.password = password
            self.step += 1
            self.show_step()
            
        elif self.step == 2:
            self.step += 1
            self.show_step()
            
        elif self.step == 3:
            # Complete setup
            self.complete_setup()
    
    def show_error(self, message):
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def complete_setup(self):
        # Initialize database
        app = App.get_running_app()
        app.initialize_app(self.password)
        
        # Switch to dashboard
        app.root.current = 'dashboard'


class DashboardScreen(Screen):
    """Main dashboard screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'dashboard'
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Header
        header = Label(
            text='Toko Kredit Syariah',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(60),
            color=(0.2, 0.6, 0.8, 1)
        )
        layout.add_widget(header)
        
        # Info cards
        info_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(120))
        
        self.piutang_card = Label(
            text='Total Piutang\nRp 0',
            font_size=dp(14),
            halign='center',
            valign='middle'
        )
        info_layout.add_widget(self.piutang_card)
        
        self.tagihan_card = Label(
            text='Tagihan Hari Ini\n0 orang',
            font_size=dp(14),
            halign='center',
            valign='middle'
        )
        info_layout.add_widget(self.tagihan_card)
        
        self.sudah_bayar_card = Label(
            text='Sudah Bayar\n0 orang',
            font_size=dp(14),
            halign='center',
            valign='middle',
            color=(0.2, 0.8, 0.2, 1)
        )
        info_layout.add_widget(self.sudah_bayar_card)
        
        self.belum_bayar_card = Label(
            text='Belum Bayar\n0 orang',
            font_size=dp(14),
            halign='center',
            valign='middle',
            color=(0.8, 0.2, 0.2, 1)
        )
        info_layout.add_widget(self.belum_bayar_card)
        
        layout.add_widget(info_layout)
        
        # Main buttons
        btn_layout = GridLayout(cols=2, spacing=dp(15), size_hint_y=None, height=dp(200))
        
        jual_btn = Button(
            text='JUAL KREDIT',
            font_size=dp(18),
            background_color=(0.2, 0.8, 0.2, 1),
            on_press=self.go_to_jual_kredit
        )
        btn_layout.add_widget(jual_btn)
        
        bayar_btn = Button(
            text='CATAT BAYAR',
            font_size=dp(18),
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.go_to_catat_bayar
        )
        btn_layout.add_widget(bayar_btn)
        
        tagih_btn = Button(
            text='TAGIH HARI INI',
            font_size=dp(18),
            background_color=(0.8, 0.6, 0.2, 1),
            on_press=self.go_to_tagih_hari_ini
        )
        btn_layout.add_widget(tagih_btn)
        
        pelanggan_btn = Button(
            text='TAMBAH PELANGGAN',
            font_size=dp(18),
            background_color=(0.6, 0.2, 0.8, 1),
            on_press=self.go_to_tambah_pelanggan
        )
        btn_layout.add_widget(pelanggan_btn)
        
        layout.add_widget(btn_layout)
        
        # Additional buttons
        extra_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        libur_btn = Button(
            text='Tandai Libur',
            background_color=(0.6, 0.6, 0.6, 1),
            on_press=self.tandai_libur
        )
        extra_layout.add_widget(libur_btn)
        
        laporan_btn = Button(
            text='Laporan',
            background_color=(0.4, 0.4, 0.4, 1),
            on_press=self.go_to_laporan
        )
        extra_layout.add_widget(laporan_btn)
        
        layout.add_widget(extra_layout)
        
        # Status bar
        self.status_label = Label(
            text='Backup: Belum pernah',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(12),
            color=(0.6, 0.6, 0.6, 1)
        )
        layout.add_widget(self.status_label)
        
        self.add_widget(layout)
        
    
    def on_enter(self):
        """Called when screen is entered"""
        self.update_dashboard_info()
        Clock.schedule_interval(self.update_dashboard_info, 30)  # Update every 30 seconds
    
    def update_dashboard_info(self, dt=None):
        """Update dashboard information"""
        app = App.get_running_app()
        if hasattr(app, 'db_manager'):
            # Get statistics
            stats = app.db_manager.get_dashboard_stats()
            
            # Update cards
            self.piutang_card.text = f"Total Piutang\n{stats['total_piutang']}"
            self.tagihan_card.text = f"Tagihan Hari Ini\n{stats['tagihan_hari_ini']} orang"
            self.sudah_bayar_card.text = f"Sudah Bayar\n{stats['sudah_bayar']} orang"
            self.belum_bayar_card.text = f"Belum Bayar\n{stats['belum_bayar']} orang"
            
            # Update backup status
            if hasattr(app, 'backup_manager'):
                backup_status = app.backup_manager.get_backup_status()
                if backup_status['last_backup']:
                    from datetime import datetime
                    last_backup = datetime.fromisoformat(backup_status['last_backup'])
                    minutes_ago = int((datetime.now() - last_backup).total_seconds() / 60)
                    self.status_label.text = f"Backup: {minutes_ago} menit lalu"
                else:
                    self.status_label.text = "Backup: Belum pernah"
    
    def go_to_jual_kredit(self, instance):
        App.get_running_app().root.current = 'jual_kredit'
    
    def go_to_catat_bayar(self, instance):
        App.get_running_app().root.current = 'catat_bayar'
    
    def go_to_tagih_hari_ini(self, instance):
        App.get_running_app().root.current = 'tagih_hari_ini'
    
    def go_to_tambah_pelanggan(self, instance):
        App.get_running_app().root.current = 'tambah_pelanggan'
    
    def go_to_laporan(self, instance):
        App.get_running_app().root.current = 'laporan'
    
    def tandai_libur(self, instance):
        """Mark today as holiday"""
        app = App.get_running_app()
        if hasattr(app, 'db_manager'):
            success = app.db_manager.mark_holiday()
            if success:
                self.show_success("Hari ini berhasil ditandai sebagai libur")
            else:
                self.show_error("Gagal menandai libur")
    
    def show_success(self, message):
        popup = Popup(
            title='Berhasil',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def show_error(self, message):
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()


class TokoKreditSyariahApp(App):
    """Main application class"""
    
    def build(self):
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(WizardScreen())
        sm.add_widget(DashboardScreen())
        sm.add_widget(TambahPelangganScreen())
        sm.add_widget(JualKreditScreen())
        sm.add_widget(CatatBayarScreen())
        sm.add_widget(TagihHariIniScreen())
        sm.add_widget(LaporanScreen())
        
        return sm
    
    def initialize_app(self, password):
        """Initialize app with password"""
        try:
            # Initialize database
            db_path = os.path.join(self.user_data_dir, 'kredit.db')
            self.db_manager = DatabaseManager(db_path, password)
            
            # Initialize printer
            self.printer = get_printer()
            
            # Initialize backup
            from backup import initialize_backup
            self.backup_manager = initialize_backup(db_path, password)
            self.backup_manager.start_auto_backup()
            
            print("App initialized successfully")
            
        except Exception as e:
            print(f"App initialization failed: {str(e)}")
    
    def on_stop(self):
        """Called when app is closing"""
        if hasattr(self, 'backup_manager'):
            # Create final backup
            self.backup_manager.create_backup()
            self.backup_manager.stop_auto_backup()
        
        if hasattr(self, 'printer'):
            self.printer.disconnect()


if __name__ == '__main__':
    TokoKreditSyariahApp().run()