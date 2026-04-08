from dataclasses import dataclass, field
from typing import Optional, List
from uuid import uuid4


@dataclass
class Court:
    """Площадка для игры."""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    court_type: str = ""  # volleyball, basketball, badminton, table_tennis
    description: Optional[str] = None
    is_active: bool = True
    hourly_rate: float = 0.0
    amenities: List[str] = field(default_factory=list)
    
    def deactivate(self) -> None:
        """Деактивировать площадку."""
        if not self.is_active:
            raise ValueError("Площадка уже деактивирована")
        self.is_active = False
    
    def activate(self) -> None:
        """Активировать площадку."""
        if self.is_active:
            raise ValueError("Площадка уже активна")
        self.is_active = True


@dataclass
class Slot:
    """Временной слот."""
    
    court_id: str = ""
    date: str = ""  # YYYY-MM-DD
    start_time: str = ""  # HH:MM
    end_time: str = ""  # HH:MM
    is_available: bool = True
    booking_id: Optional[str] = None
    
    def reserve(self, booking_id: str) -> None:
        """Зарезервировать слот."""
        if not self.is_available:
            raise ValueError("Слот уже занят")
        self.is_available = False
        self.booking_id = booking_id
    
    def release(self) -> None:
        """Освободить слот."""
        self.is_available = True
        self.booking_id = None