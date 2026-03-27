import logging
from typing import Optional

from application.ports.outt.notification_service import INotificationService

logger = logging.getLogger(__name__)


class MockNotificationService(INotificationService):
    """Mock-реализация (логирует вместо отправки)."""
    
    def send_booking_confirmation(self, to_email: str, to_phone: Optional[str],
                                  booking_id: str, court_name: str,
                                  slot_date: str, slot_time: str,
                                  qr_code: Optional[str] = None) -> bool:
        logger.info(f"[MOCK EMAIL] To: {to_email}, Booking: {booking_id}, "
                   f"Court: {court_name}, Date: {slot_date} {slot_time}")
        return True
    
    def send_payment_reminder(self, to_email: str, booking_id: str,
                              hours_left: int) -> bool:
        logger.info(f"[MOCK EMAIL] To: {to_email}, Reminder: {booking_id}, "
                   f"Hours left: {hours_left}")
        return True
    
    def send_cancellation_notice(self, to_email: str, booking_id: str,
                                 reason: Optional[str]) -> bool:
        logger.info(f"[MOCK EMAIL] To: {to_email}, Cancelled: {booking_id}, "
                   f"Reason: {reason}")
        return True
    
    def send_sms(self, to_phone: str, message: str) -> bool:
        logger.info(f"[MOCK SMS] To: {to_phone}, Message: {message}")
        return True