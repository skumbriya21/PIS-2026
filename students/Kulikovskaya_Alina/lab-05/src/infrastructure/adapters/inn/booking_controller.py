from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateBookingRequest:
    court_id: str
    date: str           # "2025-03-15"
    start_time: str     # "18:00"
    end_time: str       # "19:00"
    payment_method: str = "online"
    notes: Optional[str] = None


class BookingController:
    """REST Controller для бронирований."""
    
    def __init__(self, booking_service):
        self._service = booking_service
    
    def create_booking(self, request: CreateBookingRequest, 
                       user_id: str) -> dict:
        """POST /api/bookings"""
        raise NotImplementedError("Реализовать в Lab #4-5")
    
    def get_booking(self, booking_id: str) -> dict:
        """GET /api/bookings/{id}"""
        raise NotImplementedError("Реализовать в Lab #4-5")
    
    def cancel_booking(self, booking_id: str, user_id: str) -> dict:
        """DELETE /api/bookings/{id}"""
        raise NotImplementedError("Реализовать в Lab #4-5")