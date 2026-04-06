from abc import ABC, abstractmethod
from typing import List, Optional

from application.commands.create_booking_command import CreateBookingCommand
from domain.models.booking import Booking


class IAdminService(ABC):
    """Входящий порт: сервис для администраторов."""
    
    @abstractmethod
    def create_phone_booking(self, command: CreateBookingCommand, 
                            customer_name: str, customer_phone: str) -> str:
        """Создать бронирование по телефону (администратором)."""
        pass
    
    @abstractmethod
    def cancel_any_booking(self, booking_id: str, reason: str) -> None:
        """Отменить любое бронирование (даже без ограничений по времени)."""
        pass
    
    @abstractmethod
    def get_all_bookings(self, date: Optional[str] = None) -> List[Booking]:
        """Получить все бронирования (с фильтром по дате)."""
        pass
    
    @abstractmethod
    def block_slot(self, court_id: str, date: str, start_time: str, 
                   reason: str) -> None:
        """Заблокировать слот для технического обслуживания."""
        pass