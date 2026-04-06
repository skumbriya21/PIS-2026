from datetime import date, time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from application.commands.create_booking_command import CreateBookingCommand
from application.commands.cancel_booking_command import CancelBookingCommand
from application.dto.booking_dto import BookingDTO, BookingListItemDTO

from infrastructure.api.deps import get_booking_service


router = APIRouter()


class CreateBookingRequest(BaseModel):
    """Запрос на создание бронирования."""
    court_id: str = Field(..., description="ID площадки")
    date: date = Field(..., description="Дата бронирования")
    start_time: time = Field(..., description="Время начала (HH:00)")
    payment_method: str = Field(default="online", description="online или on_site")
    notes: Optional[str] = Field(default=None, description="Комментарий")


class BookingResponse(BaseModel):
    """Ответ с данными бронирования."""
    id: str
    status: str
    court_name: str
    date: date
    start_time: time
    total_amount: float
    currency: str = "BYN"
    payment_url: Optional[str] = None  # Для online оплаты


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    request: CreateBookingRequest,
    user_id: str,  # В реальности из JWT токена
    service=Depends(get_booking_service)
):
    """
    Создать новое бронирование.
    
    - Проверяет доступность слота
    - Блокирует слот на 10 минут
    - Возвращает ID для оплаты (если online)
    """
    command = CreateBookingCommand(
        user_id=user_id,
        court_id=request.court_id,
        date=request.date,
        start_time=request.start_time,
        end_time=time(request.start_time.hour + 1, 0),
        payment_method=request.payment_method,
        notes=request.notes
    )
    
    try:
        booking_id = await service.create_booking(command)
        booking = await service.get_booking(booking_id)
        
        return BookingResponse(
            id=booking.id,
            status=booking.status,
            court_name=booking.court_name,
            date=booking.date,
            start_time=booking.start_time,
            total_amount=booking.total_amount,
            currency=booking.currency,
            payment_url=f"/payment/{booking_id}" if request.payment_method == "online" else None
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{booking_id}", response_model=BookingDTO)
async def get_booking(
    booking_id: str,
    service=Depends(get_booking_service)
):
    """Получить детали бронирования."""
    booking = await service.get_booking(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено"
        )
    return booking


@router.get("/", response_model=List[BookingListItemDTO])
async def list_my_bookings(
    user_id: str,  # Из JWT
    service=Depends(get_booking_service)
):
    """Получить список моих бронирований."""
    return await service.list_user_bookings(user_id)


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: str,
    user_id: str,  # Из JWT
    reason: Optional[str] = None,
    service=Depends(get_booking_service)
):
    """Отменить бронирование."""
    command = CancelBookingCommand(
        booking_id=booking_id,
        user_id=user_id,
        reason=reason
    )
    
    try:
        await service.cancel_booking(command)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )