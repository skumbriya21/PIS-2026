from dataclasses import dataclass
from datetime import date, time

from src.domain.exceptions.domain_exception import DomainException


@dataclass(frozen=True)
class Slot:
    """
    Value Object: Временной слот бронирования.
    
    Иммутабельный, без ID, идентифицируется значениями.
    Длительность всегда ровно 1 час.
    """
    court_id: str
    date: date
    start_time: time
    end_time: time
    
    def __post_init__(self):
        if self.start_time >= self.end_time:
            raise DomainException(
                f"Время начала {self.start_time} должно быть меньше времени окончания {self.end_time}"
            )
        
        if self.start_time.minute != 0 or self.start_time.second != 0:
            raise DomainException("Слот должен начинаться с целого часа (00 минут)")
        
        if self.end_time.minute != 0 or self.end_time.second != 0:
            raise DomainException("Слот должен заканчиваться на целый час (00 минут)")
        
        start_minutes = self.start_time.hour * 60 + self.start_time.minute
        end_minutes = self.end_time.hour * 60 + self.end_time.minute
        duration = end_minutes - start_minutes
        
        if duration != 60:
            raise DomainException(f"Длительность слота должна быть ровно 60 минут, получено {duration}")
    
    def overlaps(self, other: 'Slot') -> bool:
        """Проверяет, пересекается ли этот слот с другим."""
        if self.court_id != other.court_id or self.date != other.date:
            return False
        
        return (
            self.start_time < other.end_time and 
            other.start_time < self.end_time
        )
    
    def __str__(self) -> str:
        return f"{self.court_id} {self.date} {self.start_time}-{self.end_time}"