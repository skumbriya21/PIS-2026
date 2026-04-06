import random
import uuid
from typing import Optional

from application.ports.outt.payment_gateway import (
    IPaymentGateway, PaymentResult, PaymentStatus
)


class MockPaymentGateway(IPaymentGateway):
    """Mock-реализация для разработки."""
    
    def __init__(self, failure_rate: float = 0.1):
        self._failure_rate = failure_rate
        self._payments: dict = {}
    
    def charge(self, amount: float, currency: str, description: str,
               idempotency_key: str) -> PaymentResult:
        """Имитация списания средств."""
        if idempotency_key in self._payments:
            return self._payments[idempotency_key]
        
        if random.random() < self._failure_rate:
            result = PaymentResult(
                success=False,
                payment_id=None,
                status=PaymentStatus.FAILED,
                error_message="Insufficient funds"
            )
        else:
            payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
            result = PaymentResult(
                success=True,
                payment_id=payment_id,
                status=PaymentStatus.SUCCESS
            )
        
        self._payments[idempotency_key] = result
        return result
    
    def refund(self, payment_id: str, 
               amount: Optional[float] = None) -> PaymentResult:
        return PaymentResult(
            success=True,
            payment_id=f"REF-{payment_id}",
            status=PaymentStatus.REFUNDED
        )
    
    def get_status(self, payment_id: str) -> PaymentStatus:
        return PaymentStatus.SUCCESS