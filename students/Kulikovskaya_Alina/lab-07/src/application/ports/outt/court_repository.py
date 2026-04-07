from abc import ABC, abstractmethod
from typing import List, Optional

from domain.models.court import Court
from domain.models.value_objects.court_type import CourtType


class ICourtRepository(ABC):
    """Исходящий порт: хранение площадок."""
    
    @abstractmethod
    def save(self, court: Court) -> None:
        """Сохранить площадку."""
        pass
    
    @abstractmethod
    def find_by_id(self, court_id: str) -> Optional[Court]:
        """Найти площадку по ID."""
        pass
    
    @abstractmethod
    def find_by_type(self, court_type: CourtType) -> List[Court]:
        """Найти площадки по типу."""
        pass
    
    @abstractmethod
    def find_all_active(self) -> List[Court]:
        """Найти все активные площадки."""
        pass