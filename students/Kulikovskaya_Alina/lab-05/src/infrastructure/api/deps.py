from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.session import get_db_session
from infrastructure.adapters.outt.postgresql_booking_repository import PostgreSQLBookingRepository
from infrastructure.adapters.outt.postgresql_court_repository import PostgreSQLCourtRepository
from infrastructure.adapters.outt.redis_schedule_repository import RedisScheduleRepository
from infrastructure.adapters.outt.mock_payment_gateway import MockPaymentGateway
from infrastructure.adapters.outt.mock_notification_service import MockNotificationService

from application.services.booking_service_impl import BookingServiceImpl


async def get_booking_repository(session: AsyncSession = Depends(get_db_session)):
    """Получить репозиторий бронирований."""
    return PostgreSQLBookingRepository(session)


async def get_court_repository(session: AsyncSession = Depends(get_db_session)):
    """Получить репозиторий площадок."""
    return PostgreSQLCourtRepository(session)


async def get_schedule_repository():
    """Получить репозиторий расписания."""
    import redis.asyncio as redis
    from infrastructure.config.settings import settings
    
    redis_client = redis.from_url(settings.REDIS_URL)
    return RedisScheduleRepository(redis_client)


async def get_booking_service(
    booking_repo=Depends(get_booking_repository),
    court_repo=Depends(get_court_repository),
    schedule_repo=Depends(get_schedule_repository)
):
    """Получить BookingService с инжектированными зависимостями."""
    return BookingServiceImpl(
        booking_repository=booking_repo,
        court_repository=court_repo,
        schedule_repository=schedule_repo,
        payment_gateway=MockPaymentGateway(),
        notification_service=MockNotificationService()
    )