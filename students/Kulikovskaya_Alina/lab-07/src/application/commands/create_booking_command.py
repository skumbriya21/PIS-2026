from dataclasses import dataclass
from datetime import date, time
from typing import Optional


@dataclass(frozen=True)
class CreateBookingCommand:
    """DTO: Команда создания бронирования."""
    user_id: str
    court_id: str
    date: date
    start_time: time
    end_time: time
    payment_method: str = "online"
    notes: Optional[str] = None
    idempotency_key: Optional[str] = None