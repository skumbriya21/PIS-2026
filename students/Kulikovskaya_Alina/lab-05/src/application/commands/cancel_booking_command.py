from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CancelBookingCommand:
    """DTO: Команда отмены бронирования."""
    booking_id: str
    user_id: str
    reason: Optional[str] = None
    force: bool = False