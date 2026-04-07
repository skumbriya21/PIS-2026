from datetime import date, time
from typing import Optional

from domain.models.booking import Booking
from domain.models.value_objects.slot import Slot
from domain.models.value_objects.money import Money
from domain.models.value_objects.booking_status import BookingStatus
from domain.services.pricing_service import PricingService
from domain.exceptions.domain_exception import DomainException


class BookingFactory:
    """
    Фабрика: создание бронирований с валидацией.
    
    Инкапсулирует сложную логику создания агрегата.
    """
    
    def __init__(self, pricing_service: Optional[PricingService] = None):
        self._pricing = pricing_service or PricingService()
    
    def create_online_booking(self, user_id: str, court_id: str,
                              slot_date: date, start_time: time,
                              court_type, notes: Optional[str] = None) -> Booking:
        """
        Создать бронирование через сайт (требует оплаты).
        
        Args:
            user_id: ID пользователя
            court_id: ID площадки
            slot_date: Дата
            start_time: Время начала
            court_type: Тип площадки (для расчёта цены)
            notes: Комментарий
        
        Returns:
            Booking со статусом PENDING_PAYMENT
        """
        end_time = time(start_time.hour + 1, 0)
        
        slot = Slot(
            court_id=court_id,
            date=slot_date,
            start_time=start_time,
            end_time=end_time
        )
        
        # Рассчитываем стоимость
        total_amount = self._pricing.calculate_price(
            court_type, slot_date, start_time
        )
        
        booking = Booking(
            user_id=user_id,
            court_id=court_id,
            slot=slot,
            status=BookingStatus.PENDING_PAYMENT,
            total_amount=total_amount,
            created_by_admin=False,
            notes=notes
        )
        
        return booking
    
    def create_phone_booking(self, admin_id: str, court_id: str,
                             slot_date: date, start_time: time,
                             court_type, customer_name: str,
                             customer_phone: str,
                             notes: Optional[str] = None) -> Booking:
        """
        Создать бронирование администратором по телефону.
        
        Особенности:
        - Сразу CONFIRMED (без online-оплаты)
        - Оплата на месте
        - Сохраняем контакт клиента в notes
        """
        end_time = time(start_time.hour + 1, 0)
        
        slot = Slot(
            court_id=court_id,
            date=slot_date,
            start_time=start_time,
            end_time=end_time
        )
        
        total_amount = self._pricing.calculate_price(
            court_type, slot_date, start_time
        )
        
        full_notes = f"Клиент: {customer_name}, Тел: {customer_phone}"
        if notes:
            full_notes += f"; {notes}"
        
        booking = Booking(
            user_id=admin_id,  # Временно, потом создаём пользователя
            court_id=court_id,
            slot=slot,
            status=BookingStatus.CONFIRMED,  # Сразу подтверждено!
            total_amount=total_amount,
            created_by_admin=True,
            notes=full_notes
        )
        
        return booking
    
    def create_reserved_booking(self, user_id: str, court_id: str,
                                slot_date: date, start_time: time,
                                court_type, notes: Optional[str] = None) -> Booking:
        """
        Создать бронирование с резервированием (оплата на месте).
        
        Статус RESERVED — слот не блокируется жёстко,
        но есть приоритет при оплате за 30 минут.
        """
        end_time = time(start_time.hour + 1, 0)
        
        slot = Slot(
            court_id=court_id,
            date=slot_date,
            start_time=start_time,
            end_time=end_time
        )
        
        total_amount = self._pricing.calculate_price(
            court_type, slot_date, start_time
        )
        
        booking = Booking(
            user_id=user_id,
            court_id=court_id,
            slot=slot,
            status=BookingStatus.RESERVED,
            total_amount=total_amount,
            created_by_admin=False,
            notes=notes
        )
        
        return booking