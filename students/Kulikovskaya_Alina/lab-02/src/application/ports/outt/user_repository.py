from abc import ABC, abstractmethod
from typing import List, Optional

from domain.models.user import User, UserRole


class IUserRepository(ABC):
    """Исходящий порт: хранение пользователей."""
    
    @abstractmethod
    def save(self, user: User) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_admins(self) -> List[User]:
        pass