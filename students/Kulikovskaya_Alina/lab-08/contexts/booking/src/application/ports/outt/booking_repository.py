from abc import ABC, abstractmethod
from typing import Optional, List
from domain.models.booking import Booking


class IBookingRepository(ABC):
    """Интерфейс репозитория бронирований."""
    
    @abstractmethod
    async def save(self, booking: Booking) -> None:
        """Сохранить бронирование."""
        pass
    
    @abstractmethod
    async def find_by_id(self, booking_id: str) -> Optional[Booking]:
        """Найти по ID."""
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> List[Booking]:
        """Найти по пользователю."""
        pass
    
    @abstractmethod
    async def find_by_court_and_slot(
        self, court_id: str, slot_date: str, slot_time: str
    ) -> Optional[Booking]:
        """Найти по площадке и слоту."""
        pass