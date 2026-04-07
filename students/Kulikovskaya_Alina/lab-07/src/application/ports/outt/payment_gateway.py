from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PaymentStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class PaymentResult:
    success: bool
    payment_id: Optional[str]
    status: PaymentStatus
    error_message: Optional[str] = None


class IPaymentGateway(ABC):
    """Исходящий порт: интеграция с платёжной системой."""
    
    @abstractmethod
    def charge(self, amount: float, currency: str, description: str,
               idempotency_key: str) -> PaymentResult:
        """Списать средства с карты."""
        pass
    
    @abstractmethod
    def refund(self, payment_id: str, 
               amount: Optional[float] = None) -> PaymentResult:
        """Вернуть средства."""
        pass
    
    @abstractmethod
    def get_status(self, payment_id: str) -> PaymentStatus:
        """Проверить статус платежа."""
        pass