from abc import ABC, abstractmethod


class ICourtClient(ABC):
    """Клиент для Court Context."""
    
    @abstractmethod
    async def check_availability(self, court_id: str, slot_date: str, slot_time: str) -> bool:
        """Проверить доступность площадки."""
        pass
    
    @abstractmethod
    async def get_court_details(self, court_id: str) -> dict:
        """Получить информацию о площадке."""
        pass
    
    @abstractmethod
    async def reserve_slot(self, court_id: str, slot_date: str, slot_time: str) -> bool:
        """Зарезервировать слот."""
        pass
    
    @abstractmethod
    async def release_slot(self, court_id: str, slot_date: str, slot_time: str) -> bool:
        """Освободить слот."""
        pass