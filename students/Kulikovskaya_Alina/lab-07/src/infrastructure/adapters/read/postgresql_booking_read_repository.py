from datetime import date
from typing import List, Optional

from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import Session

from application.read_models.booking_read_model import BookingReadModel, BookingListView
from application.ports.read.booking_read_repository import IBookingReadRepository

from infrastructure.adapters.outt.postgresql_models.read_booking_orm import ReadBookingORM


class PostgreSQLBookingReadRepository(IBookingReadRepository):
    """
    Реализация репозитория чтения на PostgreSQL.
    
    Использует отдельную таблицу (materialized view) для оптимизации запросов.
    """
    
    def __init__(self, session: Session):
        self._session = session
    
    def get_by_id(self, booking_id: str) -> Optional[BookingReadModel]:
        orm_obj = self._session.get(ReadBookingORM, booking_id)
        if orm_obj is None:
            return None
        return self._to_domain(orm_obj)
    
    def list_by_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[BookingListView]:
        """Оптимизированный запрос с фильтрами."""
        stmt = select(ReadBookingORM).where(ReadBookingORM.user_id == user_id)
        
        # Применяем фильтры на уровне БД
        if status:
            stmt = stmt.where(ReadBookingORM.status == status)
        if from_date:
            stmt = stmt.where(ReadBookingORM.date >= from_date)
        if to_date:
            stmt = stmt.where(ReadBookingORM.date <= to_date)
        
        # Сортировка: сначала новые
        stmt = stmt.order_by(ReadBookingORM.date.desc(), ReadBookingORM.start_time.desc())
        
        # Пагинация
        stmt = stmt.limit(limit).offset(offset)
        
        orm_objects = self._session.execute(stmt).scalars().all()
        
        return [self._to_list_view(obj) for obj in orm_objects]
    
    def search(
        self,
        query: str,
        court_type: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[BookingReadModel]:
        """Полнотекстовый поиск через ILIKE."""
        search_pattern = f"%{query}%"
        
        stmt = select(ReadBookingORM).where(
            or_(
                ReadBookingORM.user_email.ilike(search_pattern),
                ReadBookingORM.user_phone.ilike(search_pattern),
                ReadBookingORM.court_name.ilike(search_pattern)
            )
        )
        
        if court_type:
            stmt = stmt.where(ReadBookingORM.court_type == court_type)
        if date_from:
            stmt = stmt.where(ReadBookingORM.date >= date_from)
        if date_to:
            stmt = stmt.where(ReadBookingORM.date <= date_to)
        
        orm_objects = self._session.execute(stmt).scalars().all()
        return [self._to_domain(obj) for obj in orm_objects]
    
    def get_upcoming_for_reminders(self, hours_ahead: int = 24) -> List[BookingReadModel]:
        """Запрос для cron-задачи напоминаний."""
        from datetime import datetime, timedelta
        
        now = datetime.now()
        future = now + timedelta(hours=hours_ahead)
        
        stmt = select(ReadBookingORM).where(
            and_(
                ReadBookingORM.status == "confirmed",
                ReadBookingORM.date == future.date(),
                ReadBookingORM.start_time.between(
                    future.time(),
                    (future + timedelta(hours=1)).time()
                ),
                ReadBookingORM.reminder_sent == False
            )
        )
        
        orm_objects = self._session.execute(stmt).scalars().all()
        return [self._to_domain(obj) for obj in orm_objects]
    
    def _to_domain(self, orm: ReadBookingORM) -> BookingReadModel:
        """Маппинг ORM → Domain."""
        return BookingReadModel(
            booking_id=orm.booking_id,
            user_id=orm.user_id,
            user_email=orm.user_email,
            user_phone=orm.user_phone,
            court_id=orm.court_id,
            court_name=orm.court_name,
            court_type=orm.court_type,
            court_type_display=orm.court_type_display,
            date=orm.date,
            start_time=orm.start_time,
            end_time=orm.end_time,
            status=orm.status,
            status_display=orm.status_display,
            total_amount=orm.total_amount,
            currency=orm.currency,
            payment_status=orm.payment_status,
            created_at=orm.created_at,
            confirmed_at=orm.confirmed_at,
            cancelled_at=orm.cancelled_at,
            created_by_admin=orm.created_by_admin,
            notes=orm.notes,
            is_past=orm.date < date.today(),
            hours_until_start=None  # Вычисляется динамически
        )
    
    def _to_list_view(self, orm: ReadBookingORM) -> BookingListView:
        """Упрощённый маппинг для списков."""
        from datetime import datetime
        
        # Вычисляем can_cancel на лету
        can_cancel = (
            orm.status in ["pending_payment", "reserved", "confirmed"]
            and datetime.combine(orm.date, orm.start_time) > datetime.now()
        )
        
        return BookingListView(
            booking_id=orm.booking_id,
            court_name=orm.court_name,
            date=orm.date,
            start_time=orm.start_time,
            status=orm.status,
            total_amount=orm.total_amount,
            can_cancel=can_cancel
        )