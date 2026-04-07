from typing import Dict, List, Set
from datetime import date, time

from domain.models.value_objects.slot import Slot
from application.ports.outt.schedule_repository import IScheduleRepository


class InMemoryScheduleRepository(IScheduleRepository):
    """InMemory реализация расписания."""
    
    def __init__(self):
        self._locks: Dict[tuple, str] = {}  # (court_id, date, time) -> booking_id
        self._confirmed: Set[tuple] = set()
    
    def is_available(self, court_id: str, date: date, 
                     start_time: time) -> bool:
        key = (court_id, date, start_time)
        return key not in self._locks and key not in self._confirmed
    
    def lock_slot(self, court_id: str, date: date, start_time: time,
                  booking_id: str, ttl_minutes: int = 10) -> bool:
        key = (court_id, date, start_time)
        if key in self._locks or key in self._confirmed:
            return False
        
        self._locks[key] = booking_id
        return True
    
    def unlock_slot(self, court_id: str, date: date, 
                    start_time: time) -> None:
        key = (court_id, date, start_time)
        self._locks.pop(key, None)
    
    def confirm_slot(self, court_id: str, date: date, 
                     start_time: time) -> None:
        key = (court_id, date, start_time)
        self._locks.pop(key, None)
        self._confirmed.add(key)
    
    def get_available_slots(self, court_id: str, date: date) -> List[Slot]:
        available = []
        for hour in range(8, 23):  # 08:00 - 22:00
            start = time(hour, 0)
            end = time(hour + 1, 0)
            if self.is_available(court_id, date, start):
                available.append(Slot(
                    court_id=court_id,
                    date=date,
                    start_time=start,
                    end_time=end
                ))
        return available