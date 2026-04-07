from datetime import datetime
from typing import Dict, Callable

from domain.events.domain_event import DomainEvent
from domain.events.booking_created import BookingCreatedEvent
from domain.events.booking_confirmed import BookingConfirmedEvent
from domain.events.booking_cancelled import BookingCancelledEvent

from application.read_models.booking_read_model import BookingReadModel
from application.ports.read.booking_read_repository import IBookingReadRepository
from application.ports.outt.user_repository import IUserRepository
from application.ports.outt.court_repository import ICourtRepository


class ProjectionService:
    """
    Сервис проекции: обновляет Read Models на основе Domain Events.
    
    Реализует Eventual Consistency — read models обновляются асинхронно.
    """
    
    def __init__(
        self,
        read_repository: IBookingReadRepository,
        user_repository: IUserRepository,
        court_repository: ICourtRepository
    ):
        self._read_repo = read_repository
        self._user_repo = user_repository
        self._court_repo = court_repository
        
        # Регистрация обработчиков событий
        self._handlers: Dict[str, Callable] = {
            "booking.created": self._on_booking_created,
            "booking.confirmed": self._on_booking_confirmed,
            "booking.cancelled": self._on_booking_cancelled,
        }
    
    def project(self, event: DomainEvent) -> None:
        """
        Обработать событие и обновить Read Model.
        
        Вызывается асинхронно (через message queue или event bus).
        """
        handler = self._handlers.get(event.event_name())
        if handler:
            handler(event)
    
    def _on_booking_created(self, event: BookingCreatedEvent) -> None:
        """Создание новой read model при бронировании."""
        # Получаем дополнительные данные
        user = self._user_repo.find_by_id(event.user_id)
        court = self._court_repo.find_by_id(event.court_id)
        
        if user is None or court is None:
            # Логируем ошибку, но не падаем (eventual consistency)
            return
        
        # Создаём денормализованную модель
        read_model = BookingReadModel(
            booking_id=event.booking_id,
            user_id=event.user_id,
            user_email=user.email,
            user_phone=getattr(user, 'phone', None),
            court_id=event.court_id,
            court_name=court.name,
            court_type=court.court_type.code,
            court_type_display=court.court_type.display_name,
            date=event.slot.date,
            start_time=event.slot.start_time,
            end_time=event.slot.end_time,
            status="pending_payment",
            status_display="Ожидает оплаты",
            total_amount=event.total_amount or 0,
            currency="BYN",
            payment_status=None,
            created_at=datetime.now().isoformat(),
            confirmed_at=None,
            cancelled_at=None,
            created_by_admin=event.created_by_admin,
            notes=None,
            is_past=False,
            hours_until_start=None  # Вычисляется динамически
        )
        
        self._read_repo.save(read_model)
    
    def _on_booking_confirmed(self, event: BookingConfirmedEvent) -> None:
        """Обновление статуса при подтверждении."""
        self._read_repo.update_status(
            booking_id=event.booking_id,
            status="confirmed",
            status_display="Подтверждено",
            confirmed_at=datetime.now().isoformat(),
            payment_status="success"
        )
    
    def _on_booking_cancelled(self, event: BookingCancelledEvent) -> None:
        """Обновление статуса при отмене."""
        self._read_repo.update_status(
            booking_id=event.booking_id,
            status="cancelled",
            status_display="Отменено",
            cancelled_at=datetime.now().isoformat()
        )