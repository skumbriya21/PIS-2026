from typing import Dict, List, Optional

from domain.models.court import Court
from domain.models.value_objects.court_type import CourtType
from application.ports.outt.court_repository import ICourtRepository


class InMemoryCourtRepository(ICourtRepository):
    """InMemory реализация для тестирования."""
    
    def __init__(self):
        self._storage: Dict[str, Court] = {}
        self._init_default_courts()
    
    def _init_default_courts(self):
        """Инициализация площадками по умолчанию."""
        courts = [
            Court("court-vb-01", "Волейбольная площадка #1", CourtType.VOLLEYBALL),
            Court("court-bb-01", "Баскетбольная площадка #1", CourtType.BASKETBALL),
            *[Court(f"court-bd-{i:02d}", f"Бадминтонный корт #{i}", CourtType.BADMINTON) 
              for i in range(1, 9)],
            *[Court(f"court-tt-{i:02d}", f"Стол для настольного тенниса #{i}", CourtType.TABLE_TENNIS) 
              for i in range(1, 7)],
        ]
        for court in courts:
            self.save(court)
    
    def save(self, court: Court) -> None:
        self._storage[court.id] = court
    
    def find_by_id(self, court_id: str) -> Optional[Court]:
        return self._storage.get(court_id)
    
    def find_by_type(self, court_type: CourtType) -> List[Court]:
        return [c for c in self._storage.values() if c.court_type == court_type]
    
    def find_all_active(self) -> List[Court]:
        return [c for c in self._storage.values() if c.is_active]