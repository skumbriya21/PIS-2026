"""
gRPC сервер Booking Service.
"""

import grpc
from datetime import datetime
from typing import AsyncIterator

from generated import booking_pb2, booking_pb2_grpc
from application.ports.inn.booking_service import IBookingService


class BookingGrpcServicer(booking_pb2_grpc.BookingServiceServicer):
    """Реализация BookingService gRPC."""
    
    def __init__(self, booking_service: IBookingService):
        self._service = booking_service
    
    async def CreateBooking(
        self, 
        request: booking_pb2.CreateBookingRequest, 
        context: grpc.ServicerContext
    ) -> booking_pb2.BookingResponse:
        """Создать бронирование."""
        try:
            # Валидация входных данных
            if not request.user_id or not request.court_id:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details("user_id и court_id обязательны")
                return booking_pb2.BookingResponse()
            
            # Создание через сервис
            booking_id = await self._service.create_booking(
                user_id=request.user_id,
                court_id=request.court_id,
                slot_date=request.slot_date,
                slot_time=request.start_time,
                amount=0  # Рассчитается сервисом
            )
            
            # Получаем созданное бронирование
            booking = await self._service.get_booking(booking_id)
            
            return self._to_proto_response(booking)
            
        except ValueError as e:
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details(str(e))
            return booking_pb2.BookingResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Внутренняя ошибка: {str(e)}")
            return booking_pb2.BookingResponse()
    
    async def GetBooking(
        self,
        request: booking_pb2.GetBookingRequest,
        context: grpc.ServicerContext
    ) -> booking_pb2.BookingResponse:
        """Получить бронирование."""
        booking = await self._service.get_booking(request.booking_id)
        
        if not booking:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Бронирование {request.booking_id} не найдено")
            return booking_pb2.BookingResponse()
        
        return self._to_proto_response(booking)
    
    async def CancelBooking(
        self,
        request: booking_pb2.CancelBookingRequest,
        context: grpc.ServicerContext
    ) -> booking_pb2.BookingResponse:
        """Отменить бронирование."""
        try:
            from application.commands.cancel_booking_command import CancelBookingCommand
            
            command = CancelBookingCommand(
                booking_id=request.booking_id,
                user_id=request.user_id,
                reason=request.reason,
                force=request.force
            )
            
            await self._service.cancel_booking(command)
            booking = await self._service.get_booking(request.booking_id)
            
            return self._to_proto_response(booking)
            
        except ValueError as e:
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details(str(e))
            return booking_pb2.BookingResponse()
    
    async def ConfirmPayment(
        self,
        request: booking_pb2.ConfirmPaymentRequest,
        context: grpc.ServicerContext
    ) -> booking_pb2.BookingResponse:
        """Подтвердить оплату."""
        try:
            await self._service.confirm_payment(
                request.booking_id,
                request.payment_id
            )
            booking = await self._service.get_booking(request.booking_id)
            return self._to_proto_response(booking)
            
        except ValueError as e:
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            context.set_details(str(e))
            return booking_pb2.BookingResponse()
    
    async def ListUserBookings(
        self,
        request: booking_pb2.ListUserBookingsRequest,
        context: grpc.ServicerContext
    ) -> booking_pb2.BookingListResponse:
        """Список бронирований пользователя."""
        bookings = await self._service.list_user_bookings(request.user_id)
        
        return booking_pb2.BookingListResponse(
            bookings=[self._to_proto_response(b) for b in bookings],
            pagination=booking_pb2.PaginationResponse(
                total_count=len(bookings),
                current_page=request.pagination.page or 1,
                total_pages=1,
                has_next=False,
                has_previous=False
            )
        )
    
    async def CheckAvailability(
        self,
        request_iterator: AsyncIterator[booking_pb2.CheckAvailabilityRequest],
        context: grpc.ServicerContext
    ) -> AsyncIterator[booking_pb2.AvailabilityResponse]:
        """
        Streaming RPC: клиент отправляет несколько запросов,
        сервер отвечает на каждый.
        """
        async for request in request_iterator:
            # Проверяем через Court Service (gRPC клиент)
            is_available = await self._check_court_availability(
                request.court_id,
                request.date,
                request.preferred_time
            )
            
            # Ищем альтернативы если занят
            alternatives = []
            if not is_available and request.flexibility_hours > 0:
                alternatives = await self._find_alternatives(
                    request.court_id,
                    request.date,
                    request.preferred_time,
                    request.flexibility_hours
                )
            
            yield booking_pb2.AvailabilityResponse(
                court_id=request.court_id,
                date=request.date,
                is_available=is_available,
                alternative_slots=alternatives
            )
    
    async def WatchBookingStatus(
        self,
        request: booking_pb2.WatchBookingRequest,
        context: grpc.ServicerContext
    ) -> AsyncIterator[booking_pb2.BookingStatusUpdate]:
        """
        Server Streaming: клиент подписывается на обновления статуса.
        """
        import asyncio
        
        booking_id = request.booking_id
        
        while True:
            # Проверяем, не отменён ли контекст
            if context.is_active():
                break
            
            booking = await self._service.get_booking(booking_id)
            if not booking:
                break
            
            yield booking_pb2.BookingStatusUpdate(
                booking_id=booking_id,
                status=self._map_status(booking['status']),
                status_message=self._get_status_message(booking['status']),
                updated_at=datetime.now().isoformat()
            )
            
            # Отправляем обновления каждые 5 секунд
            await asyncio.sleep(5)
    
    def _to_proto_response(self, booking: dict) -> booking_pb2.BookingResponse:
        """Конвертация доменного объекта в protobuf."""
        from generated import common_pb2
        
        return booking_pb2.BookingResponse(
            booking_id=booking['id'],
            user_id=booking['user_id'],
            court_id=booking['court_id'],
            slot_date=booking['slot_date'],
            start_time=booking['slot_time'],
            end_time=booking.get('slot_end_time', ''),
            status=self._map_status(booking['status']),
            status_display=self._get_status_display(booking['status']),
            total_amount=common_pb2.Money(
                amount=booking['total_amount'],
                currency=booking.get('currency', 'BYN')
            ),
            payment_id=booking.get('payment_id', ''),
            confirmation_code=booking['id'][:8].upper(),
            can_cancel=booking['status'] in ('pending_payment', 'confirmed'),
            hours_until_start=int(booking.get('hours_until_start', 0))
        )
    
    def _map_status(self, status: str) -> booking_pb2.BookingStatus:
        """Маппинг строкового статуса в enum."""
        mapping = {
            'pending_payment': booking_pb2.PENDING_PAYMENT,
            'reserved': booking_pb2.RESERVED,
            'confirmed': booking_pb2.CONFIRMED,
            'cancelled': booking_pb2.CANCELLED,
            'expired': booking_pb2.EXPIRED,
        }
        return mapping.get(status, booking_pb2.BOOKING_STATUS_UNSPECIFIED)
    
    def _get_status_display(self, status: str) -> str:
        """Человекочитаемый статус."""
        displays = {
            'pending_payment': 'Ожидает оплаты',
            'reserved': 'Зарезервировано',
            'confirmed': 'Подтверждено',
            'cancelled': 'Отменено',
            'expired': 'Истекло',
        }
        return displays.get(status, status)
    
    def _get_status_message(self, status: str) -> str:
        """Сообщение для статуса."""
        messages = {
            'pending_payment': 'Ожидаем вашу оплату',
            'confirmed': 'Ждём вас на площадке!',
            'cancelled': 'Бронирование отменено',
        }
        return messages.get(status, '')
    
    async def _check_court_availability(
        self, court_id: str, date: str, time: str
    ) -> bool:
        """Проверка через Court Service gRPC клиент."""
        # Реализация через gRPC клиент
        from infrastructure.grpc.court_grpc_client import CourtGrpcClient
        
        client = CourtGrpcClient()
        return await client.check_availability(court_id, date, time)
    
    async def _find_alternatives(
        self, court_id: str, date: str, preferred_time: str, flexibility: int
    ) -> list:
        """Поиск альтернативных слотов."""
        # Реализация
        return []


async def serve_grpc(booking_service, port=50051):
    """Запуск gRPC сервера."""
    from concurrent import futures
    
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    
    booking_pb2_grpc.add_BookingServiceServicer_to_server(
        BookingGrpcServicer(booking_service), server
    )
    
    server.add_insecure_port(f'[::]:{port}')
    await server.start()
    
    print(f"✅ Booking gRPC сервер запущен на порту {port}")
    await server.wait_for_termination()