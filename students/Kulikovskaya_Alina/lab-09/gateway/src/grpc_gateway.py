"""
gRPC Gateway: трансляция REST запросов в gRPC вызовы.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
import grpc
import json
import asyncio

from generated import booking_pb2, booking_pb2_grpc
from generated import court_pb2, court_pb2_grpc

app = FastAPI(title="gRPC Gateway")

# gRPC каналы
BOOKING_CHANNEL = grpc.insecure_channel("booking-service:50051")
COURT_CHANNEL = grpc.insecure_channel("court-service:50051")

booking_stub = booking_pb2_grpc.BookingServiceStub(BOOKING_CHANNEL)
court_stub = court_pb2_grpc.CourtServiceStub(COURT_CHANNEL)


@app.post("/api/bookings")
async def create_booking(request: Request):
    """REST → gRPC CreateBooking."""
    data = await request.json()
    
    grpc_request = booking_pb2.CreateBookingRequest(
        user_id=data.get("user_id"),
        court_id=data.get("court_id"),
        slot_date=data.get("slot_date"),
        start_time=data.get("start_time"),
        end_time=data.get("end_time"),
        payment_method=data.get("payment_method", "online"),
        notes=data.get("notes", ""),
        idempotency_key=data.get("idempotency_key", "")
    )
    
    try:
        response = await booking_stub.CreateBooking(grpc_request)
        
        if not response.booking_id:
            raise HTTPException(status_code=400, detail="Ошибка создания")
        
        return {
            "booking_id": response.booking_id,
            "status": response.status,
            "total_amount": {
                "amount": response.total_amount.amount,
                "currency": response.total_amount.currency
            },
            "confirmation_code": response.confirmation_code
        }
        
    except grpc.RpcError as e:
        raise HTTPException(
            status_code=_grpc_code_to_http(e.code()),
            detail=e.details()
        )


@app.get("/api/bookings/{booking_id}")
async def get_booking(booking_id: str):
    """REST → gRPC GetBooking."""
    request = booking_pb2.GetBookingRequest(booking_id=booking_id)
    
    try:
        response = await booking_stub.GetBooking(request)
        
        if not response.booking_id:
            raise HTTPException(status_code=404, detail="Не найдено")
        
        return _booking_to_dict(response)
        
    except grpc.RpcError as e:
        raise HTTPException(
            status_code=_grpc_code_to_http(e.code()),
            detail=e.details()
        )


@app.get("/api/courts")
async def list_courts(type_filter: str = None):
    """REST → gRPC ListCourts."""
    request = court_pb2.ListCourtsRequest()
    
    if type_filter:
        type_map = {
            "volleyball": court_pb2.VOLLEYBALL,
            "basketball": court_pb2.BASKETBALL,
            "badminton": court_pb2.BADMINTON,
            "table_tennis": court_pb2.TABLE_TENNIS
        }
        request.type_filter = type_map.get(type_filter, court_pb2.COURT_TYPE_UNSPECIFIED)
    
    try:
        response = await court_stub.ListCourts(request)
        
        return {
            "courts": [
                {
                    "id": c.court_id,
                    "name": c.name,
                    "type": c.court_type,
                    "type_display": c.court_type_display,
                    "hourly_rate": c.hourly_rate.amount if c.hourly_rate else 0
                }
                for c in response.courts
            ]
        }
        
    except grpc.RpcError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/stream/bookings/{booking_id}/status")
async def stream_booking_status(booking_id: str):
    """Server-Sent Events → gRPC streaming."""
    request = booking_pb2.WatchBookingRequest(booking_id=booking_id)
    
    async def event_generator():
        try:
            async for update in booking_stub.WatchBookingStatus(request):
                yield f"data: {json.dumps({
                    'booking_id': update.booking_id,
                    'status': update.status,
                    'message': update.status_message,
                    'updated_at': update.updated_at
                })}\n\n"
                
        except grpc.RpcError as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


def _booking_to_dict(response: booking_pb2.BookingResponse) -> dict:
    """Конвертация protobuf в dict."""
    return {
        "booking_id": response.booking_id,
        "user_id": response.user_id,
        "court_id": response.court_id,
        "slot": {
            "date": response.slot_date,
            "start_time": response.start_time,
            "end_time": response.end_time
        },
        "status": response.status,
        "status_display": response.status_display,
        "total_amount": {
            "amount": response.total_amount.amount,
            "currency": response.total_amount.currency
        },
        "payment_id": response.payment_id,
        "confirmation_code": response.confirmation_code,
        "can_cancel": response.can_cancel,
        "created_at": response.created_at
    }


def _grpc_code_to_http(code: grpc.StatusCode) -> int:
    """Маппинг gRPC кодов в HTTP."""
    mapping = {
        grpc.StatusCode.OK: 200,
        grpc.StatusCode.CANCELLED: 499,
        grpc.StatusCode.UNKNOWN: 500,
        grpc.StatusCode.INVALID_ARGUMENT: 400,
        grpc.StatusCode.DEADLINE_EXCEEDED: 504,
        grpc.StatusCode.NOT_FOUND: 404,
        grpc.StatusCode.ALREADY_EXISTS: 409,
        grpc.StatusCode.PERMISSION_DENIED: 403,
        grpc.StatusCode.RESOURCE_EXHAUSTED: 429,
        grpc.StatusCode.FAILED_PRECONDITION: 400,
        grpc.StatusCode.ABORTED: 409,
        grpc.StatusCode.OUT_OF_RANGE: 400,
        grpc.StatusCode.UNIMPLEMENTED: 501,
        grpc.StatusCode.INTERNAL: 500,
        grpc.StatusCode.UNAVAILABLE: 503,
        grpc.StatusCode.DATA_LOSS: 500,
        grpc.StatusCode.UNAUTHENTICATED: 401,
    }
    return mapping.get(code, 500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)