#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Manager untuk Toko Kredit Syariah
Menggunakan SQLite dengan enkripsi Fernet + PBKDF2
"""

import sqlite3
import os
import json
import hashlib
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class DatabaseManager:
    """Manager untuk database dengan enkripsi"""
    
    def __init__(self, password):
        self.password = password
        self.db_path = 'kredit_data.db'
        self.key = self._derive_key(password)
        self.cipher = Fernet(self.key)
        self.init_database()
    
    def _derive_key(self, password):
        """Derive encryption key dari password menggunakan PBKDF2"""
        # Salt tetap untuk konsistensi (dalam produksi, gunakan salt random yang disimpan)
        salt = b'toko_kredit_syariah_salt_2025'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def init_database(self):
        """Inisialisasi database dan tabel"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel pelanggan
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                credit_limit REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_encrypted TEXT
            )
        ''')
        
        # Tabel kredit
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS credits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                item_name TEXT NOT NULL,
                total_price REAL NOT NULL,
                daily_amount REAL NOT NULL,
                total_days INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_encrypted TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        
        # Tabel pembayaran
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credit_id INTEGER,
                amount REAL NOT NULL,
                payment_date DATE NOT NULL,
                days_paid INTEGER DEFAULT 1,
                remaining_days INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_encrypted TEXT,
                FOREIGN KEY (credit_id) REFERENCES credits (id)
            )
        ''')
        
        # Tabel libur
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS holidays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                holiday_date DATE NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel backup log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backup_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_type TEXT NOT NULL,
                backup_path TEXT,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def encrypt_data(self, data):
        """Enkripsi data sensitif"""
        if isinstance(data, dict):
            data = json.dumps(data)
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data):
        """Dekripsi data sensitif"""
        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode()).decode()
            return json.loads(decrypted)
        except:
            return {}
    
    # === CUSTOMER OPERATIONS ===
    
    def add_customer(self, name, address="", phone="", credit_limit=0):
        """Tambah pelanggan baru"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Data sensitif yang akan dienkripsi
        sensitive_data = {
            'address': address,
            'phone': phone,
            'notes': ''
        }
        
        encrypted_data = self.encrypt_data(sensitive_data)
        
        cursor.execute('''
            INSERT INTO customers (name, address, phone, credit_limit, data_encrypted)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, address, phone, credit_limit, encrypted_data))
        
        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return customer_id
    
    def get_customers(self, search_term=""):
        """Ambil daftar pelanggan"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if search_term:
            cursor.execute('''
                SELECT * FROM customers 
                WHERE name LIKE ? OR phone LIKE ?
                ORDER BY name
            ''', (f'%{search_term}%', f'%{search_term}%'))
        else:
            cursor.execute('SELECT * FROM customers ORDER BY name')
        
        customers = []
        for row in cursor.fetchall():
            customer = {
                'id': row[0],
                'name': row[1],
                'address': row[2],
                'phone': row[3],
                'credit_limit': row[4],
                'created_at': row[5]
            }
            
            # Decrypt additional data if exists
            if row[6]:
                try:
                    additional_data = self.decrypt_data(row[6])
                    customer.update(additional_data)
                except:
                    pass
            
            customers.append(customer)
        
        conn.close()
        return customers
    
    def get_customer(self, customer_id):
        """Ambil data pelanggan berdasarkan ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
        row = cursor.fetchone()
        
        if row:
            customer = {
                'id': row[0],
                'name': row[1],
                'address': row[2],
                'phone': row[3],
                'credit_limit': row[4],
                'created_at': row[5]
            }
            
            # Decrypt additional data
            if row[6]:
                try:
                    additional_data = self.decrypt_data(row[6])
                    customer.update(additional_data)
                except:
                    pass
            
            conn.close()
            return customer
        
        conn.close()
        return None
    
    # === CREDIT OPERATIONS ===
    
    def add_credit(self, customer_id, item_name, total_price, total_days):
        """Tambah kredit baru"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hitung cicilan harian (pembulatan ke atas)
        daily_amount = int((total_price + total_days - 1) // total_days)  # Ceiling division
        
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=total_days)
        
        # Data sensitif
        sensitive_data = {
            'item_details': item_name,
            'original_price': total_price,
            'notes': ''
        }
        
        encrypted_data = self.encrypt_data(sensitive_data)
        
        cursor.execute('''
            INSERT INTO credits (customer_id, item_name, total_price, daily_amount, 
                               total_days, start_date, end_date, data_encrypted)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, item_name, total_price, daily_amount, total_days, 
              start_date, end_date, encrypted_data))
        
        credit_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return credit_id
    
    def get_credits(self, customer_id=None, status='active'):
        """Ambil daftar kredit"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if customer_id:
            cursor.execute('''
                SELECT c.*, cust.name as customer_name 
                FROM credits c
                JOIN customers cust ON c.customer_id = cust.id
                WHERE c.customer_id = ? AND c.status = ?
                ORDER BY c.created_at DESC
            ''', (customer_id, status))
        else:
            cursor.execute('''
                SELECT c.*, cust.name as customer_name 
                FROM credits c
                JOIN customers cust ON c.customer_id = cust.id
                WHERE c.status = ?
                ORDER BY c.created_at DESC
            ''', (status,))
        
        credits = []
        for row in cursor.fetchall():
            credit = {
                'id': row[0],
                'customer_id': row[1],
                'item_name': row[2],
                'total_price': row[3],
                'daily_amount': row[4],
                'total_days': row[5],
                'start_date': row[6],
                'end_date': row[7],
                'status': row[8],
                'created_at': row[9],
                'customer_name': row[11]
            }
            
            # Decrypt additional data
            if row[10]:
                try:
                    additional_data = self.decrypt_data(row[10])
                    credit.update(additional_data)
                except:
                    pass
            
            # Calculate payment status
            payment_info = self.get_payment_summary(row[0])
            credit.update(payment_info)
            
            credits.append(credit)
        
        conn.close()
        return credits
    
    # === PAYMENT OPERATIONS ===
    
    def add_payment(self, credit_id, amount, payment_date=None):
        """Tambah pembayaran dengan logika fleksibel"""
        if payment_date is None:
            payment_date = datetime.now().date()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ambil info kredit
        cursor.execute('SELECT * FROM credits WHERE id = ?', (credit_id,))
        credit = cursor.fetchone()
        
        if not credit:
            conn.close()
            return False
        
        daily_amount = credit[4]  # daily_amount
        total_days = credit[5]    # total_days
        
        # Hitung sudah bayar berapa hari
        cursor.execute('''
            SELECT COALESCE(SUM(days_paid), 0) as total_days_paid
            FROM payments WHERE credit_id = ?
        ''', (credit_id,))
        
        total_days_paid = cursor.fetchone()[0]
        
        # Logika pembayaran fleksibel
        if amount < daily_amount:
            # Bayar kurang: tetap 1x setor, sisa hari tetap
            days_paid = 1
            remaining_days = total_days - total_days_paid - 1
        elif amount >= daily_amount:
            # Bayar cukup/lebih: hitung berapa hari terlunasi
            days_paid = min(int(amount // daily_amount), total_days - total_days_paid)
            remaining_days = total_days - total_days_paid - days_paid
        
        # Pastikan tidak minus
        remaining_days = max(0, remaining_days)
        
        # Simpan pembayaran
        cursor.execute('''
            INSERT INTO payments (credit_id, amount, payment_date, days_paid, remaining_days)
            VALUES (?, ?, ?, ?, ?)
        ''', (credit_id, amount, payment_date, days_paid, remaining_days))
        
        # Update status kredit jika lunas
        if remaining_days == 0:
            cursor.execute('UPDATE credits SET status = ? WHERE id = ?', ('completed', credit_id))
        
        conn.commit()
        conn.close()
        
        return True
    
    def get_payment_summary(self, credit_id):
        """Ambil ringkasan pembayaran untuk kredit"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COALESCE(SUM(days_paid), 0) as total_days_paid,
                COALESCE(SUM(amount), 0) as total_amount_paid,
                COUNT(*) as payment_count,
                MAX(payment_date) as last_payment_date
            FROM payments 
            WHERE credit_id = ?
        ''', (credit_id,))
        
        result = cursor.fetchone()
        
        # Ambil info kredit
        cursor.execute('SELECT total_days, daily_amount FROM credits WHERE id = ?', (credit_id,))
        credit_info = cursor.fetchone()
        
        conn.close()
        
        if result and credit_info:
            total_days_paid = result[0]
            total_amount_paid = result[1]
            payment_count = result[2]
            last_payment_date = result[3]
            
            total_days = credit_info[0]
            daily_amount = credit_info[1]
            
            remaining_days = max(0, total_days - total_days_paid)
            remaining_amount = remaining_days * daily_amount
            
            return {
                'total_days_paid': total_days_paid,
                'remaining_days': remaining_days,
                'total_amount_paid': total_amount_paid,
                'remaining_amount': remaining_amount,
                'payment_count': payment_count,
                'last_payment_date': last_payment_date,
                'is_completed': remaining_days == 0
            }
        
        return {
            'total_days_paid': 0,
            'remaining_days': credit_info[0] if credit_info else 0,
            'total_amount_paid': 0,
            'remaining_amount': credit_info[0] * credit_info[1] if credit_info else 0,
            'payment_count': 0,
            'last_payment_date': None,
            'is_completed': False
        }
    
    def get_today_collections(self):
        """Ambil daftar tagihan hari ini"""
        today = datetime.now().date()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ambil semua kredit aktif
        cursor.execute('''
            SELECT c.*, cust.name as customer_name
            FROM credits c
            JOIN customers cust ON c.customer_id = cust.id
            WHERE c.status = 'active'
        ''')
        
        collections = []
        for row in cursor.fetchall():
            credit_id = row[0]
            customer_name = row[11]
            daily_amount = row[4]
            
            # Cek apakah sudah bayar hari ini
            cursor.execute('''
                SELECT COUNT(*) FROM payments 
                WHERE credit_id = ? AND payment_date = ?
            ''', (credit_id, today))
            
            paid_today = cursor.fetchone()[0] > 0
            
            # Ambil ringkasan pembayaran
            payment_info = self.get_payment_summary(credit_id)
            
            # Skip jika sudah lunas
            if payment_info['is_completed']:
                continue
            
            collections.append({
                'credit_id': credit_id,
                'customer_name': customer_name,
                'daily_amount': daily_amount,
                'paid_today': paid_today,
                'total_days_paid': payment_info['total_days_paid'],
                'remaining_days': payment_info['remaining_days'],
                'item_name': row[2]
            })
        
        conn.close()
        return collections
    
    # === HOLIDAY OPERATIONS ===
    
    def mark_holiday(self, holiday_date=None):
        """Tandai hari libur"""
        if holiday_date is None:
            holiday_date = datetime.now().date()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('INSERT INTO holidays (holiday_date) VALUES (?)', (holiday_date,))
            conn.commit()
            
            # Mundurkan jatuh tempo semua kredit aktif
            cursor.execute('''
                UPDATE credits 
                SET end_date = date(end_date, '+1 day')
                WHERE status = 'active'
            ''')
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Sudah ada holiday untuk tanggal ini
            conn.close()
            return False
    
    def is_holiday(self, date):
        """Cek apakah tanggal adalah hari libur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM holidays WHERE holiday_date = ?', (date,))
        result = cursor.fetchone()[0] > 0
        
        conn.close()
        return result
    
    # === BACKUP OPERATIONS ===
    
    def log_backup(self, backup_type, backup_path, status):
        """Log backup activity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO backup_log (backup_type, backup_path, status)
            VALUES (?, ?, ?)
        ''', (backup_type, backup_path, status))
        
        conn.commit()
        conn.close()
    
    def get_last_backup(self):
        """Ambil info backup terakhir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM backup_log 
            ORDER BY created_at DESC 
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'backup_type': result[1],
                'backup_path': result[2],
                'status': result[3],
                'created_at': result[4]
            }
        
        return None
    
    def export_data(self):
        """Export semua data untuk backup"""
        conn = sqlite3.connect(self.db_path)
        
        # Export semua tabel
        data = {}
        
        tables = ['customers', 'credits', 'payments', 'holidays', 'backup_log']
        
        for table in tables:
            cursor = conn.cursor()
            cursor.execute(f'SELECT * FROM {table}')
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            data[table] = {
                'columns': columns,
                'rows': rows
            }
        
        conn.close()
        return data
    
    def import_data(self, data):
        """Import data dari backup"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Clear existing data
            cursor.execute('DELETE FROM payments')
            cursor.execute('DELETE FROM credits')
            cursor.execute('DELETE FROM customers')
            cursor.execute('DELETE FROM holidays')
            
            # Import data
            for table, table_data in data.items():
                if table == 'backup_log':
                    continue  # Skip backup log
                
                columns = table_data['columns']
                rows = table_data['rows']
                
                placeholders = ','.join(['?' for _ in columns])
                
                cursor.executemany(
                    f'INSERT INTO {table} ({",".join(columns)}) VALUES ({placeholders})',
                    rows
                )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            return False