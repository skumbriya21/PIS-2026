from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent(ABC):
    """Базовый класс для всех доменных событий."""
    occurred_at: datetime = datetime.now()
    
    @abstractmethod
    def event_name(self) -> str:
        pass