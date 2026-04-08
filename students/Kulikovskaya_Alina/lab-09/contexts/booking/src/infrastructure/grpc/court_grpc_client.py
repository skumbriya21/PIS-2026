import grpc
from generated import court_pb2, court_pb2_grpc

from application.ports.outt.court_client import ICourtClient


class CourtGrpcClient(ICourtClient):
    """gRPC клиент для Court Context."""
    
    def __init__(self, target: str = "court-service:50051"):
        self._channel = grpc.aio.insecure_channel(target)
        self._stub = court_pb2_grpc.CourtServiceStub(self._channel)
    
    async def check_availability(
        self, court_id: str, slot_date: str, slot_time: str
    ) -> bool:
        """Проверить доступность."""
        request = court_pb2.CheckAvailabilityRequest(
            court_id=court_id,
            date=slot_date,
            start_time=slot_time
        )
        response = await self._stub.CheckAvailability(request)
        return response.is_available
    
    async def get_court_details(self, court_id: str) -> dict:
        """Получить детали площадки."""
        request = court_pb2.GetCourtRequest(court_id=court_id)
        response = await self._stub.GetCourt(request)
        return {
            "id": response.court_id,
            "name": response.name,
            "type": response.court_type,
            "hourly_rate": response.hourly_rate
        }
    
    async def reserve_slot(
        self, court_id: str, slot_date: str, slot_time: str
    ) -> bool:
        """Зарезервировать слот."""
        request = court_pb2.ReserveSlotRequest(
            court_id=court_id,
            date=slot_date,
            start_time=slot_time
        )
        response = await self._stub.ReserveSlot(request)
        return response.success
    
    async def release_slot(
        self, court_id: str, slot_date: str, slot_time: str
    ) -> bool:
        """Освободить слот."""
        request = court_pb2.ReleaseSlotRequest(
            court_id=court_id,
            date=slot_date,
            start_time=slot_time
        )
        response = await self._stub.ReleaseSlot(request)
        return response.success