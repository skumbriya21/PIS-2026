from enum import Enum


class PaymentStatus(Enum):
    """Статусы платежа."""
    
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"