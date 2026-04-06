"""
Integration тесты для BookingService.
Тестируют координацию между доменом и инфраструктурой.
Используют InMemory репозитории (быстро, без Docker).
"""

import pytest
from datetime import date, time, timedelta

from application.services.booking_service_impl import BookingServiceImpl
from application.commands.create_booking_command import CreateBookingCommand
from application.commands.cancel_booking_command import CancelBookingCommand

from infrastructure.adapters.outt.in_memory_booking_repository import InMemoryBookingRepository
from infrastructure.adapters.outt.in_memory_court_repository import InMemoryCourtRepository
from infrastructure.adapters.outt.in_memory_schedule_repository import InMemoryScheduleRepository
from infrastructure.adapters.outt.mock_payment_gateway import MockPaymentGateway
from infrastructure.adapters.outt.mock_notification_service import MockNotificationService

from domain.models.value_objects.court_type import CourtType
from domain.models.value_objects.booking_status import BookingStatus
from domain.exceptions.domain_exception import DomainException


@pytest.fixture
def booking_service():
    """Фикстура с настроенным сервисом."""
    return BookingServiceImpl(
        booking_repository=InMemoryBookingRepository(),
        court_repository=InMemoryCourtRepository(),
        schedule_repository=InMemoryScheduleRepository(),
        payment_gateway=MockPaymentGateway(failure_rate=0),
        notification_service=MockNotificationService()
    )


class TestCreateBookingIntegration:
    """Интеграционные тесты создания бронирования."""
    
    def test_create_booking_success(self, booking_service):
        """Успешное создание бронирования."""
        tomorrow = date.today() + timedelta(days=1)
        
        command = CreateBookingCommand(
            user_id="user-123",
            court_id="court-bd-01",
            date=tomorrow,
            start_time=time(18, 0),
            end_time=time(19, 0),
            payment_method="online"
        )
        
        booking_id = booking_service.create_booking(command)
        
        assert booking_id is not None
        
        # Проверяем, что можно получить созданное бронирование
        booking = booking_service.get_booking(booking_id)
        assert booking is not None
        assert booking.status == BookingStatus.PENDING_PAYMENT.value
        assert booking.total_amount == 30.0  # 25 + 20% пик
    
    def test_create_booking_slot_already_taken(self, booking_service):
        """Попытка забронировать занятый слот."""
        tomorrow = date.today() + timedelta(days=1)
        
        # Первое бронирование
        command1 = CreateBookingCommand(
            user_id="user-123",
            court_id="court-bd-01",
            date=tomorrow,
            start_time=time(18, 0),
            end_time=time(19, 0),
            payment_method="online"
        )
        booking_service.create_booking(command1)
        
        # Второе бронирование на тот же слот
        command2 = CreateBookingCommand(
            user_id="user-456",
            court_id="court-bd-01",
            date=tomorrow,
            start_time=time(18, 0),
            end_time=time(19, 0),
            payment_method="online"
        )
        
        with pytest.raises(DomainException):
            booking_service.create_booking(command2)
    
    def test_create_booking_too_late(self, booking_service):
        """Бронирование менее чем за 30 минут."""
        today = date.today()
        now = datetime.now()
        start = (now + timedelta(minutes=10)).time()
        
        command = CreateBookingCommand(
            user_id="user-123",
            court_id="court-bd-01",
            date=today,
            start_time=start,
            end_time=time(start.hour + 1, start.minute),
            payment_method="online"
        )
        
        with pytest.raises(DomainException) as exc:
            booking_service.create_booking(command)
        
        assert "30 минут" in str(exc.value)


class TestCancelBookingIntegration:
    """Интеграционные тесты отмены."""
    
    def test_cancel_and_refund_full(self, booking_service):
        """Полный возврат при отмене > 24 часов."""
        # Создаём бронирование на послезавтра
        future_date = date.today() + timedelta(days=2)
        
        create_cmd = CreateBookingCommand(
            user_id="user-123",
            court_id="court-bd-01",
            date=future_date,
            start_time=time(18, 0),
            end_time=time(19, 0),
            payment_method="online"
        )
        booking_id = booking_service.create_booking(create_cmd)
        
        # Подтверждаем оплату
        booking_service.confirm_payment(booking_id, "PAY-TEST-123")
        
        # Отменяем
        cancel_cmd = CancelBookingCommand(
            booking_id=booking_id,
            user_id="user-123",
            reason="Планы изменились"
        )
        booking_service.cancel_booking(cancel_cmd)
        
        # Проверяем статус
        booking = booking_service.get_booking(booking_id)
        assert booking.status == BookingStatus.CANCELLED.value