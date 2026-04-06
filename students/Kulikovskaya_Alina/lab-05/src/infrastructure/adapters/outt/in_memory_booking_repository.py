from typing import Dict, List, Optional
from datetime import date, time

from domain.models.booking import Booking
from application.ports.outt.booking_repository import IBookingRepository


class InMemoryBookingRepository(IBookingRepository):
    """InMemory реализация для тестирования."""
    
    def __init__(self):
        self._storage: Dict[str, Booking] = {}
    
    def save(self, booking: Booking) -> None:
        self._storage[booking.id] = booking
    
    def find_by_id(self, booking_id: str) -> Optional[Booking]:
        return self._storage.get(booking_id)
    
    def find_by_user_id(self, user_id: str) -> List[Booking]:
        return [b for b in self._storage.values() if b.user_id == user_id]
    
    def find_by_court_and_date(self, court_id: str, date: date) -> List[Booking]:
        return [
            b for b in self._storage.values() 
            if b.court_id == court_id and b.slot.date == date
        ]
    
    def find_active_by_slot(self, court_id: str, date: date, 
                           start_time: time) -> Optional[Booking]:
        for booking in self._storage.values():
            if (booking.court_id == court_id and 
                booking.slot.date == date and 
                booking.slot.start_time == start_time and
                booking.status.value not in ('cancelled', 'expired')):
                return booking
        return None