from enum import Enum


class BookingStatus(Enum):
    """
    Статусы бронирования и допустимые переходы.
    """
    
    PENDING_PAYMENT = "pending_payment"
    RESERVED = "reserved"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    
    def can_transition_to(self, new_status: 'BookingStatus') -> bool:
        """Проверяет допустимость перехода статуса."""
        allowed_transitions = {
            BookingStatus.PENDING_PAYMENT: [
                BookingStatus.CONFIRMED,
                BookingStatus.CANCELLED,
                BookingStatus.EXPIRED
            ],
            BookingStatus.RESERVED: [
                BookingStatus.CONFIRMED,
                BookingStatus.CANCELLED,
                BookingStatus.EXPIRED
            ],
            BookingStatus.CONFIRMED: [
                BookingStatus.CANCELLED
            ],
            BookingStatus.CANCELLED: [],
            BookingStatus.EXPIRED: []
        }
        return new_status in allowed_transitions.get(self, [])