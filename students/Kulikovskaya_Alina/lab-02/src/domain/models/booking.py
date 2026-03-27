from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from src.domain.exceptions.domain_exception import DomainException
from src.domain.models.value_objects.slot import Slot
from src.domain.models.value_objects.booking_status import BookingStatus
from src.domain.models.value_objects.money import Money
from src.domain.events.booking_created import BookingCreatedEvent
from src.domain.events.booking_confirmed import BookingConfirmedEvent
from src.domain.events.booking_cancelled import BookingCancelledEvent
from src.domain.events.domain_event import DomainEvent


@dataclass
class Booking:
    """
    Aggregate Root: Бронирование спортивной площадки.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    court_id: str = ""
    slot: Optional[Slot] = None
    status: BookingStatus = BookingStatus.PENDING_PAYMENT
    total_amount: Optional[Money] = None
    payment_id: Optional[str] = None
    created_by_admin: bool = False
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    _events: List[DomainEvent] = field(default_factory=list, repr=False)
    
    def __post_init__(self):
        if not self.user_id:
            raise DomainException("user_id обязателен для бронирования")
        if not self.court_id:
            raise DomainException("court_id обязателен для бронирования")
        if self.slot is None:
            raise DomainException("slot обязателен для бронирования")
    
    def confirm(self, payment_id: Optional[str] = None) -> None:
        """Подтвердить бронирование после успешной оплаты."""
        if self.status not in (BookingStatus.PENDING_PAYMENT, BookingStatus.RESERVED):
            raise DomainException(
                f"Нельзя подтвердить бронирование в статусе {self.status.value}"
            )
        
        if payment_id:
            self.payment_id = payment_id
        
        old_status = self.status
        self.status = BookingStatus.CONFIRMED
        self.updated_at = datetime.now()
        
        self._add_event(BookingConfirmedEvent(
            booking_id=self.id,
            user_id=self.user_id,
            court_id=self.court_id,
            slot=self.slot,
            payment_id=self.payment_id,
            previous_status=old_status.value
        ))
    
    def cancel(self, reason: Optional[str] = None, cancelled_by: Optional[str] = None) -> None:
        """Отменить бронирование."""
        if self.status in (BookingStatus.CANCELLED, BookingStatus.EXPIRED):
            raise DomainException(f"Бронирование уже {self.status.value}")
        
        old_status = self.status
        self.status = BookingStatus.CANCELLED
        self.updated_at = datetime.now()
        self.notes = f"{self.notes or ''}; Cancelled: {reason or 'No reason'}".strip()
        
        self._add_event(BookingCancelledEvent(
            booking_id=self.id,
            user_id=self.user_id,
            court_id=self.court_id,
            slot=self.slot,
            reason=reason,
            cancelled_by=cancelled_by,
            previous_status=old_status.value
        ))
    
    def mark_as_reserved(self) -> None:
        """Перевести в статус RESERVED (для бронирования без online-оплаты)."""
        if self.status != BookingStatus.PENDING_PAYMENT:
            raise DomainException(f"Нельзя зарезервировать из статуса {self.status.value}")
        
        self.status = BookingStatus.RESERVED
        self.updated_at = datetime.now()
    
    def expire(self) -> None:
        """Истекло время на оплату."""
        if self.status not in (BookingStatus.PENDING_PAYMENT, BookingStatus.RESERVED):
            raise DomainException(f"Нельзя истекить статус {self.status.value}")
        
        self.status = BookingStatus.EXPIRED
        self.updated_at = datetime.now()
    
    def is_editable(self) -> bool:
        """Можно ли изменять бронирование."""
        return self.status in (BookingStatus.PENDING_PAYMENT, BookingStatus.RESERVED, BookingStatus.CONFIRMED)
    
    def is_confirmed(self) -> bool:
        return self.status == BookingStatus.CONFIRMED
    
    def _add_event(self, event: DomainEvent) -> None:
        self._events.append(event)
    
    def clear_events(self) -> None:
        self._events.clear()
    
    def get_events(self) -> List[DomainEvent]:
        return self._events.copy()
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Booking):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)