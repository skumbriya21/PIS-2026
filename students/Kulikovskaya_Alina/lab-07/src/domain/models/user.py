from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from uuid import uuid4


class UserRole(Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    MANAGER = "manager"


@dataclass
class User:
    """
    Entity: Пользователь системы.
    """
    id: str = field(default_factory=lambda: str(uuid4()))
    email: str = ""
    phone: str = ""
    full_name: str = ""
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
    
    def __post_init__(self):
        if not self.email and not self.phone:
            raise ValueError("Необходим email или телефон")
    
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)