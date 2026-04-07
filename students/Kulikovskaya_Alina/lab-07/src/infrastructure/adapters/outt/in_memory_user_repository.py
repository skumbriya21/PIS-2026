from typing import Dict, List, Optional

from domain.models.user import User, UserRole
from application.ports.outt.user_repository import IUserRepository


class InMemoryUserRepository(IUserRepository):
    """InMemory реализация для тестирования."""
    
    def __init__(self):
        self._storage: Dict[str, User] = {}
    
    def save(self, user: User) -> None:
        self._storage[user.id] = user
    
    def find_by_id(self, user_id: str) -> Optional[User]:
        return self._storage.get(user_id)
    
    def find_by_email(self, email: str) -> Optional[User]:
        for user in self._storage.values():
            if user.email == email:
                return user
        return None
    
    def find_admins(self) -> List[User]:
        return [u for u in self._storage.values() if u.role == UserRole.ADMIN]