from typing import List, Optional

from domain.models.court import Court, Slot


class CourtServiceImpl:
    """Реализация сервиса площадок."""
    
    def __init__(self, repository):
        self._repo = repository
    
    async def get_court(self, court_id: str) -> Optional[dict]:
        """Получить площадку."""
        court = await self._repo.find_by_id(court_id)
        return self._to_dict(court) if court else None
    
    async def list_courts(self, court_type: Optional[str] = None) -> List[dict]:
        """Список площадок."""
        courts = await self._repo.find_all(court_type)
        return [self._to_dict(c) for c in courts]
    
    async def check_availability(
        self, court_id: str, date: str, start_time: str
    ) -> bool:
        """Проверить доступность."""
        slot = await self._repo.find_slot(court_id, date, start_time)
        return slot.is_available if slot else False
    
    async def reserve_slot(
        self, court_id: str, date: str, start_time: str, booking_id: str
    ) -> bool:
        """Зарезервировать слот."""
        slot = await self._repo.find_slot(court_id, date, start_time)
        if not slot or not slot.is_available:
            return False
        
        slot.reserve(booking_id)
        await self._repo.save_slot(slot)
        return True
    
    async def release_slot(self, court_id: str, date: str, start_time: str) -> bool:
        """Освободить слот."""
        slot = await self._repo.find_slot(court_id, date, start_time)
        if not slot:
            return False
        
        slot.release()
        await self._repo.save_slot(slot)
        return True
    
    def _to_dict(self, court: Court) -> dict:
        """Конвертация в словарь."""
        return {
            "id": court.id,
            "name": court.name,
            "court_type": court.court_type,
            "description": court.description,
            "is_active": court.is_active,
            "hourly_rate": court.hourly_rate,
            "amenities": court.amenities
        }