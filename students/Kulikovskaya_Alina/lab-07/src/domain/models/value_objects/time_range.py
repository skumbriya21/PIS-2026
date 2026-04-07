from dataclasses import dataclass
from datetime import time, timedelta

from domain.exceptions.domain_exception import DomainException


@dataclass(frozen=True)
class TimeRange:
    """
    Value Object: Временной диапазон.
    
    Используется для слотов, рабочих часов, ограничений.
    """
    start: time
    end: time
    
    def __post_init__(self):
        if self.start >= self.end:
            raise DomainException(f"Начало {self.start} должно быть раньше конца {self.end}")
        
        # Проверка, что диапазон в пределах одних суток
        if self.start.hour < 0 or self.end.hour > 23:
            raise DomainException("Время должно быть в пределах 00:00-23:59")
    
    @property
    def duration_minutes(self) -> int:
        """Длительность в минутах."""
        start_min = self.start.hour * 60 + self.start.minute
        end_min = self.end.hour * 60 + self.end.minute
        return end_min - start_min
    
    @property
    def duration_hours(self) -> float:
        """Длительность в часах."""
        return self.duration_minutes / 60
    
    def contains(self, other: 'TimeRange') -> bool:
        """Содержит ли этот диапазон другой."""
        return self.start <= other.start and self.end >= other.end
    
    def overlaps(self, other: 'TimeRange') -> bool:
        """Пересекается ли с другим диапазоном."""
        return self.start < other.end and other.start < self.end
    
    @classmethod
    def one_hour_from(cls, start: time) -> 'TimeRange':
        """Создать часовой слот с указанного времени."""
        end = (datetime.combine(datetime.today(), start) + timedelta(hours=1)).time()
        return cls(start, end)
    
    def __str__(self) -> str:
        return f"{self.start.strftime('%H:%M')}-{self.end.strftime('%H:%M')}"