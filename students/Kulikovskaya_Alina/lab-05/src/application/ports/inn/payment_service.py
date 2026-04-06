from abc import ABC, abstractmethod
from typing import Optional


class IPaymentService(ABC):
    """Входящий порт: обработка платежей."""
    
    @abstractmethod
    def process_payment(self, booking_id: str, amount: float, 
                        currency: str) -> str:
        """Инициировать платёж."""
        pass
    
    @abstractmethod
    def verify_payment(self, payment_id: str) -> bool:
        """Проверить статус платежа."""
        pass
    
    @abstractmethod
    def refund_payment(self, payment_id: str, amount: Optional[float] = None) -> bool:
        """Вернуть платёж."""
        pass