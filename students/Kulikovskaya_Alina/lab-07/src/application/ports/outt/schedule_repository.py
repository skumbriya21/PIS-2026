from abc import ABC, abstractmethod
from datetime import date, time
from typing import List

from domain.models.value_objects.slot import Slot


class IScheduleRepository(ABC):
    """Исходящий порт: управление расписанием и доступностью."""
    
    @abstractmethod
    def is_available(self, court_id: str, date: date, 
                     start_time: time) -> bool:
        """Проверить, свободен ли слот."""
        pass
    
    @abstractmethod
    def lock_slot(self, court_id: str, date: date, start_time: time,
                  booking_id: str, ttl_minutes: int = 10) -> bool:
        """Заблокировать слот для бронирования."""
        pass
    
    @abstractmethod
    def unlock_slot(self, court_id: str, date: date, 
                    start_time: time) -> None:
        """Снять блокировку со слота."""
        pass
    
    @abstractmethod
    def confirm_slot(self, court_id: str, date: date, 
                     start_time: time) -> None:
        """Подтвердить бронирование слота."""
        pass
    
    @abstractmethod
    def get_available_slots(self, court_id: str, date: date) -> List[Slot]:
        """Получить список доступных слотов на дату."""
        pass