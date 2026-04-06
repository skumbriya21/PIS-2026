from typing import List, Optional

from domain.models.booking import Booking
from domain.models.value_objects.slot import Slot


class ConflictChecker:
    """
    Доменный сервис: проверка конфликтов бронирований.
    
    Оптимистичная блокировка: проверяем перед созданием,
    но финальная проверка в БД (Lab #5).
    """
    
    def check_conflicts(self, proposed_slot: Slot, 
                        existing_bookings: List[Booking]) -> Optional[str]:
        """
        Проверить, есть ли конфликты с существующими бронированиями.
        
        Returns:
            Описание конфликта или None если конфликтов нет
        """
        for booking in existing_bookings:
            # Пропускаем отменённые и истёкшие
            if booking.status.value in ('cancelled', 'expired'):
                continue
            
            if booking.slot.overlaps(proposed_slot):
                return (
                    f"Конфликт с бронированием {booking.id}: "
                    f"{booking.slot.start_time}-{booking.slot.end_time}"
                )
        
        return None
    
    def has_double_booking(self, user_id: str, proposed_slot: Slot,
                          user_existing_bookings: List[Booking]) -> bool:
        """
        Проверить, не пытается ли пользователь забронировать 
        два пересекающихся слота.
        """
        for booking in user_existing_bookings:
            if booking.status.value in ('cancelled', 'expired'):
                continue
            
            if booking.slot.overlaps(proposed_slot):
                return True
        
        return False