from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import uuid4

from domain.exceptions.domain_exception import DomainException
from domain.models.value_objects.slot import Slot
from domain.models.value_objects.booking_status import BookingStatus
from domain.models.value_objects.money import Money
from domain.events.booking_created import BookingCreatedEvent
from domain.events.booking_confirmed import BookingConfirmedEvent
from domain.events.booking_cancelled import BookingCancelledEvent
from domain.events.domain_event import DomainEvent


@dataclass
class Booking:
    """
    Aggregate Root: Бронирование спортивной площадки.
    
    Богатая модель с бизнес-логикой внутри.
    """
    # Identity
    id: str = field(default_factory=lambda: str(uuid4()))
    
    # References
    user_id: str = ""
    court_id: str = ""
    
    # Value Objects
    slot: Optional[Slot] = None
    status: BookingStatus = BookingStatus.PENDING_PAYMENT
    total_amount: Optional[Money] = None
    
    # Optional
    payment_id: Optional[str] = None
    created_by_admin: bool = False
    notes: Optional[str] = None
    
    # Audit
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Domain Events
    _events: List[DomainEvent] = field(default_factory=list, repr=False)
    
    # Инварианты при создании
    
    def __post_init__(self):
        if not self.user_id:
            raise DomainException("user_id обязателен для бронирования")
        if not self.court_id:
            raise DomainException("court_id обязателен для бронирования")
        if self.slot is None:
            raise DomainException("slot обязателен для бронирования")
        
        # Публикация события создания
        self._add_event(BookingCreatedEvent(
            booking_id=self.id,
            user_id=self.user_id,
            court_id=self.court_id,
            slot=self.slot,
            total_amount=self.total_amount.amount if self.total_amount else None,
            created_by_admin=self.created_by_admin
        ))
    
    # Бизнес-операции с инвариантами
    
    def confirm(self, payment_id: Optional[str] = None,
                confirmed_by: Optional[str] = None) -> None:
        """
        Подтвердить бронирование после успешной оплаты.
        
        Инварианты:
        - Можно подтвердить только из PENDING_PAYMENT или RESERVED
        - Устанавливается confirmed_at
        - Генерируется BookingConfirmedEvent
        """
        allowed_sources = (BookingStatus.PENDING_PAYMENT, BookingStatus.RESERVED)
        if self.status not in allowed_sources:
            raise DomainException(
                f"Нельзя подтвердить бронирование в статусе {self.status.value}. "
                f"Допустимые: {[s.value for s in allowed_sources]}"
            )
        
        if payment_id:
            self.payment_id = payment_id
        
        old_status = self.status
        self.status = BookingStatus.CONFIRMED
        self.confirmed_at = datetime.now()
        self.updated_at = datetime.now()
        
        self._add_event(BookingConfirmedEvent(
            booking_id=self.id,
            user_id=self.user_id,
            court_id=self.court_id,
            slot=self.slot,
            payment_id=self.payment_id,
            previous_status=old_status.value
        ))
    
    def cancel(self, reason: Optional[str] = None, 
               cancelled_by: Optional[str] = None,
               force: bool = False) -> None:
        """
        Отменить бронирование.
        
        Инварианты:
        - Нельзя отменить уже отменённое/истекшее
        - force=True позволяет админу отменить в любое время
        - Устанавливается cancelled_at
        """
        if self.status in (BookingStatus.CANCELLED, BookingStatus.EXPIRED):
            raise DomainException(f"Бронирование уже {self.status.value}")
        
        old_status = self.status
        self.status = BookingStatus.CANCELLED
        self.cancelled_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Добавляем информацию об отмене в notes
        cancel_info = f"Отменено: {cancelled_by or 'Unknown'}"
        if reason:
            cancel_info += f", Причина: {reason}"
        self.notes = f"{self.notes or ''}; {cancel_info}".strip()
        
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
            raise DomainException(
                f"Нельзя зарезервировать из статуса {self.status.value}"
            )
        
        self.status = BookingStatus.RESERVED
        self.updated_at = datetime.now()
    
    def expire(self, reason: str = "Таймаут оплаты") -> None:
        """Истекло время на оплату."""
        if self.status not in (BookingStatus.PENDING_PAYMENT, BookingStatus.RESERVED):
            raise DomainException(f"Нельзя истекить статус {self.status.value}")
        
        old_status = self.status
        self.status = BookingStatus.EXPIRED
        self.updated_at = datetime.now()
        self.notes = f"{self.notes or ''}; Expired: {reason}".strip()
    
    # Query methods (без изменения состояния)
    
    def is_editable(self) -> bool:
        """Можно ли изменять бронирование."""
        return self.status in (
            BookingStatus.PENDING_PAYMENT, 
            BookingStatus.RESERVED, 
            BookingStatus.CONFIRMED
        )
    
    def is_confirmed(self) -> bool:
        return self.status == BookingStatus.CONFIRMED
    
    def is_pending_payment(self) -> bool:
        return self.status == BookingStatus.PENDING_PAYMENT
    
    def is_cancelled(self) -> bool:
        return self.status == BookingStatus.CANCELLED
    
    def hours_until_start(self, now: Optional[datetime] = None) -> float:
        """Часов до начала бронирования."""
        if now is None:
            now = datetime.now()
        
        slot_datetime = datetime.combine(self.slot.date, self.slot.start_time)
        delta = slot_datetime - now
        return delta.total_seconds() / 3600
    
    def can_be_paid(self) -> bool:
        """Можно ли оплатить (не истёк ли срок)."""
        return self.status in (BookingStatus.PENDING_PAYMENT, BookingStatus.RESERVED)
    
    # Domain Events management
    
    def _add_event(self, event: DomainEvent) -> None:
        self._events.append(event)
    
    def clear_events(self) -> None:
        self._events.clear()
    
    def get_events(self) -> List[DomainEvent]:
        return self._events.copy()
    
    def has_unpublished_events(self) -> bool:
        return len(self._events) > 0
    
    # Equality
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Booking):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __repr__(self) -> str:
        return (
            f"Booking(id={self.id[:8]}..., "
            f"status={self.status.value}, "
            f"slot={self.slot})"
        )