#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Screen classes untuk fitur-fitur utama Toko Kredit Syariah
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock

from models import Customer, Credit, Payment, DailyCollection, Receipt, format_currency
from datetime import datetime, date

class TambahPelangganScreen(Screen):
    """Screen untuk menambah pelanggan baru"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'tambah_pelanggan'
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Header
        header_layout = BoxLayout(size_hint_y=None, height=dp(50))
        
        back_btn = Button(
            text='← Kembali',
            size_hint_x=0.3,
            on_press=self.go_back
        )
        header_layout.add_widget(back_btn)
        
        title = Label(
            text='Tambah Pelanggan',
            font_size=dp(20),
            color=(0.2, 0.6, 0.8, 1)
        )
        header_layout.add_widget(title)
        
        header_layout.add_widget(Label(size_hint_x=0.3))  # Spacer
        layout.add_widget(header_layout)
        
        # Form
        form_layout = BoxLayout(orientation='vertical', spacing=dp(15))
        
        # Nama
        form_layout.add_widget(Label(text='Nama Lengkap:', size_hint_y=None, height=dp(30), halign='left'))
        self.nama_input = TextInput(
            hint_text='Masukkan nama lengkap',
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        form_layout.add_widget(self.nama_input)
        
        # Alamat
        form_layout.add_widget(Label(text='Alamat:', size_hint_y=None, height=dp(30), halign='left'))
        self.alamat_input = TextInput(
            hint_text='Masukkan alamat lengkap',
            multiline=True,
            size_hint_y=None,
            height=dp(80),
            font_size=dp(16)
        )
        form_layout.add_widget(self.alamat_input)
        
        # No HP
        form_layout.add_widget(Label(text='No. HP:', size_hint_y=None, height=dp(30), halign='left'))
        self.hp_input = TextInput(
            hint_text='08xxxxxxxxxx',
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        form_layout.add_widget(self.hp_input)
        
        # Batas Kredit
        form_layout.add_widget(Label(text='Batas Kredit (Opsional):', size_hint_y=None, height=dp(30), halign='left'))
        self.batas_input = TextInput(
            hint_text='0',
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        form_layout.add_widget(self.batas_input)
        
        layout.add_widget(form_layout)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        clear_btn = Button(
            text='Bersihkan',
            size_hint_x=0.3,
            background_color=(0.6, 0.6, 0.6, 1),
            on_press=self.clear_form
        )
        btn_layout.add_widget(clear_btn)
        
        btn_layout.add_widget(Label())  # Spacer
        
        save_btn = Button(
            text='Simpan',
            size_hint_x=0.3,
            background_color=(0.2, 0.8, 0.2, 1),
            on_press=self.save_customer
        )
        btn_layout.add_widget(save_btn)
        
        layout.add_widget(btn_layout)
        self.add_widget(layout)
    
    def clear_form(self, instance):
        self.nama_input.text = ''
        self.alamat_input.text = ''
        self.hp_input.text = ''
        self.batas_input.text = ''
    
    def save_customer(self, instance):
        nama = self.nama_input.text.strip()
        alamat = self.alamat_input.text.strip()
        hp = self.hp_input.text.strip()
        batas = self.batas_input.text.strip()
        
        if not nama:
            self.show_error("Nama harus diisi")
            return
        
        try:
            batas_kredit = float(batas) if batas else 0
        except ValueError:
            self.show_error("Batas kredit harus berupa angka")
            return
        
        # Save to database
        app = App.get_running_app()
        if hasattr(app, 'db_manager'):
            customer_id = app.db_manager.add_customer(nama, alamat, hp, batas_kredit)
            
            if customer_id:
                self.show_success(f"Pelanggan {nama} berhasil ditambahkan")
                self.clear_form(None)
            else:
                self.show_error("Gagal menyimpan pelanggan")
    
    def show_error(self, message):
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def show_success(self, message):
        popup = Popup(
            title='Berhasil',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def go_back(self, instance):
        App.get_running_app().root.current = 'dashboard'


class JualKreditScreen(Screen):
    """Screen untuk jual kredit"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'jual_kredit'
        self.selected_customer = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Header
        header_layout = BoxLayout(size_hint_y=None, height=dp(50))
        
        back_btn = Button(
            text='← Kembali',
            size_hint_x=0.3,
            on_press=self.go_back
        )
        header_layout.add_widget(back_btn)
        
        title = Label(
            text='Jual Kredit',
            font_size=dp(20),
            color=(0.2, 0.6, 0.8, 1)
        )
        header_layout.add_widget(title)
        
        header_layout.add_widget(Label(size_hint_x=0.3))  # Spacer
        layout.add_widget(header_layout)
        
        # Customer selection
        layout.add_widget(Label(text='Pilih Pelanggan:', size_hint_y=None, height=dp(30), halign='left'))
        
        customer_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.customer_spinner = Spinner(
            text='Pilih pelanggan...',
            values=[],
            size_hint_x=0.7
        )
        customer_layout.add_widget(self.customer_spinner)
        
        add_customer_btn = Button(
            text='+ Baru',
            size_hint_x=0.3,
            background_color=(0.2, 0.8, 0.2, 1),
            on_press=self.add_new_customer
        )
        customer_layout.add_widget(add_customer_btn)
        
        layout.add_widget(customer_layout)
        
        # Item form
        form_layout = BoxLayout(orientation='vertical', spacing=dp(15))
        
        # Nama barang
        form_layout.add_widget(Label(text='Nama Barang:', size_hint_y=None, height=dp(30), halign='left'))
        self.barang_input = TextInput(
            hint_text='Contoh: TV LED 32"',
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        form_layout.add_widget(self.barang_input)
        
        # Harga
        form_layout.add_widget(Label(text='Harga Total:', size_hint_y=None, height=dp(30), halign='left'))
        self.harga_input = TextInput(
            hint_text='4000000',
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        form_layout.add_widget(self.harga_input)
        
        # Jumlah hari
        form_layout.add_widget(Label(text='Jumlah Hari:', size_hint_y=None, height=dp(30), halign='left'))
        self.hari_input = TextInput(
            hint_text='20',
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(16)
        )
        form_layout.add_widget(self.hari_input)
        
        # Cicilan per hari (auto calculate)
        form_layout.add_widget(Label(text='Cicilan Per Hari:', size_hint_y=None, height=dp(30), halign='left'))
        self.cicilan_label = Label(
            text='Rp 0',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            color=(0.2, 0.8, 0.2, 1),
            halign='left'
        )
        form_layout.add_widget(self.cicilan_label)
        
        layout.add_widget(form_layout)
        
        # Bind events for auto calculation
        self.harga_input.bind(text=self.calculate_daily)
        self.hari_input.bind(text=self.calculate_daily)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        calculate_btn = Button(
            text='Hitung Ulang',
            size_hint_x=0.3,
            background_color=(0.6, 0.6, 0.6, 1),
            on_press=self.calculate_daily
        )
        btn_layout.add_widget(calculate_btn)
        
        btn_layout.add_widget(Label())  # Spacer
        
        save_btn = Button(
            text='Simpan & Cetak',
            size_hint_x=0.4,
            background_color=(0.2, 0.8, 0.2, 1),
            on_press=self.save_credit
        )
        btn_layout.add_widget(save_btn)
        
        layout.add_widget(btn_layout)
        self.add_widget(layout)
    
    def on_enter(self):
        """Called when screen is entered"""
        self.load_customers()
    
    def load_customers(self):
        """Load customer list"""
        app = App.get_running_app()
        if hasattr(app, 'db_manager'):
            customers = app.db_manager.get_customers()
            customer_names = [f"{c['name']} - {c['phone']}" for c in customers]
            self.customer_spinner.values = customer_names
            self.customers_data = customers
    
    def add_new_customer(self, instance):
        App.get_running_app().root.current = 'tambah_pelanggan'
    
    def calculate_daily(self, instance=None):
        """Calculate daily payment amount"""
        try:
            harga = float(self.harga_input.text) if self.harga_input.text else 0
            hari = int(self.hari_input.text) if self.hari_input.text else 0
            
            if harga > 0 and hari > 0:
                # Ceiling division
                cicilan = int((harga + hari - 1) // hari)
                self.cicilan_label.text = format_currency(cicilan)
            else:
                self.cicilan_label.text = 'Rp 0'
        except ValueError:
            self.cicilan_label.text = 'Rp 0'
    
    def save_credit(self, instance):
        # Validate customer selection
        if not self.customer_spinner.text or self.customer_spinner.text == 'Pilih pelanggan...':
            self.show_error("Pilih pelanggan terlebih dahulu")
            return
        
        # Get selected customer
        selected_index = self.customer_spinner.values.index(self.customer_spinner.text)
        customer = self.customers_data[selected_index]
        
        # Validate form
        barang = self.barang_input.text.strip()
        harga_text = self.harga_input.text.strip()
        hari_text = self.hari_input.text.strip()
        
        if not barang:
            self.show_error("Nama barang harus diisi")
            return
        
        try:
            harga = float(harga_text)
            hari = int(hari_text)
            
            if harga <= 0:
                self.show_error("Harga harus lebih dari 0")
                return
            
            if hari <= 0:
                self.show_error("Jumlah hari harus lebih dari 0")
                return
                
        except ValueError:
            self.show_error("Harga dan jumlah hari harus berupa angka")
            return
        
        # Save to database
        app = App.get_running_app()
        if hasattr(app, 'db_manager'):
            credit_id = app.db_manager.add_credit(customer['id'], barang, harga, hari)
            
            if credit_id:
                # Create receipt
                cicilan = int((harga + hari - 1) // hari)
                receipt = Receipt(
                    customer_name=customer['name'],
                    item_name=barang,
                    total_price=harga,
                    total_days=hari,
                    daily_amount=cicilan,
                    days_paid=0,
                    remaining_days=hari,
                    payment_amount=0,
                    status="BARU",
                    date=date.today()
                )
                
                # Print receipt
                self.print_receipt(receipt)
                
                # Clear form
                self.clear_form()
                
                self.show_success(f"Kredit untuk {customer['name']} berhasil disimpan")
            else:
                self.show_error("Gagal menyimpan kredit")
    
    def print_receipt(self, receipt):
        """Print receipt via Bluetooth"""
        app = App.get_running_app()
        if hasattr(app, 'printer'):
            try:
                app.printer.print_receipt(receipt)
            except Exception as e:
                self.show_error(f"Gagal mencetak struk: {str(e)}")
    
    def clear_form(self):
        self.barang_input.text = ''
        self.harga_input.text = ''
        self.hari_input.text = ''
        self.cicilan_label.text = 'Rp 0'
        self.customer_spinner.text = 'Pilih pelanggan...'
    
    def show_error(self, message):
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def show_success(self, message):
        popup = Popup(
            title='Berhasil',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def go_back(self, instance):
        App.get_running_app().root.current = 'dashboard'


class CatatBayarScreen(Screen):
    """Screen untuk catat pembayaran"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'catat_bayar'
        self.selected_credit = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Header
        header_layout = BoxLayout(size_hint_y=None, height=dp(50))
        
        back_btn = Button(
            text='← Kembali',
            size_hint_x=0.3,
            on_press=self.go_back
        )
        header_layout.add_widget(back_btn)
        
        title = Label(
            text='Catat Pembayaran',
            font_size=dp(20),
            color=(0.2, 0.6, 0.8, 1)
        )
        header_layout.add_widget(title)
        
        header_layout.add_widget(Label(size_hint_x=0.3))  # Spacer
        layout.add_widget(header_layout)
        
        # Credit selection
        layout.add_widget(Label(text='Pilih Kredit:', size_hint_y=None, height=dp(30), halign='left'))
        
        self.credit_spinner = Spinner(
            text='Pilih kredit yang akan dibayar...',
            values=[],
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(self.credit_spinner)
        
        # Credit info
        self.credit_info = Label(
            text='Pilih kredit untuk melihat detail',
            size_hint_y=None,
            height=dp(80),
            text_size=(dp(300), None),
            halign='left',
            valign='top'
        )
        layout.add_widget(self.credit_info)
        
        # Payment amount
        layout.add_widget(Label(text='Jumlah Bayar:', size_hint_y=None, height=dp(30), halign='left'))
        
        amount_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.amount_input = TextInput(
            hint_text='200000',
            multiline=False,
            input_filter='int',
            size_hint_x=0.7,
            font_size=dp(16)
        )
        amount_layout.add_widget(self.amount_input)
        
        # Quick amount buttons
        quick_layout = BoxLayout(orientation='vertical', size_hint_x=0.3, spacing=dp(5))
        
        exact_btn = Button(
            text='Pas',
            size_hint_y=0.5,
            font_size=dp(12),
            on_press=self.set_exact_amount
        )
        quick_layout.add_widget(exact_btn)
        
        half_btn = Button(
            text='1/2',
            size_hint_y=0.5,
            font_size=dp(12),
            on_press=self.set_half_amount
        )
        quick_layout.add_widget(half_btn)
        
        amount_layout.add_widget(quick_layout)
        layout.add_widget(amount_layout)
        
        # Payment preview
        self.payment_preview = Label(
            text='',
            size_hint_y=None,
            height=dp(60),
            text_size=(dp(300), None),
            halign='left',
            valign='top',
            color=(0.2, 0.8, 0.2, 1)
        )
        layout.add_widget(self.payment_preview)
        
        # Buttons
        btn_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(10))
        
        preview_btn = Button(
            text='Preview',
            size_hint_x=0.3,
            background_color=(0.6, 0.6, 0.6, 1),
            on_press=self.preview_payment
        )
        btn_layout.add_widget(preview_btn)
        
        btn_layout.add_widget(Label())  # Spacer
        
        save_btn = Button(
            text='Simpan & Cetak',
            size_hint_x=0.4,
            background_color=(0.2, 0.8, 0.2, 1),
            on_press=self.save_payment
        )
        btn_layout.add_widget(save_btn)
        
        layout.add_widget(btn_layout)
        self.add_widget(layout)
        
        # Bind events
        self.credit_spinner.bind(text=self.on_credit_selected)
        self.amount_input.bind(text=self.preview_payment)
    
    def on_enter(self):
        """Called when screen is entered"""
        self.load_active_credits()
    
    def load_active_credits(self):
        """Load active credits"""
        app = App.get_running_app()
        if hasattr(app, 'db_manager'):
            credits = app.db_manager.get_credits(status='active')
            credit_names = [f"{c['customer_name']} - {c['item_name']} (Sisa: {c['remaining_days']} hari)" 
                           for c in credits]
            self.credit_spinner.values = credit_names
            self.credits_data = credits
    
    def on_credit_selected(self, spinner, text):
        """When credit is selected"""
        if text and text != 'Pilih kredit yang akan dibayar...':
            try:
                selected_index = self.credit_spinner.values.index(text)
                self.selected_credit = self.credits_data[selected_index]
                self.update_credit_info()
            except (ValueError, IndexError):
                pass
    
    def update_credit_info(self):
        """Update credit information display"""
        if self.selected_credit:
            credit = self.selected_credit
            info_text = f"""Pelanggan: {credit['customer_name']}
Barang: {credit['item_name']}
Cicilan: {format_currency(credit['daily_amount'])}/hari
Sudah bayar: {credit['total_days_paid']} hari
Sisa: {credit['remaining_days']} hari"""
            
            self.credit_info.text = info_text
    
    def set_exact_amount(self, instance):
        """Set exact daily amount"""
        if self.selected_credit:
            self.amount_input.text = str(int(self.selected_credit['daily_amount']))
    
    def set_half_amount(self, instance):
        """Set half daily amount"""
        if self.selected_credit:
            half_amount = int(self.selected_credit['daily_amount'] / 2)
            self.amount_input.text = str(half_amount)
    
    def preview_payment(self, instance=None):
        """Preview payment calculation"""
        if not self.selected_credit or not self.amount_input.text:
            self.payment_preview.text = ''
            return
        
        try:
            amount = float(self.amount_input.text)
            daily_amount = self.selected_credit['daily_amount']
            remaining_days = self.selected_credit['remaining_days']
            
            if amount < daily_amount:
                # Underpayment
                preview_text = f"Bayar kurang: {format_currency(amount)}\n"
                preview_text += f"Tetap dihitung 1 hari setor\n"
                preview_text += f"Sisa: {remaining_days - 1} hari"
            elif amount == daily_amount:
                # Exact payment
                preview_text = f"Bayar pas: {format_currency(amount)}\n"
                preview_text += f"1 hari setor\n"
                preview_text += f"Sisa: {remaining_days - 1} hari"
            else:
                # Overpayment
                days_paid = min(int(amount // daily_amount), remaining_days)
                new_remaining = remaining_days - days_paid
                
                preview_text = f"Bayar lebih: {format_currency(amount)}\n"
                preview_text += f"Lunas {days_paid} hari sekaligus\n"
                preview_text += f"Sisa: {new_remaining} hari"
                
                if new_remaining == 0:
                    preview_text += "\n🎉 LUNAS!"
            
            self.payment_preview.text = preview_text
            
        except ValueError:
            self.payment_preview.text = ''
    
    def save_payment(self, instance):
        """Save payment"""
        if not self.selected_credit:
            self.show_error("Pilih kredit terlebih dahulu")
            return
        
        amount_text = self.amount_input.text.strip()
        if not amount_text:
            self.show_error("Masukkan jumlah pembayaran")
            return
        
        try:
            amount = float(amount_text)
            if amount <= 0:
                self.show_error("Jumlah pembayaran harus lebih dari 0")
                return
        except ValueError:
            self.show_error("Jumlah pembayaran harus berupa angka")
            return
        
        # Save payment
        app = App.get_running_app()
        if hasattr(app, 'db_manager'):
            success = app.db_manager.add_payment(self.selected_credit['id'], amount)
            
            if success:
                # Get updated credit info
                updated_credit = app.db_manager.get_credits(customer_id=self.selected_credit['customer_id'])
                if updated_credit:
                    credit = updated_credit[0]
                    
                    # Create receipt
                    receipt = Receipt(
                        customer_name=credit['customer_name'],
                        item_name=credit['item_name'],
                        total_price=credit['total_price'],
                        total_days=credit['total_days'],
                        daily_amount=credit['daily_amount'],
                        days_paid=credit['total_days_paid'],
                        remaining_days=credit['remaining_days'],
                        payment_amount=amount,
                        status="SUDAH" if credit['remaining_days'] == 0 else "SUDAH",
                        date=date.today()
                    )
                    
                    # Print receipt
                    self.print_receipt(receipt)
                
                # Clear form
                self.clear_form()
                
                self.show_success("Pembayaran berhasil dicatat")
                
                # Reload credits
                self.load_active_credits()
            else:
                self.show_error("Gagal menyimpan pembayaran")
    
    def print_receipt(self, receipt):
        """Print receipt via Bluetooth"""
        app = App.get_running_app()
        if hasattr(app, 'printer'):
            try:
                app.printer.print_receipt(receipt)
            except Exception as e:
                self.show_error(f"Gagal mencetak struk: {str(e)}")
    
    def clear_form(self):
        self.amount_input.text = ''
        self.credit_spinner.text = 'Pilih kredit yang akan dibayar...'
        self.credit_info.text = 'Pilih kredit untuk melihat detail'
        self.payment_preview.text = ''
        self.selected_credit = None
    
    def show_error(self, message):
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def show_success(self, message):
        popup = Popup(
            title='Berhasil',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def go_back(self, instance):
        App.get_running_app().root.current = 'dashboard'


class TagihHariIniScreen(Screen):
    """Screen untuk tagihan hari ini"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'tagih_hari_ini'
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Header
        header_layout = BoxLayout(size_hint_y=None, height=dp(50))
        
        back_btn = Button(
            text='← Kembali',
            size_hint_x=0.3,
            on_press=self.go_back
        )
        header_layout.add_widget(back_btn)
        
        title = Label(
            text='Tagih Hari Ini',
            font_size=dp(20),
            color=(0.2, 0.6, 0.8, 1)
        )
        header_layout.add_widget(title)
        
        refresh_btn = Button(
            text='🔄',
            size_hint_x=0.2,
            on_press=self.refresh_data
        )
        header_layout.add_widget(refresh_btn)
        
        layout.add_widget(header_layout)
        
        # Summary
        self.summary_label = Label(
            text='Loading...',
            size_hint_y=None,
            height=dp(60),
            font_size=dp(16)
        )
        layout.add_widget(self.summary_label)
        
        # Collection list
        scroll = ScrollView()
        self.collection_layout = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        self.collection_layout.bind(minimum_height=self.collection_layout.setter('height'))
        
        scroll.add_widget(self.collection_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Called when screen is entered"""
        self.refresh_data()
    
    def refresh_data(self, instance=None):
        """Refresh collection data"""
        app = App.get_running_app()
        if hasattr(app, 'db_manager'):
            collections = app.db_manager.get_today_collections()
            self.update_collection_list(collections)
    
    def update_collection_list(self, collections):
        """Update collection list display"""
        self.collection_layout.clear_widgets()
        
        # Update summary
        total_count = len(collections)
        paid_count = sum(1 for c in collections if c['paid_today'])
        unpaid_count = total_count - paid_count
        
        summary_text = f"Total: {total_count} | Sudah: {paid_count} | Belum: {unpaid_count}"
        self.summary_label.text = summary_text
        
        # Add collection items
        for collection in collections:
            item_layout = BoxLayout(
                size_hint_y=None,
                height=dp(80),
                spacing=dp(10),
                padding=[dp(10), dp(5)]
            )
            
            # Status icon
            status_color = (0.2, 0.8, 0.2, 1) if collection['paid_today'] else (0.8, 0.2, 0.2, 1)
            status_icon = "✓" if collection['paid_today'] else "!"
            
            status_label = Label(
                text=status_icon,
                size_hint_x=None,
                width=dp(30),
                font_size=dp(20),
                color=status_color
            )
            item_layout.add_widget(status_label)
            
            # Customer info
            info_text = f"{collection['customer_name']}\n{collection['item_name']}"
            info_label = Label(
                text=info_text,
                size_hint_x=0.5,
                text_size=(dp(150), None),
                halign='left',
                valign='middle'
            )
            item_layout.add_widget(info_label)
            
            # Amount and status
            amount_text = f"{format_currency(collection['daily_amount'])}\n"
            amount_text += f"({collection['total_days_paid']}x | {collection['remaining_days']}x)"
            
            amount_label = Label(
                text=amount_text,
                size_hint_x=0.3,
                text_size=(dp(100), None),
                halign='right',
                valign='middle'
            )
            item_layout.add_widget(amount_label)
            
            # Action button
            if collection['paid_today']:
                action_btn = Button(
                    text='Cetak Ulang',
                    size_hint_x=0.2,
                    background_color=(0.6, 0.6, 0.6, 1),
                    on_press=lambda x, cid=collection['credit_id']: self.reprint_receipt(cid)
                )
            else:
                action_btn = Button(
                    text='Bayar',
                    size_hint_x=0.2,
                    background_color=(0.2, 0.8, 0.2, 1),
                    on_press=lambda x, cid=collection['credit_id']: self.go_to_payment(cid)
                )
            
            item_layout.add_widget(action_btn)
            
            # Add separator
            separator = Label(
                text='',
                size_hint_y=None,
                height=dp(1),
                canvas=None
            )
            
            self.collection_layout.add_widget(item_layout)
            self.collection_layout.add_widget(separator)
    
    def go_to_payment(self, credit_id):
        """Go to payment screen for specific credit"""
        # Switch to payment screen and pre-select credit
        app = App.get_running_app()
        app.root.current = 'catat_bayar'
        
        # Schedule to select the credit after screen transition
        Clock.schedule_once(lambda dt: self.select_credit_in_payment_screen(credit_id), 0.1)
    
    def select_credit_in_payment_screen(self, credit_id):
        """Select specific credit in payment screen"""
        app = App.get_running_app()
        payment_screen = app.root.get_screen('catat_bayar')
        
        # Find and select the credit
        if hasattr(payment_screen, 'credits_data'):
            for i, credit in enumerate(payment_screen.credits_data):
                if credit['id'] == credit_id:
                    payment_screen.credit_spinner.text = payment_screen.credit_spinner.values[i]
                    payment_screen.selected_credit = credit
                    payment_screen.update_credit_info()
                    break
    
    def reprint_receipt(self, credit_id):
        """Reprint receipt for paid credit"""
        app = App.get_running_app()
        if hasattr(app, 'db_manager'):
            # Get credit info
            credits = app.db_manager.get_credits()
            credit = next((c for c in credits if c['id'] == credit_id), None)
            
            if credit:
                # Create receipt
                receipt = Receipt(
                    customer_name=credit['customer_name'],
                    item_name=credit['item_name'],
                    total_price=credit['total_price'],
                    total_days=credit['total_days'],
                    daily_amount=credit['daily_amount'],
                    days_paid=credit['total_days_paid'],
                    remaining_days=credit['remaining_days'],
                    payment_amount=credit['daily_amount'],  # Assume daily amount
                    status="SUDAH",
                    date=date.today()
                )
                
                # Print receipt
                self.print_receipt(receipt)
    
    def print_receipt(self, receipt):
        """Print receipt via Bluetooth"""
        app = App.get_running_app()
        if hasattr(app, 'printer'):
            try:
                app.printer.print_receipt(receipt)
                self.show_success("Struk berhasil dicetak ulang")
            except Exception as e:
                self.show_error(f"Gagal mencetak struk: {str(e)}")
    
    def show_error(self, message):
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def show_success(self, message):
        popup = Popup(
            title='Berhasil',
            content=Label(text=message),
            size_hint=(0.8, 0.3)
        )
        popup.open()
    
    def go_back(self, instance):
        App.get_running_app().root.current = 'dashboard'


class LaporanScreen(Screen):
    """Screen untuk laporan"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'laporan'
        self.setup_ui()
    
    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Header
        header_layout = BoxLayout(size_hint_y=None, height=dp(50))
        
        back_btn = Button(
            text='← Kembali',
            size_hint_x=0.3,
            on_press=self.go_back
        )
        header_layout.add_widget(back_btn)
        
        title = Label(
            text='Laporan',
            font_size=dp(20),
            color=(0.2, 0.6, 0.8, 1)
        )
        header_layout.add_widget(title)
        
        export_btn = Button(
            text='📄 Ekspor',
            size_hint_x=0.3,
            background_color=(0.2, 0.8, 0.2, 1),
            on_press=self.export_report
        )
        header_layout.add_widget(export_btn)
        
        layout.add_widget(header_layout)
        
        # Summary cards
        summary_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(100))
        
        self.total_piutang_card = Label(
            text='Total Piutang\nRp 0',
            font_size=dp(14),
            halign='center',
            valign='middle'
        )
        summary_layout.add_widget(self.total_piutang_card)
        
        self.total_lunas_card = Label(
            text='Total Lunas\nRp 0',
            font_size=dp(14),
            halign='center',
            valign='middle',
            color=(0.2, 0.8, 0.2, 1)
        )
        summary_layout.add_widget(self.total_lunas_card)
        
        layout.add_widget(summary_layout)
        
        # Report table
        scroll = ScrollView()
        self.report_layout = BoxLayout(orientation='vertical', spacing=dp(2), size_hint_y=None)
        self.report_layout.bind(minimum_height=self.report_layout.setter('height'))
        
        scroll.add_widget(self.report_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def on_enter(self):
        """Called when screen is entered"""
        self.load_report_data()
    
    def load_report_data(self):
        """Load report data"""
        app = App.get_running_app()
        if hasattr(app, 'db_manager'):
            # Get all credits
            active_credits = app.db_manager.get_credits(status='active')
            completed_credits = app.db_manager.get_credits(status='completed')
            
            self.update_report_display(active_credits, completed_credits)
    
    def update_report_display(self, active_credits, completed_credits):
        """Update report display"""
        self.report_layout.clear_widgets()
        
        # Calculate totals
        total_piutang = sum(c['remaining_amount'] for c in active_credits)
        total_lunas = sum(c['total_price'] for c in completed_credits)
        
        # Update summary cards
        self.total_piutang_card.text = f'Total Piutang\n{format_currency(total_piutang)}'
        self.total_lunas_card.text = f'Total Lunas\n{format_currency(total_lunas)}'
        
        # Table header
        header_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(2))
        
        headers = ['Nama', 'Barang', 'Total', 'Sudah', 'Sisa']
        for header in headers:
            header_label = Label(
                text=header,
                size_hint_x=0.2,
                font_size=dp(12),
                bold=True,
                color=(0.2, 0.6, 0.8, 1)
            )
            header_layout.add_widget(header_label)
        
        self.report_layout.add_widget(header_layout)
        
        # Add separator
        separator = Label(text='', size_hint_y=None, height=dp(2))
        self.report_layout.add_widget(separator)
        
        # Table rows - Active credits
        for credit in active_credits:
            row_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(2))
            
            # Customer name
            name_label = Label(
                text=credit['customer_name'][:15],
                size_hint_x=0.2,
                text_size=(dp(60), None),
                halign='left',
                valign='middle',
                font_size=dp(11)
            )
            row_layout.add_widget(name_label)
            
            # Item name
            item_label = Label(
                text=credit['item_name'][:15],
                size_hint_x=0.2,
                text_size=(dp(60), None),
                halign='left',
                valign='middle',
                font_size=dp(11)
            )
            row_layout.add_widget(item_label)
            
            # Total price
            total_label = Label(
                text=format_currency(credit['total_price']),
                size_hint_x=0.2,
                text_size=(dp(60), None),
                halign='right',
                valign='middle',
                font_size=dp(11)
            )
            row_layout.add_widget(total_label)
            
            # Paid amount
            paid_label = Label(
                text=format_currency(credit['total_amount_paid']),
                size_hint_x=0.2,
                text_size=(dp(60), None),
                halign='right',
                valign='middle',
                font_size=dp(11),
                color=(0.2, 0.8, 0.2, 1)
            )
            row_layout.add_widget(paid_label)
            
            # Remaining amount
            remaining_label = Label(
                text=format_currency(credit['remaining_amount']),
                size_hint_x=0.2,
                text_size=(dp(60), None),
                halign='right',
                valign='middle',
                font_size=dp(11),
                color=(0.8, 0.2, 0.2, 1)
            )
            row_layout.add_widget(remaining_label)
            
            self.report_layout.add_widget(row_layout)
    
    def export_report(self, instance):
        """Export report to PDF"""
        try:
            # Create simple text report
            app = App.get_running_app()
            if hasattr(app, 'db_manager'):
                active_credits = app.db_manager.get_credits(status='active')
                completed_credits = app.db_manager.get_credits(status='completed')
                
                # Generate report text
                report_text = self.generate_report_text(active_credits, completed_credits)
                
                # Save to file
                from datetime import datetime
                filename = f"laporan_kredit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                filepath = os.path.join(os.path.expanduser('~'), 'Documents', filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(report_text)
                
                self.show_success(f"Laporan berhasil diekspor ke:\n{filepath}")
        
        except Exception as e:
            self.show_error(f"Gagal mengekspor laporan: {str(e)}")
    
    def generate_report_text(self, active_credits, completed_credits):
        """Generate report text"""
        from datetime import datetime
        
        lines = []
        lines.append("=" * 50)
        lines.append("LAPORAN TOKO KREDIT SYARIAH")
        lines.append("=" * 50)
        lines.append(f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        lines.append("")
        
        # Summary
        total_piutang = sum(c['remaining_amount'] for c in active_credits)
        total_lunas = sum(c['total_price'] for c in completed_credits)
        
        lines.append("RINGKASAN:")
        lines.append(f"Total Piutang Aktif: {format_currency(total_piutang)}")
        lines.append(f"Total Kredit Lunas: {format_currency(total_lunas)}")
        lines.append(f"Jumlah Kredit Aktif: {len(active_credits)}")
        lines.append(f"Jumlah Kredit Lunas: {len(completed_credits)}")
        lines.append("")
        
        # Active credits detail
        lines.append("KREDIT AKTIF:")
        lines.append("-" * 50)
        
        for credit in active_credits:
            lines.append(f"Nama: {credit['customer_name']}")
            lines.append(f"Barang: {credit['item_name']}")
            lines.append(f"Total: {format_currency(credit['total_price'])}")
            lines.append(f"Sudah Bayar: {format_currency(credit['total_amount_paid'])} ({credit['total_days_paid']} hari)")
            lines.append(f"Sisa: {format_currency(credit['remaining_amount'])} ({credit['remaining_days']} hari)")
            lines.append("")
        
        return "\n".join(lines)
    
    def show_error(self, message):
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def show_success(self, message):
        popup = Popup(
            title='Berhasil',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def go_back(self, instance):
        App.get_running_app().root.current = 'dashboard'