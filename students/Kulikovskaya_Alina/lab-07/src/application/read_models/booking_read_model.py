from dataclasses import dataclass
from datetime import date, time
from typing import Optional, List


@dataclass(frozen=True)
class BookingReadModel:
    """
    Денормализованная модель для чтения бронирований.
    
    Оптимизирована для быстрых запросов — все данные в одном месте.
    """
    # Identity
    booking_id: str
    
    # User info (денормализация — без JOIN)
    user_id: str
    user_email: str
    user_phone: Optional[str]
    
    # Court info (денормализация — без JOIN)
    court_id: str
    court_name: str
    court_type: str
    court_type_display: str
    
    # Slot info
    date: date
    start_time: time
    end_time: time
    
    # Status & Payment
    status: str
    status_display: str
    total_amount: float
    currency: str
    payment_status: Optional[str]
    
    # Metadata
    created_at: str
    confirmed_at: Optional[str]
    cancelled_at: Optional[str]
    created_by_admin: bool
    notes: Optional[str]
    
    # Computed fields (вычисляемые при создании read model)
    is_past: bool  # Прошедшее бронирование?
    hours_until_start: Optional[float]  # Часов до начала (для напоминаний)


@dataclass(frozen=True)
class BookingListView:
    """Упрощённая модель для списков."""
    booking_id: str
    court_name: str
    date: date
    start_time: time
    status: str
    total_amount: float
    can_cancel: bool  # Вычисляемое поле