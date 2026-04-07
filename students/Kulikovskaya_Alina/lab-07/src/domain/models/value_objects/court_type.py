from enum import Enum


class CourtType(Enum):
    """Типы спортивных площадок в манеже."""
    
    VOLLEYBALL = ("volleyball", "Волейбольная площадка", 25)
    BASKETBALL = ("basketball", "Баскетбольная площадка", 25)
    BADMINTON = ("badminton", "Бадминтонный корт", 17)
    TABLE_TENNIS = ("table_tennis", "Стол для настольного тенниса", 4)
    
    def __init__(self, code: str, display_name: str, hourly_rate: int):
        self.code = code
        self.display_name = display_name
        self.hourly_rate = hourly_rate
    
    @classmethod
    def from_code(cls, code: str) -> 'CourtType':
        for court_type in cls:
            if court_type.code == code:
                return court_type
        raise ValueError(f"Unknown court type code: {code}")