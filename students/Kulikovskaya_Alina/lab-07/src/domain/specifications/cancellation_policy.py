from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from domain.models.booking import Booking
from domain.models.value_objects.booking_status import BookingStatus


@dataclass(frozen=True)
class CancellationResult:
    """Результат проверки возможности отмены."""
    can_cancel: bool
    refund_amount: float  # Процент возврата (0-100)
    reason: Optional[str] = None


class CancellationPolicy:
    """
    Спецификация: политика отмены бронирования.
    
    Бизнес-правила:
    - > 24 часов до начала: полный возврат (100%)
    - 2-24 часа: возврат 50%
    - < 2 часов: отмена невозможна (0%)
    - CONFIRMED можно отменить, RESERVED тоже
    """
    
    FULL_REFUND_HOURS = 24
    PARTIAL_REFUND_HOURS = 2
    PARTIAL_REFUND_PERCENT = 50
    
    def can_cancel(self, booking: Booking, now: Optional[datetime] = None) -> CancellationResult:
        """
        Проверить, можно ли отменить бронирование.
        
        Args:
            booking: Бронирование для проверки
            now: Текущее время (для тестирования)
        
        Returns:
            CancellationResult с решением и % возврата
        """
        if now is None:
            now = datetime.now()
        
        # Нельзя отменить уже отменённое/истекшее
        if booking.status in (BookingStatus.CANCELLED, BookingStatus.EXPIRED):
            return CancellationResult(
                can_cancel=False,
                refund_amount=0,
                reason=f"Бронирование уже {booking.status.value}"
            )
        
        # Рассчитываем время до начала
        slot_datetime = datetime.combine(booking.slot.date, booking.slot.start_time)
        hours_until_start = (slot_datetime - now).total_seconds() / 3600
        
        if hours_until_start >= self.FULL_REFUND_HOURS:
            return CancellationResult(
                can_cancel=True,
                refund_amount=100,
                reason="Отмена более чем за 24 часа"
            )
        elif hours_until_start >= self.PARTIAL_REFUND_HOURS:
            return CancellationResult(
                can_cancel=True,
                refund_amount=self.PARTIAL_REFUND_PERCENT,
                reason=f"Отмена менее чем за {self.FULL_REFUND_HOURS} часов"
            )
        else:
            return CancellationResult(
                can_cancel=False,
                refund_amount=0,
                reason=f"Нельзя отменить менее чем за {self.PARTIAL_REFUND_HOURS} часа"
            )
    
    def calculate_refund(self, booking: Booking, now: Optional[datetime] = None) -> float:
        """Рассчитать сумму возврата."""
        result = self.can_cancel(booking, now)
        if not result.can_cancel or booking.total_amount is None:
            return 0.0
        
        return booking.total_amount.amount * (result.refund_amount / 100)