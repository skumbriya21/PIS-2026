"""
Интеграционные тесты gRPC Booking Service.
"""

import pytest
import grpc
from generated import booking_pb2, booking_pb2_grpc


@pytest.fixture
async def grpc_channel():
    """gRPC канал для тестов."""
    channel = grpc.aio.insecure_channel("localhost:50051")
    yield channel
    await channel.close()


@pytest.fixture
def booking_stub(grpc_channel):
    """Stub для BookingService."""
    return booking_pb2_grpc.BookingServiceStub(grpc_channel)


@pytest.mark.asyncio
class TestBookingGrpc:
    """Тесты gRPC бронирования."""
    
    async def test_create_booking_success(self, booking_stub):
        """Успешное создание бронирования."""
        request = booking_pb2.CreateBookingRequest(
            user_id="test-user-123",
            court_id="court-bd-01",
            slot_date="2025-04-15",
            start_time="18:00",
            end_time="19:00",
            payment_method="online"
        )
        
        response = await booking_stub.CreateBooking(request)
        
        assert response.booking_id
        assert response.status == booking_pb2.PENDING_PAYMENT
        assert response.total_amount.amount > 0
        assert response.confirmation_code
    
    async def test_create_booking_validation_error(self, booking_stub):
        """Ошибка валидации при создании."""
        request = booking_pb2.CreateBookingRequest(
            user_id="",  # Пустой user_id
            court_id="court-bd-01",
            slot_date="2025-04-15",
            start_time="18:00",
            end_time="19:00"
        )
        
        with pytest.raises(grpc.RpcError) as exc_info:
            await booking_stub.CreateBooking(request)
        
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    
    async def test_get_booking_not_found(self, booking_stub):
        """Получение несуществующего бронирования."""
        request = booking_pb2.GetBookingRequest(
            booking_id="non-existent-id"
        )
        
        with pytest.raises(grpc.RpcError) as exc_info:
            await booking_stub.GetBooking(request)
        
        assert exc_info.value.code() == grpc.StatusCode.NOT_FOUND
    
    async def test_streaming_availability(self, booking_stub):
        """Streaming RPC для проверки доступности."""
        
        async def request_generator():
            for hour in [18, 19, 20]:
                yield booking_pb2.CheckAvailabilityRequest(
                    court_id="court-bd-01",
                    date="2025-04-15",
                    preferred_time=f"{hour}:00",
                    flexibility_hours=1
                )
        
        responses = []
        async for response in booking_stub.CheckAvailability(request_generator()):
            responses.append(response)
        
        assert len(responses) == 3
        for r in responses:
            assert r.court_id == "court-bd-01"