from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from application.dto.court_dto import CourtDTO, CourtAvailabilityDTO
from application.dto.slot_dto import SlotDTO

from infrastructure.api.deps import get_court_repository, get_schedule_repository


router = APIRouter()


@router.get("/", response_model=List[CourtDTO])
async def list_courts(
    court_type: str = None,
    repo=Depends(get_court_repository)
):
    """Получить список площадок."""
    if court_type:
        from domain.models.value_objects.court_type import CourtType
        courts = await repo.find_by_type(CourtType.from_code(court_type))
    else:
        courts = await repo.find_all_active()
    
    return [
        CourtDTO(
            id=c.id,
            name=c.name,
            court_type=c.court_type.code,
            court_type_display=c.court_type.display_name,
            hourly_rate=c.court_type.hourly_rate,
            is_active=c.is_active,
            description=c.description or ""
        )
        for c in courts
    ]


@router.get("/{court_id}/availability", response_model=CourtAvailabilityDTO)
async def get_court_availability(
    court_id: str,
    date: date,
    court_repo=Depends(get_court_repository),
    schedule_repo=Depends(get_schedule_repository)
):
    """Получить доступные слоты для площадки на дату."""
    court = await court_repo.find_by_id(court_id)
    if not court:
        raise HTTPException(status_code=404, detail="Площадка не найдена")
    
    slots = await schedule_repo.get_available_slots(court_id, date)
    
    from domain.services.pricing_service import PricingService
    pricing = PricingService()
    
    return CourtAvailabilityDTO(
        court=CourtDTO(
            id=court.id,
            name=court.name,
            court_type=court.court_type.code,
            court_type_display=court.court_type.display_name,
            hourly_rate=court.court_type.hourly_rate,
            is_active=court.is_active
        ),
        date=date,
        available_slots=[
            SlotDTO(
                start_time=s.start_time,
                end_time=s.end_time,
                is_available=True,
                price=pricing.calculate_price(
                    court.court_type, date, s.start_time
                ).amount
            )
            for s in slots
        ]
    )