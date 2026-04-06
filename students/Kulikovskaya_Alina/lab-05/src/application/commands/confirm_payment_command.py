from dataclasses import dataclass


@dataclass(frozen=True)
class ConfirmPaymentCommand:
    """DTO: Команда подтверждения оплаты."""
    booking_id: str
    payment_id: str
    external_payment_id: str