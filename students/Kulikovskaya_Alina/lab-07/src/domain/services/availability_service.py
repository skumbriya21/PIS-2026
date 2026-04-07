from datetime import date, time
from typing import List, Optional

from domain.models.court import Court
from domain.models.value_objects.court_type import CourtType
from domain.models.value_objects.slot import Slot


class AvailabilityService:
    """
    Доменный сервис: проверка доступности слотов.
    
    Инкапсулирует логику поиска свободных слотов
    без привязки к конкретному хранилищу.
    """
    
    OPENING_HOUR = 8   # 08:00
    CLOSING_HOUR = 23  # 23:00 (последний слот 22:00-23:00)
    
    def __init__(self, schedule_repository):
        self._schedule_repo = schedule_repository
    
    def find_available_slots(self, court: Court, date: date) -> List[Slot]:
        """Найти все доступные слоты для площадки на дату."""
        if not court.is_active:
            return []
        
        return self._schedule_repo.get_available_slots(court.id, date)
    
    def is_slot_available(self, court_id: str, date: date, 
                          start_time: time) -> bool:
        """Проверить доступность конкретного слота."""
        return self._schedule_repo.is_available(court_id, date, start_time)
    
    def find_alternative_slots(self, court_type: CourtType, date: date,
                               preferred_time: time, 
                               court_repository,
                               hours_range: int = 2) -> List[Slot]:
        """
        Найти альтернативные слоты рядом с предпочтительным временем.
        
        Используется при конфликтах (race condition).
        """
        alternatives = []
        
        # Ищем слоты ± hours_range часов от предпочтительного времени
        preferred_hour = preferred_time.hour
        
        for hour_offset in range(-hours_range, hours_range + 1):
            check_hour = preferred_hour + hour_offset
            if self.OPENING_HOUR <= check_hour < self.CLOSING_HOUR:
                check_time = time(check_hour, 0)
                
                # Проверяем все площадки данного типа
                courts = court_repository.find_by_type(court_type)
                for court in courts:
                    if self.is_slot_available(court.id, date, check_time):
                        slot = Slot(
                            court_id=court.id,
                            date=date,
                            start_time=check_time,
                            end_time=time(check_hour + 1, 0)
                        )
                        alternatives.append(slot)
                        break  # Достаточно одного корта на это время
        
        return alternatives