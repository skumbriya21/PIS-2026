# ORM модель для пользователя

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Boolean

from infrastructure.database.base import Base


class UserModel(Base):
    # ORM модель пользователя
    
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="customer")  # customer, admin, manager
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<UserModel(id={self.id}, email={self.email})>"