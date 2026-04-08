from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent:
    """Базовый класс доменного события."""
    
    event_name: str
    occurred_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        """Сериализация."""
        return {
            "event_type": self.event_name,
            "occurred_at": self.occurred_at,
            "payload": self.__dict__
        }