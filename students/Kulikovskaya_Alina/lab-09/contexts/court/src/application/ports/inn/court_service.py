from abc import ABC, abstractmethod
from typing import List, Optional


class ICourtService(ABC):
    """Интерфейс сервиса площадок."""
    
    @abstractmethod
    async def get_court(self, court_id: str) -> Optional[dict]:
        """Получить площадку."""
        pass
    
    @abstractmethod
    async def list_courts(self, court_type: Optional[str] = None) -> List[dict]:
        """Список площадок."""
        pass
    
    @abstractmethod
    async def check_availability(
        self, court_id: str, date: str, start_time: str
    ) -> bool:
        """Проверить доступность."""
        pass
    
    @abstractmethod
    async def reserve_slot(
        self, court_id: str, date: str, start_time: str, booking_id: str
    ) -> bool:
        """Зарезервировать слот."""
        pass
    
    @abstractmethod
    async def release_slot(self, court_id: str, date: str, start_time: str) -> bool:
        """Освободить слот."""
        pass