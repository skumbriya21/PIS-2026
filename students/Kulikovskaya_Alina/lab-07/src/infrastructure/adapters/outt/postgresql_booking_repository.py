# PostgreSQL реализация репозитория бронирований

from typing import List, Optional
from datetime import date, time

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.booking import Booking
from domain.models.value_objects.slot import Slot
from domain.models.value_objects.money import Money
from domain.models.value_objects.booking_status import BookingStatus
from application.ports.outt.booking_repository import IBookingRepository

from infrastructure.database.models.booking_model import BookingModel


class PostgreSQLBookingRepository(IBookingRepository):
    # PostgreSQL реализация репозитория бронирований
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    def _to_domain(self, model: BookingModel) -> Booking:
        # Конвертация ORM модели в доменную сущность
        return Booking(
            id=model.id,
            user_id=model.user_id,
            court_id=model.court_id,
            slot=Slot(
                court_id=model.court_id,
                date=model.slot_date,
                start_time=model.slot_start_time,
                end_time=model.slot_end_time
            ),
            status=BookingStatus(model.status),
            total_amount=Money(float(model.total_amount), model.currency) if model.total_amount else None,
            payment_id=model.payment_id,
            created_by_admin=model.created_by_admin,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            confirmed_at=model.confirmed_at,
            cancelled_at=model.cancelled_at
        )
    
    def _to_model(self, booking: Booking) -> BookingModel:
        # Конвертация доменной сущности в ORM модель
        return BookingModel(
            id=booking.id,
            user_id=booking.user_id,
            court_id=booking.court_id,
            slot_date=booking.slot.date,
            slot_start_time=booking.slot.start_time,
            slot_end_time=booking.slot.end_time,
            status=booking.status.value,
            total_amount=booking.total_amount.amount if booking.total_amount else None,
            currency=booking.total_amount.currency if booking.total_amount else "BYN",
            payment_id=booking.payment_id,
            created_by_admin=booking.created_by_admin,
            notes=booking.notes,
            created_at=booking.created_at,
            updated_at=booking.updated_at,
            confirmed_at=booking.confirmed_at,
            cancelled_at=booking.cancelled_at
        )
    
    async def save(self, booking: Booking) -> None:
        # Сохранить или обновить бронирование
        # Проверяем существование
        result = await self._session.execute(
            select(BookingModel).where(BookingModel.id == booking.id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update
            existing.status = booking.status.value
            existing.payment_id = booking.payment_id
            existing.updated_at = booking.updated_at
            existing.confirmed_at = booking.confirmed_at
            existing.cancelled_at = booking.cancelled_at
            existing.notes = booking.notes
        else:
            # Insert
            model = self._to_model(booking)
            self._session.add(model)
        
        await self._session.commit()
    
    async def find_by_id(self, booking_id: str) -> Optional[Booking]:
        # Найти бронирование по ID
        result = await self._session.execute(
            select(BookingModel).where(BookingModel.id == booking_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    async def find_by_user_id(self, user_id: str) -> List[Booking]:
        # Найти все бронирования пользователя
        result = await self._session.execute(
            select(BookingModel).where(BookingModel.user_id == user_id)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]
    
    async def find_by_court_and_date(self, court_id: str, date: date) -> List[Booking]:
        # Найти бронирования площадки на конкретную дату
        result = await self._session.execute(
            select(BookingModel).where(
                and_(
                    BookingModel.court_id == court_id,
                    BookingModel.slot_date == date
                )
            )
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]
    
    async def find_active_by_slot(self, court_id: str, date: date, 
                                 start_time: time) -> Optional[Booking]:
        # Найти активное бронирование на конкретный слот
        result = await self._session.execute(
            select(BookingModel).where(
                and_(
                    BookingModel.court_id == court_id,
                    BookingModel.slot_date == date,
                    BookingModel.slot_start_time == start_time,
                    BookingModel.status.not_in(["cancelled", "expired"])
                )
            )
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None