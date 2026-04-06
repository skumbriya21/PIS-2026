from dataclasses import dataclass, field
from typing import Optional

from src.domain.models.value_objects.court_type import CourtType


@dataclass
class Court:
    """
    Entity: Спортивная площадка/корт/стол.
    """
    id: str
    name: str
    court_type: CourtType
    description: Optional[str] = None
    is_active: bool = True
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Название площадки обязательно")
    
    def deactivate(self) -> None:
        self.is_active = False
    
    def activate(self) -> None:
        self.is_active = True
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Court):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)