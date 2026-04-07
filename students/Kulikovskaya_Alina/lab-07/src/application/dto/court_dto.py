from dataclasses import dataclass
from datetime import date
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from application.dto.slot_dto import SlotDTO


@dataclass(frozen=True)
class CourtDTO:
    """Данные площадки."""
    id: str
    name: str
    court_type: str
    court_type_display: str
    hourly_rate: int
    is_active: bool
    description: str = ""


@dataclass(frozen=True)
class CourtAvailabilityDTO:
    """Доступность площадки на конкретную дату."""
    court: CourtDTO
    date: date
    available_slots: List['SlotDTO']  