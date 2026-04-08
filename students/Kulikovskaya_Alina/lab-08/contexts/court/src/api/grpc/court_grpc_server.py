import grpc
from concurrent import futures
from generated import court_pb2, court_pb2_grpc

from application.ports.inn.court_service import ICourtService


class CourtGrpcServicer(court_pb2_grpc.CourtServiceServicer):
    """gRPC сервис площадок."""
    
    def __init__(self, court_service: ICourtService):
        self._service = court_service
    
    async def GetCourt(self, request, context):
        """Получить площадку."""
        court = await self._service.get_court(request.court_id)
        
        if not court:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Площадка не найдена")
            return court_pb2.CourtResponse()
        
        return court_pb2.CourtResponse(
            court_id=court["id"],
            name=court["name"],
            court_type=court["court_type"],
            description=court.get("description", ""),
            is_active=court["is_active"],
            hourly_rate=court["hourly_rate"]
        )
    
    async def ListCourts(self, request, context):
        """Список площадок."""
        courts = await self._service.list_courts(
            request.court_type if request.court_type else None
        )
        
        return court_pb2.CourtListResponse(
            courts=[
                court_pb2.CourtResponse(
                    court_id=c["id"],
                    name=c["name"],
                    court_type=c["court_type"],
                    is_active=c["is_active"],
                    hourly_rate=c["hourly_rate"]
                )
                for c in courts
            ]
        )
    
    async def CheckAvailability(self, request, context):
        """Проверить доступность."""
        is_available = await self._service.check_availability(
            request.court_id, request.date, request.start_time
        )
        
        return court_pb2.AvailabilityResponse(is_available=is_available)
    
    async def ReserveSlot(self, request, context):
        """Зарезервировать слот."""
        # В реальности booking_id передаётся в метаданных или отдельным полем
        success = await self._service.reserve_slot(
            request.court_id, request.date, request.start_time,
            booking_id="temp"  # Заглушка
        )
        
        return court_pb2.ReserveSlotResponse(success=success)
    
    async def ReleaseSlot(self, request, context):
        """Освободить слот."""
        success = await self._service.release_slot(
            request.court_id, request.date, request.start_time
        )
        
        return court_pb2.ReleaseSlotResponse(success=success)


async def serve_grpc(court_service, port=50051):
    """Запуск gRPC сервера."""
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    court_pb2_grpc.add_CourtServiceServicer_to_server(
        CourtGrpcServicer(court_service), server
    )
    server.add_insecure_port(f'[::]:{port}')
    await server.start()
    print(f"Court gRPC сервер на порту {port}")
    await server.wait_for_termination()