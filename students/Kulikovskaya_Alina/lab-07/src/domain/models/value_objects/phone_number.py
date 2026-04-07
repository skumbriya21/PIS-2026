import re
from dataclasses import dataclass

from domain.exceptions.domain_exception import DomainException


@dataclass(frozen=True)
class PhoneNumber:
    """
    Value Object: Номер телефона с валидацией.
    
    Формат: +375 (XX) XXX-XX-XX (Беларусь)
    """
    raw: str
    
    def __post_init__(self):
        cleaned = self._clean(self.raw)
        if not self._is_valid(cleaned):
            raise DomainException(f"Неверный формат номера телефона: {self.raw}")
    
    def _clean(self, phone: str) -> str:
        """Очистка от пробелов, скобок, дефисов."""
        return re.sub(r'[\s\-\(\)\.]', '', phone)
    
    def _is_valid(self, cleaned: str) -> bool:
        """Валидация белорусского номера."""
        # +375XXXXXXXXX или 375XXXXXXXXX или 80XXXXXXXXX
        patterns = [
            r'^\+375(25|29|33|44)\d{7}$',  # Мобильный с +
            r'^375(25|29|33|44)\d{7}$',     # Мобильный без +
            r'^80(25|29|33|44)\d{7}$',      # Мобильный с 80
        ]
        return any(re.match(p, cleaned) for p in patterns)
    
    @property
    def formatted(self) -> str:
        """Форматированный номер: +375 (29) 123-45-67."""
        cleaned = self._clean(self.raw)
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
        if cleaned.startswith('80'):
            cleaned = '375' + cleaned[2:]
        
        return f"+{cleaned[:3]} ({cleaned[3:5]}) {cleaned[5:8]}-{cleaned[8:10]}-{cleaned[10:]}"
    
    def __str__(self) -> str:
        return self.formatted