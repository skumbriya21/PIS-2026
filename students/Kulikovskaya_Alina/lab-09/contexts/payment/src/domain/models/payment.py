from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4


@dataclass
class Payment:
    """Платёж."""
    
    id: str = field(default_factory=lambda: str(uuid4()))
    booking_id: str = ""
    user_id: str = ""
    amount: float = 0.0
    currency: str = "BYN"
    status: str = "pending"  # pending, processing, success, failed, refunded
    payment_method: str = ""  # card, cash, online_bank
    external_payment_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    processed_at: Optional[str] = None
    refunded_at: Optional[str] = None
    
    def mark_processing(self) -> None:
        """В обработке."""
        if self.status != "pending":
            raise ValueError(f"Нельзя перевести в processing из {self.status}")
        self.status = "processing"
    
    def mark_success(self, external_id: str) -> None:
        """Успешно обработан."""
        if self.status != "processing":
            raise ValueError(f"Нельзя подтвердить из {self.status}")
        self.status = "success"
        self.external_payment_id = external_id
        self.processed_at = datetime.now().isoformat()
    
    def mark_failed(self, reason: str) -> None:
        """Ошибка обработки."""
        self.status = "failed"
        self.processed_at = datetime.now().isoformat()
    
    def refund(self, amount: Optional[float] = None) -> None:
        """Возврат средств."""
        if self.status != "success":
            raise ValueError("Можно вернуть только успешный платёж")
        
        self.status = "refunded"
        self.refunded_at = datetime.now().isoformat()