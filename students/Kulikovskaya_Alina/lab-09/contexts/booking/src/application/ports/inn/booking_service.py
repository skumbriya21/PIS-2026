from abc import ABC, abstractmethod
from typing import Optional, List


class IBookingService(ABC):
    """Интерфейс сервиса бронирования."""
    
    @abstractmethod
    async def create_booking(
        self, user_id: str, court_id: str, slot_date: str,
        slot_time: str, amount: float
    ) -> str:
        """Создать бронирование."""
        pass
    
    @abstractmethod
    async def confirm_booking(self, booking_id: str, payment_id: str) -> None:
        """Подтвердить бронирование."""
        pass
    
    @abstractmethod
    async def cancel_booking(self, booking_id: str, reason: Optional[str]) -> None:
        """Отменить бронирование."""
        pass
    
    @abstractmethod
    async def get_booking(self, booking_id: str) -> Optional[dict]:
        """Получить бронирование."""
        pass
    
    @abstractmethod
    async def list_user_bookings(self, user_id: str) -> List[dict]:
        """Список бронирований пользователя."""
        pass