from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date, time

from domain.models.booking import Booking


class IBookingRepository(ABC):
    """Исходящий порт: хранение и загрузка бронирований."""
    
    @abstractmethod
    def save(self, booking: Booking) -> None:
        """Сохранить или обновить бронирование."""
        pass
    
    @abstractmethod
    def find_by_id(self, booking_id: str) -> Optional[Booking]:
        """Найти бронирование по ID."""
        pass
    
    @abstractmethod
    def find_by_user_id(self, user_id: str) -> List[Booking]:
        """Найти все бронирования пользователя."""
        pass
    
    @abstractmethod
    def find_by_court_and_date(self, court_id: str, date: date) -> List[Booking]:
        """Найти бронирования площадки на конкретную дату."""
        pass
    
    @abstractmethod
    def find_active_by_slot(self, court_id: str, date: date, 
                           start_time: time) -> Optional[Booking]:
        """Найти активное бронирование на конкретный слот."""
        pass