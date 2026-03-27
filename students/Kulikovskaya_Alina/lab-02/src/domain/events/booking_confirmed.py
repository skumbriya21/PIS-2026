from dataclasses import dataclass
from typing import Optional

from src.domain.events.domain_event import DomainEvent
from src.domain.models.value_objects.slot import Slot


@dataclass(frozen=True)
class BookingConfirmedEvent(DomainEvent):
    """Событие: бронирование подтверждено."""
    
    booking_id: str
    user_id: str
    court_id: str
    slot: Slot
    payment_id: Optional[str]
    previous_status: str
    
    def event_name(self) -> str:
        return "booking.confirmed"