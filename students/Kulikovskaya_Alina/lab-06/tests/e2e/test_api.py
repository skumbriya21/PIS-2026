"""
E2E тесты REST API с реальной PostgreSQL в Docker (Testcontainers).
"""

import pytest
import httpx
from datetime import date, time, timedelta

# Testcontainers
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer


@pytest.fixture(scope="module")
def postgres_container():
    """Запуск PostgreSQL в Docker."""
    with PostgresContainer("postgres:15-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="module")
def redis_container():
    """Запуск Redis в Docker."""
    with RedisContainer("redis:7-alpine") as redis:
        yield redis


@pytest.fixture
def api_client(postgres_container, redis_container):
    """HTTP клиент для тестирования API."""
    # Настройка подключения к тестовым контейнерам
    import os
    os.environ["DATABASE_URL"] = postgres_container.get_connection_url()
    os.environ["REDIS_URL"] = redis_container.get_connection_url()
    
    from infrastructure.config.fastapi_app import app
    return httpx.AsyncClient(app=app, base_url="http://test")


@pytest.mark.asyncio
class TestBookingAPI:
    """E2E тесты API бронирований."""
    
    async def test_create_booking_endpoint(self, api_client):
        """POST /api/bookings создаёт бронирование."""
        tomorrow = date.today() + timedelta(days=1)
        
        response = await api_client.post(
            "/api/bookings",
            json={
                "court_id": "court-bd-01",
                "date": tomorrow.isoformat(),
                "start_time": "18:00:00",
                "end_time": "19:00:00",
                "payment_method": "online"
            },
            params={"user_id": "test-user-123"}  # В реальности из JWT
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "booking_id" in data
        assert data["status"] == "pending_payment"
        assert data["total_amount"] == 30.0  # 25 + 20%
    
    async def test_get_booking_endpoint(self, api_client):
        """GET /api/bookings/{id} возвращает бронирование."""
        # Сначала создаём
        tomorrow = date.today() + timedelta(days=1)
        create_response = await api_client.post(
            "/api/bookings",
            json={
                "court_id": "court-bd-01",
                "date": tomorrow.isoformat(),
                "start_time": "18:00:00",
                "end_time": "19:00:00",
                "payment_method": "online"
            },
            params={"user_id": "test-user-123"}
        )
        booking_id = create_response.json()["booking_id"]
        
        # Получаем
        get_response = await api_client.get(f"/api/bookings/{booking_id}")
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["id"] == booking_id
        assert data["court_name"] is not None
    
    async def test_cancel_booking_endpoint(self, api_client):
        """DELETE /api/bookings/{id} отменяет бронирование."""
        # Создаём
        tomorrow = date.today() + timedelta(days=1)
        create_response = await api_client.post(
            "/api/bookings",
            json={
                "court_id": "court-bd-01",
                "date": tomorrow.isoformat(),
                "start_time": "18:00:00",
                "end_time": "19:00:00",
                "payment_method": "online"
            },
            params={"user_id": "test-user-123"}
        )
        booking_id = create_response.json()["booking_id"]
        
        # Отменяем
        cancel_response = await api_client.delete(
            f"/api/bookings/{booking_id}",
            json={"reason": "Тестовая отмена"},
            params={"user_id": "test-user-123"}
        )
        
        assert cancel_response.status_code == 204
        
        # Проверяем статус
        get_response = await api_client.get(f"/api/bookings/{booking_id}")
        assert get_response.json()["status"] == "cancelled"
    
    async def test_get_nonexistent_booking_404(self, api_client):
        """Запрос несуществующего бронирования возвращает 404."""
        response = await api_client.get("/api/bookings/nonexistent-id")
        
        assert response.status_code == 404