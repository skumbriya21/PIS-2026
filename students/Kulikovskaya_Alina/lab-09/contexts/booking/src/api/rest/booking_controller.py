from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from application.ports.inn.booking_service import IBookingService


app = FastAPI(title="Booking Service")


class CreateBookingRequest(BaseModel):
    user_id: str
    court_id: str
    slot_date: str  # YYYY-MM-DD
    slot_time: str  # HH:MM
    amount: float


class ConfirmBookingRequest(BaseModel):
    payment_id: str


class CancelBookingRequest(BaseModel):
    reason: Optional[str] = None


class BookingResponse(BaseModel):
    booking_id: str
    status: str
    total_amount: float
    currency: str


# Dependency injection (упрощённо)
_booking_service: IBookingService = None

def set_booking_service(service: IBookingService):
    global _booking_service
    _booking_service = service


@app.post("/bookings", response_model=BookingResponse, status_code=201)
async def create_booking(request: CreateBookingRequest):
    """Создать бронирование."""
    try:
        booking_id = await _booking_service.create_booking(
            user_id=request.user_id,
            court_id=request.court_id,
            slot_date=request.slot_date,
            slot_time=request.slot_time,
            amount=request.amount
        )
        
        return BookingResponse(
            booking_id=booking_id,
            status="pending_payment",
            total_amount=request.amount,
            currency="BYN"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/bookings/{booking_id}/confirm")
async def confirm_booking(booking_id: str, request: ConfirmBookingRequest):
    """Подтвердить бронирование."""
    try:
        await _booking_service.confirm_booking(booking_id, request.payment_id)
        return {"status": "confirmed"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/bookings/{booking_id}/cancel")
async def cancel_booking(booking_id: str, request: CancelBookingRequest):
    """Отменить бронирование."""
    try:
        await _booking_service.cancel_booking(booking_id, request.reason)
        return {"status": "cancelled"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/bookings/{booking_id}")
async def get_booking(booking_id: str):
    """Получить бронирование."""
    booking = await _booking_service.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    return booking


@app.get("/users/{user_id}/bookings")
async def list_user_bookings(user_id: str):
    """Список бронирований пользователя."""
    bookings = await _booking_service.list_user_bookings(user_id)
    return {"bookings": bookings}