from abc import ABC, abstractmethod
from datetime import datetime, date, time, timedelta
from typing import Optional

from domain.exceptions.domain_exception import DomainException
from domain.models.value_objects.court_type import CourtType


class BookingRule(ABC):
    """Базовый класс для бизнес-правил бронирования."""
    
    @abstractmethod
    def is_satisfied(self, court_type: CourtType, slot_date: date, 
                     slot_time: time, now: Optional[datetime] = None) -> bool:
        pass
    
    @abstractmethod
    def error_message(self) -> str:
        pass


class MinAdvanceBookingRule(BookingRule):
    """
    Правило: минимальное время до бронирования.
    
    Online: минимум 30 минут до начала слота
    """
    
    MIN_ADVANCE_MINUTES = 30
    
    def is_satisfied(self, court_type: CourtType, slot_date: date,
                     slot_time: time, now: Optional[datetime] = None) -> bool:
        if now is None:
            now = datetime.now()
        
        slot_datetime = datetime.combine(slot_date, slot_time)
        minutes_until = (slot_datetime - now).total_seconds() / 60
        
        return minutes_until >= self.MIN_ADVANCE_MINUTES
    
    def error_message(self) -> str:
        return f"Online-бронирование возможно не позднее чем за {self.MIN_ADVANCE_MINUTES} минут"


class MaxAdvanceBookingRule(BookingRule):
    """
    Правило: максимальное время до бронирования.
    
    Можно бронировать максимум на 14 дней вперёд
    """
    
    MAX_ADVANCE_DAYS = 14
    
    def is_satisfied(self, court_type: CourtType, slot_date: date,
                     slot_time: time, now: Optional[datetime] = None) -> bool:
        if now is None:
            now = datetime.now()
        
        max_date = now.date() + timedelta(days=self.MAX_ADVANCE_DAYS)
        return slot_date <= max_date
    
    def error_message(self) -> str:
        return f"Бронирование возможно максимум на {self.MAX_ADVANCE_DAYS} дней вперёд"


class PeakHoursRule(BookingRule):
    """
    Правило: пиковые часы с повышенным спросом.
    
    18:00-22:00 в будни, весь день в выходные — требуется предоплата
    """
    
    PEAK_START = time(18, 0)
    PEAK_END = time(22, 0)
    
    def is_satisfied(self, court_type: CourtType, slot_date: date,
                     slot_time: time, now: Optional[datetime] = None) -> bool:
        # Проверка на пиковое время
        is_weekend = slot_date.weekday() >= 5  # Суббота=5, Воскресенье=6
        is_peak_hour = self.PEAK_START <= slot_time < self.PEAK_END
        
        return is_weekend or is_peak_hour
    
    def is_peak(self, court_type: CourtType, slot_date: date,
                slot_time: time) -> bool:
        """Является ли слот пиковым."""
        return self.is_satisfied(court_type, slot_date, slot_time)
    
    def error_message(self) -> str:
        return "Пиковое время требует предоплаты"
    
    def requires_prepayment(self, court_type: CourtType, slot_date: date,
                           slot_time: time) -> bool:
        """Требуется ли предоплата для этого слота."""
        return self.is_peak(court_type, slot_date, slot_time)