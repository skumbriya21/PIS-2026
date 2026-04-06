# ORM модель для площадки.

from sqlalchemy import String, Integer, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base


class CourtModel(Base):
    # ORM модель спортивной площадки
    
    __tablename__ = "courts"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    court_type: Mapped[str] = mapped_column(String(50), nullable=False)  # volleyball, basketball, etc.
    hourly_rate: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    def __repr__(self) -> str:
        return f"<CourtModel(id={self.id}, name={self.name}, type={self.court_type})>"