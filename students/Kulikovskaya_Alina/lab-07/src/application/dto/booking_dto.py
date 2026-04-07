from dataclasses import dataclass
from datetime import date, time
from typing import Optional, List


@dataclass(frozen=True)
class BookingDTO:
    """Полные данные бронирования для отображения."""
    id: str
    user_id: str
    court_id: str
    court_name: str
    court_type: str
    date: date
    start_time: time
    end_time: time
    status: str
    total_amount: float
    currency: str
    payment_id: Optional[str]
    created_by_admin: bool
    notes: Optional[str]
    created_at: str
    confirmed_at: Optional[str]
    cancelled_at: Optional[str]


@dataclass(frozen=True)
class BookingListItemDTO:
    """Краткие данные для списка бронирований."""
    id: str
    court_name: str
    court_type: str
    date: date
    start_time: time
    status: str
    total_amount: float