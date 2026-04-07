from abc import ABC, abstractmethod
from typing import Optional


class INotificationService(ABC):
    """Исходящий порт: отправка уведомлений."""
    
    @abstractmethod
    def send_booking_confirmation(self, to_email: str, to_phone: Optional[str],
                                  booking_id: str, court_name: str,
                                  slot_date: str, slot_time: str,
                                  qr_code: Optional[str] = None) -> bool:
        """Отправить подтверждение бронирования."""
        pass
    
    @abstractmethod
    def send_payment_reminder(self, to_email: str, booking_id: str,
                              hours_left: int) -> bool:
        """Отправить напоминание об оплате."""
        pass
    
    @abstractmethod
    def send_cancellation_notice(self, to_email: str, booking_id: str,
                                 reason: Optional[str]) -> bool:
        """Отправить уведомление об отмене."""
        pass
    
    @abstractmethod
    def send_sms(self, to_phone: str, message: str) -> bool:
        """Отправить SMS."""
        pass