from dataclasses import dataclass


@dataclass(frozen=True)
class Money:
    """
    Value Object: Денежная сумма с валютой.
    
    Иммутабельный, поддерживает операции сложения/вычитания.
    """
    amount: float
    currency: str = "BYN"
    
    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Сумма не может быть отрицательной")
        if len(self.currency) != 3:
            raise ValueError("Валюта должна быть в формате ISO 4217 (3 буквы)")
    
    def add(self, other: 'Money') -> 'Money':
        """Сложить две суммы (одинаковой валюты)."""
        if self.currency != other.currency:
            raise ValueError(f"Нельзя складывать разные валюты: {self.currency} и {other.currency}")
        return Money(self.amount + other.amount, self.currency)
    
    def multiply(self, factor: int) -> 'Money':
        """Умножить сумму на коэффициент."""
        return Money(self.amount * factor, self.currency)
    
    def __str__(self) -> str:
        return f"{self.amount:.2f} {self.currency}"