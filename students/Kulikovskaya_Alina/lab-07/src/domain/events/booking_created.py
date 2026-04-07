from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from src.domain.events.domain_event import DomainEvent
from src.domain.models.value_objects.slot import Slot


@dataclass(frozen=True)
class BookingCreatedEvent(DomainEvent):
    """Событие: создано новое бронирование."""
    
    booking_id: str
    user_id: str
    court_id: str
    slot: Slot
    total_amount: Optional[float] = None
    created_by_admin: bool = False
    
    def event_name(self) -> str:
        return "booking.created"