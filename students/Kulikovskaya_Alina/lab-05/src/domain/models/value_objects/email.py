import re
from dataclasses import dataclass

from domain.exceptions.domain_exception import DomainException


@dataclass(frozen=True)
class Email:
    """
    Value Object: Email адрес с валидацией.
    """
    address: str
    
    def __post_init__(self):
        if not self._is_valid(self.address):
            raise DomainException(f"Неверный формат email: {self.address}")
    
    def _is_valid(self, email: str) -> bool:
        """Простая валидация email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @property
    def domain(self) -> str:
        """Домен email (после @)."""
        return self.address.split('@')[1]
    
    def __str__(self) -> str:
        return self.address.lower()