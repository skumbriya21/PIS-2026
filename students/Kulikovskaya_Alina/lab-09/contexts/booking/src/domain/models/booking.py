from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import uuid4


@dataclass
class Booking:
    """Aggregate Root: Бронирование площадки."""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    court_id: str = ""
    slot_date: str = ""  # YYYY-MM-DD
    slot_time: str = ""  # HH:MM
    status: str = "pending_payment"  # pending_payment, confirmed, cancelled, expired
    total_amount: float = 0.0
    currency: str = "BYN"
    payment_id: Optional[str] = None
    created_by_admin: bool = False
    notes: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    confirmed_at: Optional[str] = None
    cancelled_at: Optional[str] = None
    
    def confirm(self, payment_id: Optional[str] = None) -> None:
        """Подтвердить бронирование."""
        if self.status not in ("pending_payment", "reserved"):
            raise ValueError(f"Нельзя подтвердить статус {self.status}")
        
        self.status = "confirmed"
        self.payment_id = payment_id
        self.confirmed_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """Отменить бронирование."""
        if self.status in ("cancelled", "expired"):
            raise ValueError(f"Бронирование уже {self.status}")
        
        self.status = "cancelled"
        self.cancelled_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        
        if reason:
            self.notes = f"{self.notes or ''}; Отмена: {reason}".strip()
    
    def expire(self) -> None:
        """Истечение времени на оплату."""
        if self.status not in ("pending_payment", "reserved"):
            raise ValueError(f"Нельзя истекить статус {self.status}")
        
        self.status = "expired"
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        """Сериализация в словарь."""
        return {
            "booking_id": self.id,
            "user_id": self.user_id,
            "court_id": self.court_id,
            "slot_date": self.slot_date,
            "slot_time": self.slot_time,
            "status": self.status,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "payment_id": self.payment_id,
            "created_by_admin": self.created_by_admin,
            "notes": self.notes,
            "created_at": self.created_at,
            "confirmed_at": self.confirmed_at,
            "cancelled_at": self.cancelled_at,
        }