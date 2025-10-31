#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bluetooth ESC/POS Thermal Printer Module
Mendukung printer thermal 58mm via Bluetooth
"""

import os
import sys
import time
import threading
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Check if running on Android in a more robust way
IS_ANDROID = False
try:
    from kivy.utils import platform
    IS_ANDROID = platform == 'android'
except ImportError:
    pass

# Import Bluetooth libraries based on platform
BLUETOOTH_AVAILABLE = False
ANDROID_BLUETOOTH = False

if IS_ANDROID:
    try:
        from jnius import autoclass, cast
        try:
            from plyer import bluetooth as plyer_bluetooth
            ANDROID_BLUETOOTH = True
            BLUETOOTH_AVAILABLE = True
        except ImportError:
            print("Warning: Plyer bluetooth not available.")
    except ImportError:
        print("Warning: Android Bluetooth not available.")
else:
    try:
        import bluetooth
        BLUETOOTH_AVAILABLE = True
    except ImportError:
        print("Warning: Bluetooth not available.")

try:
    import serial
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("Warning: Serial not available.")

from datetime import datetime

# Try to import Receipt model safely
try:
    from models import Receipt
except ImportError:
    # Define a simple Receipt class as fallback
    @dataclass
    class Receipt:
        customer_name: str
        item_name: str
        total_price: float
        total_days: int
        daily_amount: float
        days_paid: int
        remaining_days: int
        payment_amount: float
        status: str
        date: datetime
        
        def format_currency(self, amount):
            return f"Rp {amount:,.0f}".replace(",", ".")

class BluetoothPrinter:
    """Bluetooth ESC/POS Printer Manager"""
    
    # ESC/POS Commands
    ESC = b'\x1b'
    INIT = ESC + b'@'
    ALIGN_LEFT = ESC + b'a\x00'
    ALIGN_CENTER = ESC + b'a\x01'
    ALIGN_RIGHT = ESC + b'a\x02'
    BOLD_ON = ESC + b'E\x01'
    BOLD_OFF = ESC + b'E\x00'
    UNDERLINE_ON = ESC + b'-\x01'
    UNDERLINE_OFF = ESC + b'-\x00'
    FONT_SMALL = ESC + b'!\x01'
    FONT_NORMAL = ESC + b'!\x00'
    FONT_LARGE = ESC + b'!\x10'
    CUT_PAPER = ESC + b'd\x03' + ESC + b'i'
    LINE_FEED = b'\n'
    
    def __init__(self):
        self.socket = None
        self.connected_device = None
        self.is_connected = False
        self.last_error = None
        
    def scan_devices(self):
        """Scan for available Bluetooth devices"""
        try:
            if not BLUETOOTH_AVAILABLE:
                self.last_error = "Bluetooth is not available"
                return []
                
            print("Scanning for Bluetooth devices...")
            
            if IS_ANDROID and ANDROID_BLUETOOTH:
                # Android-specific implementation
                try:
                    # Use Plyer for scanning on Android
                    devices = plyer_bluetooth.discover_devices()
                    printer_devices = []
                    for addr, name in devices.items():
                        if any(keyword in name.upper() for keyword in ['PRINTER', 'POS', 'THERMAL', 'XPRINTER', 'ZONERICH', 'EPSON']):
                            printer_devices.append({'address': addr, 'name': name})
                    return printer_devices
                except Exception as e:
                    self.last_error = f"Error scanning Android devices: {str(e)}"
                    print(self.last_error)
                    return []
            else:
                # Standard Python implementation
                devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True)
                printer_devices = []
                for addr, name in devices:
                    if any(keyword in name.upper() for keyword in ['PRINTER', 'POS', 'THERMAL', 'XPRINTER', 'ZONERICH', 'EPSON']):
                        printer_devices.append({'address': addr, 'name': name})
                return printer_devices
        except Exception as e:
            self.last_error = f"Error scanning devices: {str(e)}"
            print(self.last_error)
            return []
    
    def connect(self, device_address):
        """Connect to Bluetooth printer"""
        try:
            if not BLUETOOTH_AVAILABLE:
                self.last_error = "Bluetooth is not available"
                return False
                
            if self.is_connected:
                self.disconnect()
            
            print(f"Connecting to printer: {device_address}")
            
            if IS_ANDROID and ANDROID_BLUETOOTH:
                # Android-specific implementation using Pyjnius
                try:
                    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
                    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
                    BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
                    UUID = autoclass('java.util.UUID')
                    
                    adapter = BluetoothAdapter.getDefaultAdapter()
                    device = adapter.getRemoteDevice(device_address)
                    socket = device.createRfcommSocketToServiceRecord(
                        UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")  # SPP UUID
                    )
                    
                    socket.connect()
                    self.socket = socket
                    self.connected_device = device_address
                    self.is_connected = True
                    
                    # Initialize printer
                    self.send_command(self.INIT)
                    
                    print("Printer connected successfully")
                    return True
                except Exception as e:
                    self.last_error = f"Android connection failed: {str(e)}"
                    print(self.last_error)
                    return False
            else:
                # Standard Python implementation
                self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
                self.socket.connect((device_address, 1))  # Port 1 is common for printers
                
                self.connected_device = device_address
                self.is_connected = True
                
                # Initialize printer
                self.send_command(self.INIT)
                
                print("Printer connected successfully")
                return True
        except Exception as e:
            self.last_error = f"Connection failed: {str(e)}"
            print(self.last_error)
            self.is_connected = False
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            return False
    
    def disconnect(self):
        """Disconnect from printer"""
        try:
            if self.socket:
                if IS_ANDROID and ANDROID_BLUETOOTH:
                    self.socket.close()
                else:
                    self.socket.close()
                self.socket = None
            
            self.is_connected = False
            self.connected_device = None
            print("Printer disconnected")
            
        except Exception as e:
            print(f"Error disconnecting: {str(e)}")
    
    def send_command(self, command):
        """Send raw command to printer"""
        if not self.is_connected or not self.socket:
            raise Exception("Printer not connected")
        
        try:
            if IS_ANDROID and ANDROID_BLUETOOTH:
                # Android-specific implementation
                output_stream = self.socket.getOutputStream()
                output_stream.write(command)
                output_stream.flush()
            else:
                # Standard Python implementation
                self.socket.send(command)
                
            time.sleep(0.1)  # Small delay for printer processing
            
        except Exception as e:
            self.last_error = f"Send command failed: {str(e)}"
            raise Exception(self.last_error)
    
    def send_text(self, text, encoding='utf-8'):
        """Send text to printer"""
        try:
            # Convert text to bytes
            if isinstance(text, str):
                text_bytes = text.encode(encoding, errors='replace')
            else:
                text_bytes = text
            
            self.send_command(text_bytes)
            
        except Exception as e:
            self.last_error = f"Send text failed: {str(e)}"
            raise Exception(self.last_error)
    
    def print_line(self, text, align='left', bold=False, underline=False, font_size='normal'):
        """Print a line with formatting"""
        try:
            # Set alignment
            if align == 'center':
                self.send_command(self.ALIGN_CENTER)
            elif align == 'right':
                self.send_command(self.ALIGN_RIGHT)
            else:
                self.send_command(self.ALIGN_LEFT)
            
            # Set font size
            if font_size == 'small':
                self.send_command(self.FONT_SMALL)
            elif font_size == 'large':
                self.send_command(self.FONT_LARGE)
            else:
                self.send_command(self.FONT_NORMAL)
            
            # Set bold
            if bold:
                self.send_command(self.BOLD_ON)
            else:
                self.send_command(self.BOLD_OFF)
            
            # Set underline
            if underline:
                self.send_command(self.UNDERLINE_ON)
            else:
                self.send_command(self.UNDERLINE_OFF)
            
            # Send text
            self.send_text(text + '\n')
            
            # Reset formatting
            self.send_command(self.FONT_NORMAL)
            self.send_command(self.BOLD_OFF)
            self.send_command(self.UNDERLINE_OFF)
            self.send_command(self.ALIGN_LEFT)
            
        except Exception as e:
            raise Exception(f"Print line failed: {str(e)}")
    
    def print_separator(self, char='=', length=32):
        """Print separator line"""
        separator = char * length
        self.print_line(separator, align='center')
    
    def print_receipt(self, receipt):
        """Print formatted receipt"""
        try:
            if not self.is_connected:
                raise Exception("Printer not connected")
            
            # Initialize printer
            self.send_command(self.INIT)
            
            # Header
            self.print_separator('=', 32)
            self.print_line("TOKO ANDA - KREDIT", align='center', bold=True)
            self.print_separator('=', 32)
            
            # Receipt number and date
            receipt_no = f"#{receipt.date.strftime('%Y-%m-%d')}-{receipt.customer_name[:3].upper()}"
            self.print_line(f"No: {receipt_no}")
            self.print_line(f"Tgl: {receipt.date.strftime('%d %b %Y')}")
            
            self.print_separator('-', 32)
            
            # Customer and item info
            self.print_line(f"Nama : {receipt.customer_name[:20]}")
            self.print_line(f"Barang: {receipt.item_name[:20]}")
            self.print_line(f"Harga : {receipt.format_currency(receipt.total_price)}")
            self.print_line(f"Cicilan: {receipt.total_days} hari")
            self.print_line(f"Per Hari: {receipt.format_currency(receipt.daily_amount)}")
            
            self.print_separator('-', 32)
            
            # Payment status
            self.print_line(f"SUDAH SETOR : {receipt.days_paid}x")
            self.print_line(f"SISA SETOR  : {receipt.remaining_days}x")
            
            if receipt.payment_amount > 0:
                self.print_line(f"Hari Ini   : {receipt.format_currency(receipt.payment_amount)}")
            
            self.print_separator('-', 32)
            
            # Status
            status_text = f"Status: {receipt.status}"
            if receipt.status == "SUDAH":
                status_text += " ✓"
            
            self.print_line(status_text, bold=True)
            
            # Special messages for overpayment
            if receipt.payment_amount > receipt.daily_amount and receipt.remaining_days > 0:
                days_ahead = int(receipt.payment_amount // receipt.daily_amount) - 1
                if days_ahead > 0:
                    self.print_line(f"Lunas {days_ahead} hari ke depan!", align='center', bold=True)
            
            if receipt.remaining_days == 0:
                self.print_line("🎉 LUNAS SEMUA! 🎉", align='center', bold=True)
            
            self.print_separator('-', 32)
            
            # Footer
            self.print_line("Catatan: Tanpa DP. Tanpa denda.", align='center', font_size='small')
            
            self.print_separator('=', 32)
            
            # Signature
            self.print_line("Ttd: ___________")
            
            # Cut paper
            self.send_command(self.LINE_FEED * 3)
            self.send_command(self.CUT_PAPER)
            
            print("Receipt printed successfully")
            return True
            
        except Exception as e:
            self.last_error = f"Print receipt failed: {str(e)}"
            print(self.last_error)
            raise Exception(self.last_error)
    
    def test_print(self):
        """Print test page"""
        try:
            if not self.is_connected:
                raise Exception("Printer not connected")
            
            # Initialize printer
            self.send_command(self.INIT)
            
            # Test header
            self.print_separator('=', 32)
            self.print_line("TEST PRINT", align='center', bold=True, font_size='large')
            self.print_separator('=', 32)
            
            # Test content
            self.print_line(f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            self.print_line("Printer: Connected ✓", bold=True)
            self.print_line("")
            
            # Test formatting
            self.print_line("Test Alignment:")
            self.print_line("Left aligned", align='left')
            self.print_line("Center aligned", align='center')
            self.print_line("Right aligned", align='right')
            self.print_line("")
            
            self.print_line("Test Formatting:")
            self.print_line("Normal text")
            self.print_line("Bold text", bold=True)
            self.print_line("Underlined text", underline=True)
            self.print_line("Small font", font_size='small')
            self.print_line("Large font", font_size='large')
            
            self.print_separator('-', 32)
            self.print_line("Test completed successfully!", align='center', bold=True)
            self.print_separator('=', 32)
            
            # Cut paper
            self.send_command(self.LINE_FEED * 3)
            self.send_command(self.CUT_PAPER)
            
            print("Test print completed")
            return True
            
        except Exception as e:
            self.last_error = f"Test print failed: {str(e)}"
            print(self.last_error)
            raise Exception(self.last_error)
    
    def get_status(self):
        """Get printer status"""
        return {
            'connected': self.is_connected,
            'device': self.connected_device,
            'last_error': self.last_error
        }


class PrinterManager:
    """High-level printer management"""
    
    def __init__(self):
        self.printer = BluetoothPrinter()
        self.auto_connect_address = None
        self.print_queue = []
        self.is_printing = False
    
    def scan_and_connect(self):
        """Scan for printers and connect to first available"""
        devices = self.printer.scan_devices()
        
        if not devices:
            raise Exception("No printer devices found")
        
        # Try to connect to first printer
        for device in devices:
            if self.printer.connect(device['address']):
                self.auto_connect_address = device['address']
                return device
        
        raise Exception("Failed to connect to any printer")
    
    def connect_to_saved(self):
        """Connect to previously saved printer"""
        if self.auto_connect_address:
            return self.printer.connect(self.auto_connect_address)
        return False
    
    def print_receipt_async(self, receipt):
        """Print receipt asynchronously"""
        def print_worker():
            try:
                self.is_printing = True
                
                # Try to connect if not connected
                if not self.printer.is_connected:
                    if not self.connect_to_saved():
                        raise Exception("Printer not connected")
                
                # Print receipt
                self.printer.print_receipt(receipt)
                
            except Exception as e:
                print(f"Async print failed: {str(e)}")
                raise
            finally:
                self.is_printing = False
        
        # Start printing in background thread
        thread = threading.Thread(target=print_worker)
        thread.daemon = True
        thread.start()
        
        return thread
    
    def get_available_printers(self):
        """Get list of available printers"""
        return self.printer.scan_devices()
    
    def is_connected(self):
        """Check if printer is connected"""
        return self.printer.is_connected
    
    def get_last_error(self):
        """Get last error message"""
        return self.printer.last_error
    
    def disconnect(self):
        """Disconnect printer"""
        self.printer.disconnect()


# Global printer instance
printer_manager = PrinterManager()


def get_printer():
    """Get global printer instance"""
    return printer_manager