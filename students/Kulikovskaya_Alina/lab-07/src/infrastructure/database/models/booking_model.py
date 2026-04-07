# ORM модель для бронирования

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Date, Time, DateTime, Numeric, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.base import Base


class BookingModel(Base):
    # ORM модель бронирования
    
    __tablename__ = "bookings"
    
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    court_id: Mapped[str] = mapped_column(String(50), ForeignKey("courts.id"), nullable=False)
    
    # Slot
    slot_date: Mapped[Date] = mapped_column(Date, nullable=False)
    slot_start_time: Mapped[Time] = mapped_column(Time, nullable=False)
    slot_end_time: Mapped[Time] = mapped_column(Time, nullable=False)
    
    # Status and payment
    status: Mapped[str] = mapped_column(String(50), default="pending_payment")
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="BYN")
    payment_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Metadata
    created_by_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<BookingModel(id={self.id}, status={self.status})>"