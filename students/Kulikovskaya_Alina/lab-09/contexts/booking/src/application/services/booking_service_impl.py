from typing import Optional, List

from domain.models.booking import Booking
from domain.events.booking_events import (
    BookingCreatedEvent, BookingConfirmedEvent, BookingCancelledEvent
)

from application.ports.inn.booking_service import IBookingService
from application.ports.outt.booking_repository import IBookingRepository
from application.ports.outt.event_publisher import IEventPublisher
from application.ports.outt.court_client import ICourtClient


class BookingServiceImpl(IBookingService):
    """Реализация сервиса бронирования."""
    
    def __init__(
        self,
        repository: IBookingRepository,
        event_publisher: IEventPublisher,
        court_client: ICourtClient
    ):
        self._repo = repository
        self._events = event_publisher
        self._court = court_client
    
    async def create_booking(
        self, user_id: str, court_id: str, slot_date: str,
        slot_time: str, amount: float
    ) -> str:
        """Создать бронирование."""
        # Проверяем доступность через Court Context
        is_available = await self._court.check_availability(
            court_id, slot_date, slot_time
        )
        if not is_available:
            raise ValueError("Слот недоступен")
        
        # Резервируем слот
        reserved = await self._court.reserve_slot(court_id, slot_date, slot_time)
        if not reserved:
            raise ValueError("Не удалось зарезервировать слот")
        
        # Создаём бронирование
        booking = Booking(
            user_id=user_id,
            court_id=court_id,
            slot_date=slot_date,
            slot_time=slot_time,
            total_amount=amount
        )
        
        await self._repo.save(booking)
        
        # Публикуем событие
        await self._events.publish(BookingCreatedEvent(
            booking_id=booking.id,
            user_id=user_id,
            court_id=court_id,
            slot_date=slot_date,
            slot_time=slot_time,
            amount=amount,
            currency="BYN",
            created_by_admin=False
        ))
        
        return booking.id
    
    async def confirm_booking(self, booking_id: str, payment_id: str) -> None:
        """Подтвердить бронирование."""
        booking = await self._repo.find_by_id(booking_id)
        if not booking:
            raise ValueError("Бронирование не найдено")
        
        booking.confirm(payment_id)
        await self._repo.save(booking)
        
        await self._events.publish(BookingConfirmedEvent(
            booking_id=booking.id,
            user_id=booking.user_id,
            court_id=booking.court_id,
            payment_id=payment_id
        ))
    
    async def cancel_booking(self, booking_id: str, reason: Optional[str]) -> None:
        """Отменить бронирование."""
        booking = await self._repo.find_by_id(booking_id)
        if not booking:
            raise ValueError("Бронирование не найдено")
        
        # Освобождаем слот
        await self._court.release_slot(
            booking.court_id, booking.slot_date, booking.slot_time
        )
        
        booking.cancel(reason)
        await self._repo.save(booking)
        
        await self._events.publish(BookingCancelledEvent(
            booking_id=booking.id,
            user_id=booking.user_id,
            court_id=booking.court_id,
            reason=reason
        ))
    
    async def get_booking(self, booking_id: str) -> Optional[dict]:
        """Получить бронирование."""
        booking = await self._repo.find_by_id(booking_id)
        return booking.to_dict() if booking else None
    
    async def list_user_bookings(self, user_id: str) -> List[dict]:
        """Список бронирований пользователя."""
        bookings = await self._repo.find_by_user_id(user_id)
        return [b.to_dict() for b in bookings]