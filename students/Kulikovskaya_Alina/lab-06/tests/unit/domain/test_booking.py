"""
Unit тесты для доменной модели Booking.
Изолированные, без зависимостей, быстрые.
"""

import pytest
from datetime import date, time, datetime, timedelta

from domain.models.booking import Booking
from domain.models.value_objects.slot import Slot
from domain.models.value_objects.money import Money
from domain.models.value_objects.booking_status import BookingStatus
from domain.exceptions.domain_exception import DomainException


class TestBookingCreation:
    """Тесты создания бронирования."""
    
    def test_create_valid_booking(self):
        """Успешное создание с валидными данными."""
        slot = Slot(
            court_id="court-001",
            date=date(2025, 3, 15),
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        
        booking = Booking(
            user_id="user-123",
            court_id="court-001",
            slot=slot,
            total_amount=Money(35.0)
        )
        
        assert booking.id is not None
        assert booking.status == BookingStatus.PENDING_PAYMENT
        assert booking.user_id == "user-123"
        assert len(booking.get_events()) == 1  # BookingCreatedEvent
    
    def test_create_booking_without_user_id_fails(self):
        """Нельзя создать без user_id."""
        slot = Slot(
            court_id="court-001",
            date=date(2025, 3, 15),
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        
        with pytest.raises(DomainException) as exc:
            Booking(
                user_id="",
                court_id="court-001",
                slot=slot,
                total_amount=Money(35.0)
            )
        
        assert "user_id обязателен" in str(exc.value)
    
    def test_create_booking_without_slot_fails(self):
        """Нельзя создать без слота."""
        with pytest.raises(DomainException) as exc:
            Booking(
                user_id="user-123",
                court_id="court-001",
                slot=None,
                total_amount=Money(35.0)
            )
        
        assert "slot обязателен" in str(exc.value)


class TestBookingConfirmation:
    """Тесты подтверждения бронирования."""
    
    def test_confirm_pending_payment_booking(self):
        """Подтверждение из статуса PENDING_PAYMENT."""
        slot = Slot(
            court_id="court-001",
            date=date(2025, 3, 15),
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        booking = Booking(
            user_id="user-123",
            court_id="court-001",
            slot=slot,
            total_amount=Money(35.0)
        )
        
        booking.confirm(payment_id="PAY-123")
        
        assert booking.status == BookingStatus.CONFIRMED
        assert booking.payment_id == "PAY-123"
        assert booking.confirmed_at is not None
        assert len(booking.get_events()) == 2  # Created + Confirmed
    
    def test_confirm_reserved_booking(self):
        """Подтверждение из статуса RESERVED."""
        slot = Slot(
            court_id="court-001",
            date=date(2025, 3, 15),
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        booking = Booking(
            user_id="user-123",
            court_id="court-001",
            slot=slot,
            status=BookingStatus.RESERVED,
            total_amount=Money(35.0)
        )
        
        booking.confirm(payment_id="PAY-456")
        
        assert booking.status == BookingStatus.CONFIRMED
    
    def test_confirm_already_confirmed_fails(self):
        """Нельзя подтвердить уже подтверждённое."""
        slot = Slot(
            court_id="court-001",
            date=date(2025, 3, 15),
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        booking = Booking(
            user_id="user-123",
            court_id="court-001",
            slot=slot,
            status=BookingStatus.CONFIRMED,
            total_amount=Money(35.0)
        )
        
        with pytest.raises(DomainException) as exc:
            booking.confirm()
        
        assert "Нельзя подтвердить" in str(exc.value)


class TestBookingCancellation:
    """Тесты отмены бронирования."""
    
    def test_cancel_pending_booking(self):
        """Отмена в статусе PENDING_PAYMENT."""
        slot = Slot(
            court_id="court-001",
            date=date(2025, 3, 15),
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        booking = Booking(
            user_id="user-123",
            court_id="court-001",
            slot=slot,
            total_amount=Money(35.0)
        )
        
        booking.cancel(reason="Планы изменились")
        
        assert booking.status == BookingStatus.CANCELLED
        assert booking.cancelled_at is not None
        assert "Планы изменились" in booking.notes
        assert len(booking.get_events()) == 2  # Created + Cancelled
    
    def test_cancel_already_cancelled_fails(self):
        """Нельзя отменить уже отменённое."""
        slot = Slot(
            court_id="court-001",
            date=date(2025, 3, 15),
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        booking = Booking(
            user_id="user-123",
            court_id="court-001",
            slot=slot,
            status=BookingStatus.CANCELLED,
            total_amount=Money(35.0)
        )
        
        with pytest.raises(DomainException) as exc:
            booking.cancel()
        
        assert "уже cancelled" in str(exc.value)


class TestBookingEquality:
    """Тесты сравнения бронирований."""
    
    def test_same_id_are_equal(self):
        """Бронирования с одинаковым ID равны."""
        slot = Slot(
            court_id="court-001",
            date=date(2025, 3, 15),
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        booking1 = Booking(
            id="same-id",
            user_id="user-123",
            court_id="court-001",
            slot=slot,
            total_amount=Money(35.0)
        )
        booking2 = Booking(
            id="same-id",
            user_id="user-456",  # Другой пользователь!
            court_id="court-002",  # Другая площадка!
            slot=slot,
            total_amount=Money(50.0)
        )
        
        assert booking1 == booking2  # Равны по ID
        assert hash(booking1) == hash(booking2)
    
    def test_different_id_are_not_equal(self):
        """Бронирования с разным ID не равны."""
        slot = Slot(
            court_id="court-001",
            date=date(2025, 3, 15),
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        booking1 = Booking(
            user_id="user-123",
            court_id="court-001",
            slot=slot,
            total_amount=Money(35.0)
        )
        booking2 = Booking(
            user_id="user-123",
            court_id="court-001",
            slot=slot,
            total_amount=Money(35.0)
        )
        
        assert booking1 != booking2  # Разные ID (uuid)