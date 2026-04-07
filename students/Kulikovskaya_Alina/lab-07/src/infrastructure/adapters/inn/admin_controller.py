from typing import Optional


class AdminController:
    """REST Controller для администраторов."""
    
    def __init__(self, admin_service):
        self._service = admin_service
    
    def create_phone_booking(self, court_id: str, date: str, 
                             start_time: str, customer_name: str,
                             customer_phone: str) -> dict:
        """POST /api/admin/bookings/phone"""
        raise NotImplementedError("Реализовать в Lab #4-5")
    
    def get_all_bookings(self, date: Optional[str] = None) -> dict:
        """GET /api/admin/bookings"""
        raise NotImplementedError("Реализовать в Lab #4-5")
    
    def cancel_booking(self, booking_id: str, reason: str) -> dict:
        """DELETE /api/admin/bookings/{id}"""
        raise NotImplementedError("Реализовать в Lab #4-5")