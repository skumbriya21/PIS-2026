from abc import ABC, abstractmethod
from typing import List, Optional

from application.commands.create_booking_command import CreateBookingCommand
from application.commands.cancel_booking_command import CancelBookingCommand
from domain.models.booking import Booking


class IBookingService(ABC):
    # Входящий порт: сервис управления бронированиями.
    
    @abstractmethod
    def create_booking(self, command: CreateBookingCommand) -> str:
        # Создать новое бронирование.
        pass
    
    @abstractmethod
    def cancel_booking(self, command: CancelBookingCommand) -> None:
        # Отменить существующее бронирование.
        pass
    
    @abstractmethod
    def get_booking(self, booking_id: str) -> Optional[Booking]:
        # Получить бронирование по ID.
        pass
    
    @abstractmethod
    def list_user_bookings(self, user_id: str) -> List[Booking]:
        # Получить список бронирований пользователя.
        pass
    
    @abstractmethod
    def confirm_payment(self, booking_id: str, payment_id: str) -> None:
        # Подтвердить оплату бронирования.
        pass