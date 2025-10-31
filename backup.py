#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup Manager untuk Toko Kredit Syariah
Mendukung backup otomatis ke Google Drive dan folder internal
"""

import os
import sys
import json
import shutil
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

# Encryption
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Check if running on Android
try:
    from kivy.utils import platform
    IS_ANDROID = platform == 'android'
except ImportError:
    IS_ANDROID = False

# Google Drive API (disabled for Android compatibility)
GOOGLE_DRIVE_AVAILABLE = False
# Commented out heavy Google API dependencies for Android build
# try:
#     from googleapiclient.discovery import build
#     from google_auth_oauthlib.flow import InstalledAppFlow
#     from google.auth.transport.requests import Request
#     from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
#     import pickle
#     GOOGLE_DRIVE_AVAILABLE = True
# except ImportError:
print("Info: Google Drive API disabled for Android compatibility. Using local backup only.")

# Android storage
if IS_ANDROID:
    try:
        from plyer import storagepath
        ANDROID_STORAGE = True
    except ImportError:
        ANDROID_STORAGE = False
        print("Warning: Android storage access not available.")
else:
    ANDROID_STORAGE = False


class BackupManager:
    """Backup and Restore Manager"""
    
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    def __init__(self, db_path, password):
        self.db_path = db_path
        self.password = password
        self.backup_folder = os.path.join(os.path.expanduser('~'), 'KreditBackup')
        self.struk_folder = os.path.join(self.backup_folder, 'Struk')
        
        # Create backup folders
        os.makedirs(self.backup_folder, exist_ok=True)
        os.makedirs(self.struk_folder, exist_ok=True)
        
        # Encryption setup
        self.fernet = self._setup_encryption()
        
        # Google Drive setup
        self.drive_service = None
        self.google_drive_enabled = False
        
        # Auto backup settings
        self.auto_backup_interval = 30 * 60  # 30 minutes
        self.last_backup_time = None
        self.backup_thread = None
        self.stop_backup = False
    
    def _setup_encryption(self):
        """Setup encryption for backups"""
        try:
            # Generate key from password
            password_bytes = self.password.encode()
            salt = b'kredit_syariah_salt_2025'  # Fixed salt for consistency
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            return Fernet(key)
            
        except Exception as e:
            print(f"Encryption setup failed: {str(e)}")
            return None
    
    def setup_google_drive(self, credentials_file=None):
        """Setup Google Drive API"""
        if not GOOGLE_DRIVE_AVAILABLE:
            print("Google Drive API not available")
            return False
        
        try:
            creds = None
            token_file = os.path.join(self.backup_folder, 'token.json')
            
            # Load existing credentials
            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not credentials_file:
                        print("Google Drive credentials file not provided")
                        return False
                    
                    flow = InstalledAppFlow.from_client_secrets_file(credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            # Build Drive service
            self.drive_service = build('drive', 'v3', credentials=creds)
            self.google_drive_enabled = True
            
            print("Google Drive setup successful")
            return True
            
        except Exception as e:
            print(f"Google Drive setup failed: {str(e)}")
            self.google_drive_enabled = False
            return False
    
    def create_backup(self):
        """Create encrypted backup"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'kredit_backup_{timestamp}.enc'
            backup_path = os.path.join(self.backup_folder, backup_filename)
            
            # Create backup data
            backup_data = self._create_backup_data()
            
            # Encrypt backup
            if self.fernet:
                encrypted_data = self.fernet.encrypt(json.dumps(backup_data).encode())
            else:
                encrypted_data = json.dumps(backup_data).encode()
            
            # Save to file
            with open(backup_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Upload to Google Drive if enabled
            if self.google_drive_enabled:
                self._upload_to_drive(backup_path, backup_filename)
            
            # Clean old backups (keep last 10)
            self._cleanup_old_backups()
            
            self.last_backup_time = datetime.now()
            
            print(f"Backup created: {backup_filename}")
            return backup_path
            
        except Exception as e:
            print(f"Backup creation failed: {str(e)}")
            return None
    
    def _create_backup_data(self):
        """Create backup data from database"""
        backup_data = {
            'version': '1.0',
            'timestamp': datetime.now().isoformat(),
            'tables': {}
        }
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Backup each table
            for table in tables:
                table_name = table['name']
                if table_name.startswith('sqlite_'):
                    continue
                
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Convert rows to dictionaries
                backup_data['tables'][table_name] = [dict(row) for row in rows]
            
            conn.close()
            return backup_data
            
        except Exception as e:
            print(f"Database backup failed: {str(e)}")
            return {'error': str(e)}
    
    def restore_backup(self, backup_path):
        """Restore from backup file"""
        try:
            # Read backup file
            with open(backup_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt backup
            if self.fernet:
                decrypted_data = self.fernet.decrypt(encrypted_data)
                backup_data = json.loads(decrypted_data.decode())
            else:
                backup_data = json.loads(encrypted_data.decode())
            
            # Restore to database
            self._restore_to_database(backup_data)
            
            print(f"Backup restored from: {backup_path}")
            return True
            
        except Exception as e:
            print(f"Backup restore failed: {str(e)}")
            return False
    
    def _restore_to_database(self, backup_data):
        """Restore backup data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing data
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table['name']
                if not table_name.startswith('sqlite_'):
                    cursor.execute(f"DELETE FROM {table_name}")
            
            # Restore data
            for table_name, rows in backup_data['tables'].items():
                if not rows:
                    continue
                
                # Get column names
                columns = list(rows[0].keys())
                placeholders = ','.join(['?' for _ in columns])
                
                # Insert data
                for row in rows:
                    values = [row[col] for col in columns]
                    cursor.execute(f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})", values)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Database restore failed: {str(e)}")
            raise
    
    def _upload_to_drive(self, file_path, filename):
        """Upload backup to Google Drive"""
        try:
            if not self.drive_service:
                return False
            
            # Check if backup folder exists in Drive
            folder_id = self._get_or_create_drive_folder('KreditBackup')
            
            # Upload file
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(file_path, resumable=True)
            
            file = self.drive_service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            print(f"File uploaded to Google Drive: {file.get('id')}")
            return True
            
        except Exception as e:
            print(f"Google Drive upload failed: {str(e)}")
            return False
    
    def _get_or_create_drive_folder(self, folder_name):
        """Get or create folder in Google Drive"""
        try:
            # Search for existing folder
            results = self.drive_service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)"
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                return folders[0]['id']
            
            # Create new folder
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.drive_service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            return folder.get('id')
            
        except Exception as e:
            print(f"Drive folder creation failed: {str(e)}")
            return None
    
    def _cleanup_old_backups(self):
        """Clean up old backup files"""
        try:
            # Get all backup files
            backup_files = []
            for filename in os.listdir(self.backup_folder):
                if filename.startswith('kredit_backup_') and filename.endswith('.enc'):
                    filepath = os.path.join(self.backup_folder, filename)
                    backup_files.append((filepath, os.path.getmtime(filepath)))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Keep only last 10 backups
            for filepath, _ in backup_files[10:]:
                os.remove(filepath)
                print(f"Removed old backup: {os.path.basename(filepath)}")
            
        except Exception as e:
            print(f"Backup cleanup failed: {str(e)}")
    
    def get_latest_backup(self):
        """Get path to latest backup file"""
        try:
            backup_files = []
            for filename in os.listdir(self.backup_folder):
                if filename.startswith('kredit_backup_') and filename.endswith('.enc'):
                    filepath = os.path.join(self.backup_folder, filename)
                    backup_files.append((filepath, os.path.getmtime(filepath)))
            
            if backup_files:
                # Sort by modification time (newest first)
                backup_files.sort(key=lambda x: x[1], reverse=True)
                return backup_files[0][0]
            
            return None
            
        except Exception as e:
            print(f"Get latest backup failed: {str(e)}")
            return None
    
    def start_auto_backup(self):
        """Start automatic backup thread"""
        if self.backup_thread and self.backup_thread.is_alive():
            return
        
        self.stop_backup = False
        self.backup_thread = threading.Thread(target=self._auto_backup_worker)
        self.backup_thread.daemon = True
        self.backup_thread.start()
        
        print("Auto backup started")
    
    def stop_auto_backup(self):
        """Stop automatic backup thread"""
        self.stop_backup = True
        if self.backup_thread:
            self.backup_thread.join(timeout=5)
        
        print("Auto backup stopped")
    
    def _auto_backup_worker(self):
        """Auto backup worker thread"""
        while not self.stop_backup:
            try:
                # Check if backup is needed
                if self._should_backup():
                    self.create_backup()
                
                # Sleep for 1 minute before checking again
                time.sleep(60)
                
            except Exception as e:
                print(f"Auto backup error: {str(e)}")
                time.sleep(60)
    
    def _should_backup(self):
        """Check if backup is needed"""
        if not self.last_backup_time:
            return True
        
        time_since_backup = datetime.now() - self.last_backup_time
        return time_since_backup.total_seconds() >= self.auto_backup_interval
    
    def save_receipt_pdf(self, receipt_text, customer_name):
        """Save receipt as text file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'struk_{customer_name}_{timestamp}.txt'
            filepath = os.path.join(self.struk_folder, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(receipt_text)
            
            print(f"Receipt saved: {filename}")
            return filepath
            
        except Exception as e:
            print(f"Receipt save failed: {str(e)}")
            return None
    
    def get_backup_status(self):
        """Get backup status information"""
        status = {
            'last_backup': self.last_backup_time.isoformat() if self.last_backup_time else None,
            'google_drive_enabled': self.google_drive_enabled,
            'backup_folder': self.backup_folder,
            'auto_backup_running': self.backup_thread and self.backup_thread.is_alive()
        }
        
        # Count backup files
        try:
            backup_files = [f for f in os.listdir(self.backup_folder) 
                           if f.startswith('kredit_backup_') and f.endswith('.enc')]
            status['backup_count'] = len(backup_files)
        except:
            status['backup_count'] = 0
        
        return status


# Global backup manager instance
backup_manager = None


def get_backup_manager(db_path=None, password=None):
    """Get global backup manager instance"""
    global backup_manager
    
    if backup_manager is None and db_path and password:
        backup_manager = BackupManager(db_path, password)
    
    return backup_manager


def initialize_backup(db_path, password):
    """Initialize backup manager"""
    global backup_manager
    backup_manager = BackupManager(db_path, password)
    return backup_manager