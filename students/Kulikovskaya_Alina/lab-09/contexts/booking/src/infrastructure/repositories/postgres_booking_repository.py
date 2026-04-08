from typing import Optional, List
import asyncpg

from domain.models.booking import Booking
from application.ports.outt.booking_repository import IBookingRepository


class PostgresBookingRepository(IBookingRepository):
    """PostgreSQL репозиторий бронирований."""
    
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool
    
    async def save(self, booking: Booking) -> None:
        """Сохранить бронирование."""
        async with self._pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO bookings (
                    id, user_id, court_id, slot_date, slot_time, status,
                    total_amount, currency, payment_id, created_by_admin,
                    notes, created_at, updated_at, confirmed_at, cancelled_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                ON CONFLICT (id) DO UPDATE SET
                    status = EXCLUDED.status,
                    payment_id = EXCLUDED.payment_id,
                    updated_at = EXCLUDED.updated_at,
                    confirmed_at = EXCLUDED.confirmed_at,
                    cancelled_at = EXCLUDED.cancelled_at,
                    notes = EXCLUDED.notes
            """,
                booking.id, booking.user_id, booking.court_id,
                booking.slot_date, booking.slot_time, booking.status,
                booking.total_amount, booking.currency, booking.payment_id,
                booking.created_by_admin, booking.notes,
                booking.created_at, booking.updated_at,
                booking.confirmed_at, booking.cancelled_at
            )
    
    async def find_by_id(self, booking_id: str) -> Optional[Booking]:
        """Найти по ID."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM bookings WHERE id = $1", booking_id
            )
            return self._to_domain(row) if row else None
    
    async def find_by_user_id(self, user_id: str) -> List[Booking]:
        """Найти по пользователю."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM bookings WHERE user_id = $1 ORDER BY created_at DESC",
                user_id
            )
            return [self._to_domain(r) for r in rows]
    
    async def find_by_court_and_slot(
        self, court_id: str, slot_date: str, slot_time: str
    ) -> Optional[Booking]:
        """Найти по площадке и слоту."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM bookings 
                WHERE court_id = $1 AND slot_date = $2 AND slot_time = $3
                AND status NOT IN ('cancelled', 'expired')
            """, court_id, slot_date, slot_time)
            return self._to_domain(row) if row else None
    
    def _to_domain(self, row) -> Booking:
        """Конвертация строки в доменный объект."""
        return Booking(
            id=row['id'],
            user_id=row['user_id'],
            court_id=row['court_id'],
            slot_date=row['slot_date'],
            slot_time=row['slot_time'],
            status=row['status'],
            total_amount=row['total_amount'],
            currency=row['currency'],
            payment_id=row['payment_id'],
            created_by_admin=row['created_by_admin'],
            notes=row['notes'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            confirmed_at=row['confirmed_at'],
            cancelled_at=row['cancelled_at']
        )