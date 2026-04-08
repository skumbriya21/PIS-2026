import asyncpg
import aio_pika
from fastapi import FastAPI

from infrastructure.repositories.postgres_booking_repository import PostgresBookingRepository
from infrastructure.messaging.rabbitmq_publisher import RabbitMQEventPublisher
from infrastructure.grpc.court_grpc_client import CourtGrpcClient
from application.services.booking_service_impl import BookingServiceImpl
from api.rest import booking_controller


async def create_app():
    """Создание приложения с инициализацией зависимостей."""
    
    # Подключение к PostgreSQL
    pg_pool = await asyncpg.create_pool(
        "postgresql://postgres:postgres@booking-db:5432/booking"
    )
    
    # Подключение к RabbitMQ
    rabbit_conn = await aio_pika.connect_robust("amqp://rabbitmq:5672")
    
    # Инициализация инфраструктуры
    repository = PostgresBookingRepository(pg_pool)
    
    event_publisher = RabbitMQEventPublisher(rabbit_conn)
    await event_publisher.connect()
    
    court_client = CourtGrpcClient("court-service:50051")
    
    # Создание сервиса
    booking_service = BookingServiceImpl(
        repository=repository,
        event_publisher=event_publisher,
        court_client=court_client
    )
    
    # Настройка контроллера
    booking_controller.set_booking_service(booking_service)
    
    return booking_controller.app


# Запуск
if __name__ == "__main__":
    import uvicorn
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)