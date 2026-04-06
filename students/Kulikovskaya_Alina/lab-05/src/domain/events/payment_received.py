from dataclasses import dataclass

from src.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class PaymentReceivedEvent(DomainEvent):
    """Событие: получен платёж."""
    
    payment_id: str
    booking_id: str
    amount: float
    currency: str
    
    def event_name(self) -> str:
        return "payment.received"