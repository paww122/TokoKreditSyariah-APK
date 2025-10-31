#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Models untuk Toko Kredit Syariah
"""

from datetime import datetime, date
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Customer:
    """Model untuk data pelanggan"""
    id: Optional[int] = None
    name: str = ""
    address: str = ""
    phone: str = ""
    credit_limit: float = 0.0
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'credit_limit': self.credit_limit,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        customer = cls()
        customer.id = data.get('id')
        customer.name = data.get('name', '')
        customer.address = data.get('address', '')
        customer.phone = data.get('phone', '')
        customer.credit_limit = data.get('credit_limit', 0.0)
        
        created_at = data.get('created_at')
        if created_at:
            customer.created_at = datetime.fromisoformat(created_at)
        
        return customer

@dataclass
class Credit:
    """Model untuk data kredit"""
    id: Optional[int] = None
    customer_id: int = 0
    customer_name: str = ""
    item_name: str = ""
    total_price: float = 0.0
    daily_amount: float = 0.0
    total_days: int = 0
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = "active"  # active, completed, cancelled
    created_at: Optional[datetime] = None
    
    # Payment summary fields
    total_days_paid: int = 0
    remaining_days: int = 0
    total_amount_paid: float = 0.0
    remaining_amount: float = 0.0
    payment_count: int = 0
    last_payment_date: Optional[date] = None
    is_completed: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.start_date is None:
            self.start_date = date.today()
        if self.end_date is None and self.total_days > 0:
            from datetime import timedelta
            self.end_date = self.start_date + timedelta(days=self.total_days)
        
        # Calculate daily amount if not set
        if self.daily_amount == 0 and self.total_price > 0 and self.total_days > 0:
            # Ceiling division for daily amount
            self.daily_amount = int((self.total_price + self.total_days - 1) // self.total_days)
        
        # Update remaining days
        if self.total_days > 0:
            self.remaining_days = max(0, self.total_days - self.total_days_paid)
            self.remaining_amount = self.remaining_days * self.daily_amount
            self.is_completed = self.remaining_days == 0
    
    def calculate_payment_summary(self, payments: List['Payment']):
        """Calculate payment summary from payment list"""
        self.total_days_paid = sum(p.days_paid for p in payments)
        self.total_amount_paid = sum(p.amount for p in payments)
        self.payment_count = len(payments)
        
        if payments:
            self.last_payment_date = max(p.payment_date for p in payments)
        
        self.remaining_days = max(0, self.total_days - self.total_days_paid)
        self.remaining_amount = self.remaining_days * self.daily_amount
        self.is_completed = self.remaining_days == 0
        
        if self.is_completed:
            self.status = "completed"
    
    def get_daily_status(self, check_date: date = None) -> dict:
        """Get payment status for specific date"""
        if check_date is None:
            check_date = date.today()
        
        # This would need to be implemented with actual payment data
        return {
            'date': check_date,
            'due_amount': self.daily_amount,
            'paid_amount': 0.0,
            'is_paid': False,
            'is_overdue': False
        }
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'item_name': self.item_name,
            'total_price': self.total_price,
            'daily_amount': self.daily_amount,
            'total_days': self.total_days,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'total_days_paid': self.total_days_paid,
            'remaining_days': self.remaining_days,
            'total_amount_paid': self.total_amount_paid,
            'remaining_amount': self.remaining_amount,
            'payment_count': self.payment_count,
            'last_payment_date': self.last_payment_date.isoformat() if self.last_payment_date else None,
            'is_completed': self.is_completed
        }
    
    @classmethod
    def from_dict(cls, data):
        credit = cls()
        credit.id = data.get('id')
        credit.customer_id = data.get('customer_id', 0)
        credit.customer_name = data.get('customer_name', '')
        credit.item_name = data.get('item_name', '')
        credit.total_price = data.get('total_price', 0.0)
        credit.daily_amount = data.get('daily_amount', 0.0)
        credit.total_days = data.get('total_days', 0)
        credit.status = data.get('status', 'active')
        
        # Parse dates
        start_date = data.get('start_date')
        if start_date:
            credit.start_date = date.fromisoformat(start_date)
        
        end_date = data.get('end_date')
        if end_date:
            credit.end_date = date.fromisoformat(end_date)
        
        created_at = data.get('created_at')
        if created_at:
            credit.created_at = datetime.fromisoformat(created_at)
        
        last_payment_date = data.get('last_payment_date')
        if last_payment_date:
            credit.last_payment_date = date.fromisoformat(last_payment_date)
        
        # Payment summary
        credit.total_days_paid = data.get('total_days_paid', 0)
        credit.remaining_days = data.get('remaining_days', 0)
        credit.total_amount_paid = data.get('total_amount_paid', 0.0)
        credit.remaining_amount = data.get('remaining_amount', 0.0)
        credit.payment_count = data.get('payment_count', 0)
        credit.is_completed = data.get('is_completed', False)
        
        return credit

@dataclass
class Payment:
    """Model untuk data pembayaran"""
    id: Optional[int] = None
    credit_id: int = 0
    amount: float = 0.0
    payment_date: Optional[date] = None
    days_paid: int = 1
    remaining_days: int = 0
    notes: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.payment_date is None:
            self.payment_date = date.today()
    
    def calculate_days_paid(self, daily_amount: float) -> int:
        """Calculate how many days this payment covers"""
        if daily_amount <= 0:
            return 1
        
        if self.amount < daily_amount:
            # Partial payment still counts as 1 day
            return 1
        else:
            # Full or overpayment
            return int(self.amount // daily_amount)
    
    def is_overpayment(self, daily_amount: float) -> bool:
        """Check if this is an overpayment"""
        return self.amount > daily_amount
    
    def is_underpayment(self, daily_amount: float) -> bool:
        """Check if this is an underpayment"""
        return self.amount < daily_amount
    
    def get_excess_amount(self, daily_amount: float) -> float:
        """Get excess amount for overpayment"""
        if self.is_overpayment(daily_amount):
            return self.amount - (self.days_paid * daily_amount)
        return 0.0
    
    def to_dict(self):
        return {
            'id': self.id,
            'credit_id': self.credit_id,
            'amount': self.amount,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'days_paid': self.days_paid,
            'remaining_days': self.remaining_days,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data):
        payment = cls()
        payment.id = data.get('id')
        payment.credit_id = data.get('credit_id', 0)
        payment.amount = data.get('amount', 0.0)
        payment.days_paid = data.get('days_paid', 1)
        payment.remaining_days = data.get('remaining_days', 0)
        payment.notes = data.get('notes', '')
        
        # Parse dates
        payment_date = data.get('payment_date')
        if payment_date:
            payment.payment_date = date.fromisoformat(payment_date)
        
        created_at = data.get('created_at')
        if created_at:
            payment.created_at = datetime.fromisoformat(created_at)
        
        return payment

@dataclass
class DailyCollection:
    """Model untuk tagihan harian"""
    credit_id: int
    customer_name: str
    item_name: str
    daily_amount: float
    paid_today: bool = False
    total_days_paid: int = 0
    remaining_days: int = 0
    last_payment_amount: float = 0.0
    
    def get_status_color(self):
        """Get color for status display"""
        if self.paid_today:
            return (0.2, 0.8, 0.2, 1)  # Green
        else:
            return (0.8, 0.2, 0.2, 1)  # Red
    
    def get_status_text(self):
        """Get status text"""
        if self.paid_today:
            return "SUDAH"
        else:
            return "BELUM"
    
    def get_status_icon(self):
        """Get status icon"""
        if self.paid_today:
            return "✓"
        else:
            return "!"
    
    def to_dict(self):
        return {
            'credit_id': self.credit_id,
            'customer_name': self.customer_name,
            'item_name': self.item_name,
            'daily_amount': self.daily_amount,
            'paid_today': self.paid_today,
            'total_days_paid': self.total_days_paid,
            'remaining_days': self.remaining_days,
            'last_payment_amount': self.last_payment_amount
        }

@dataclass
class Receipt:
    """Model untuk struk pembayaran"""
    receipt_number: str
    date: date
    customer_name: str
    item_name: str
    total_price: float
    total_days: int
    daily_amount: float
    days_paid: int
    remaining_days: int
    payment_amount: float
    status: str
    notes: str = ""
    
    def __post_init__(self):
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
    
    def generate_receipt_number(self):
        """Generate unique receipt number"""
        from datetime import datetime
        now = datetime.now()
        return f"#{now.strftime('%Y-%m-%d')}-{now.strftime('%H%M%S')}"
    
    def format_currency(self, amount):
        """Format currency for Indonesian Rupiah"""
        return f"Rp {amount:,.0f}".replace(',', '.')
    
    def get_receipt_text(self):
        """Generate receipt text for thermal printer (32 chars width)"""
        lines = []
        
        # Header
        lines.append("=" * 32)
        lines.append("     TOKO ANDA - KREDIT")
        lines.append("=" * 32)
        
        # Receipt info
        lines.append(f"No: {self.receipt_number}")
        lines.append(f"Tgl: {self.date.strftime('%d %b %Y')}")
        lines.append("-" * 32)
        
        # Customer and item info
        lines.append(f"Nama : {self.customer_name[:22]}")
        lines.append(f"Barang: {self.item_name[:23]}")
        lines.append(f"Harga : {self.format_currency(self.total_price)}")
        lines.append(f"Cicilan: {self.total_days} hari")
        lines.append(f"Per Hari: {self.format_currency(self.daily_amount)}")
        lines.append("-" * 32)
        
        # Payment info
        lines.append(f"SUDAH SETOR : {self.days_paid}x")
        lines.append(f"SISA SETOR  : {self.remaining_days}x")
        lines.append(f"Hari Ini   : {self.format_currency(self.payment_amount)}")
        lines.append("-" * 32)
        
        # Status
        status_icon = "✓" if self.status == "SUDAH" else "!"
        lines.append(f"Status: {self.status} SETOR {status_icon}")
        lines.append("-" * 32)
        
        # Notes
        lines.append("Catatan: Tanpa DP. Tanpa denda.")
        
        # Special notes for overpayment
        if self.payment_amount > self.daily_amount:
            days_ahead = int(self.payment_amount // self.daily_amount) - 1
            if days_ahead > 0:
                lines.append(f"Lunas {days_ahead} hari ke depan!")
        
        lines.append("=" * 32)
        lines.append("Ttd: ___________")
        lines.append("")
        
        return "\n".join(lines)
    
    def to_dict(self):
        return {
            'receipt_number': self.receipt_number,
            'date': self.date.isoformat(),
            'customer_name': self.customer_name,
            'item_name': self.item_name,
            'total_price': self.total_price,
            'total_days': self.total_days,
            'daily_amount': self.daily_amount,
            'days_paid': self.days_paid,
            'remaining_days': self.remaining_days,
            'payment_amount': self.payment_amount,
            'status': self.status,
            'notes': self.notes
        }

# Utility functions
def format_currency(amount):
    """Format currency for display"""
    return f"Rp {amount:,.0f}".replace(',', '.')

def format_date(date_obj):
    """Format date for display"""
    if date_obj is None:
        return "-"
    
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj).date()
        except:
            return date_obj
    
    return date_obj.strftime('%d/%m/%Y')

def format_datetime(datetime_obj):
    """Format datetime for display"""
    if datetime_obj is None:
        return "-"
    
    if isinstance(datetime_obj, str):
        try:
            datetime_obj = datetime.fromisoformat(datetime_obj)
        except:
            return datetime_obj
    
    return datetime_obj.strftime('%d/%m/%Y %H:%M')