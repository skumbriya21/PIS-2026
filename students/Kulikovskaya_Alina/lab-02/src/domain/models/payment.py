from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from src.domain.models.value_objects.money import Money
from src.domain.models.value_objects.payment_status import PaymentStatus


@dataclass
class Payment:
    """
    Entity: Платёж (часть агрегата Booking).
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    booking_id: str = ""
    amount: Optional[Money] = None
    status: PaymentStatus = PaymentStatus.PENDING
    external_payment_id: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def mark_as_success(self, external_id: str) -> None:
        self.status = PaymentStatus.SUCCESS
        self.external_payment_id = external_id
        self.paid_at = datetime.now()
    
    def mark_as_failed(self, reason: Optional[str] = None) -> None:
        self.status = PaymentStatus.FAILED
    
    def refund(self) -> None:
        if self.status != PaymentStatus.SUCCESS:
            raise ValueError("Нельзя вернуть неуспешный платёж")
        self.status = PaymentStatus.REFUNDED
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Payment):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)