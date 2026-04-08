from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class BookingCreatedEvent:
    """Событие: создано новое бронирование."""
    booking_id: str
    user_id: str
    court_id: str
    slot_date: str
    slot_time: str
    amount: float
    currency: str
    created_by_admin: bool
    event_name: str = "booking.created"
    occurred_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass(frozen=True)
class BookingConfirmedEvent:
    """Событие: бронирование подтверждено."""
    booking_id: str
    user_id: str
    court_id: str
    payment_id: Optional[str]
    event_name: str = "booking.confirmed"
    occurred_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass(frozen=True)
class BookingCancelledEvent:
    """Событие: бронирование отменено."""
    booking_id: str
    user_id: str
    court_id: str
    reason: Optional[str]
    event_name: str = "booking.cancelled"
    occurred_at: str = field(default_factory=lambda: datetime.now().isoformat())