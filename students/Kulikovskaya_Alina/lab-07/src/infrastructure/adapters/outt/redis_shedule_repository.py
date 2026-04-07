"""
Redis реализация репозитория расписания (блокировки слотов).
"""

from datetime import date, time
from typing import List
import json

import redis.asyncio as redis

from domain.models.value_objects.slot import Slot
from application.ports.outt.schedule_repository import IScheduleRepository


class RedisScheduleRepository(IScheduleRepository):
    # Redis реализация для блокировок и доступности слотов
    
    # TTL для блокировки (секунды)
    LOCK_TTL = 600  # 10 минут
    
    def __init__(self, redis_client: redis.Redis):
        self._redis = redis_client
    
    def _key(self, court_id: str, slot_date: date, start_time: time) -> str:
        # Сформировать ключ Redis
        return f"slot:{court_id}:{slot_date.isoformat()}:{start_time.strftime('%H:%M')}"
    
    def _confirmed_key(self, court_id: str, slot_date: date) -> str:
        # Ключ для подтверждённых бронирований на дату
        return f"confirmed:{court_id}:{slot_date.isoformat()}"
    
    async def is_available(self, court_id: str, date: date, start_time: time) -> bool:
        # Проверить, свободен ли слот
        key = self._key(court_id, date, start_time)
        
        # Проверяем блокировку
        lock_exists = await self._redis.exists(key)
        if lock_exists:
            return False
        
        # Проверяем подтверждённые брони
        confirmed_key = self._confirmed_key(court_id, date)
        slot_str = start_time.strftime('%H:%M')
        is_confirmed = await self._redis.sismember(confirmed_key, slot_str)
        
        return not is_confirmed
    
    async def lock_slot(self, court_id: str, date: date, start_time: time,
                       booking_id: str, ttl_minutes: int = 10) -> bool:
        # Заблокировать слот
        key = self._key(court_id, date, start_time)
        
        # NX = только если не существует
        success = await self._redis.set(
            key, 
            booking_id, 
            nx=True, 
            ex=ttl_minutes * 60
        )
        return success is not None
    
    async def unlock_slot(self, court_id: str, date: date, start_time: time) -> None:
        # Снять блокировку
        key = self._key(court_id, date, start_time)
        await self._redis.delete(key)
    
    async def confirm_slot(self, court_id: str, date: date, start_time: time) -> None:
        # Подтвердить бронирование слота
        # Убираем блокировку
        await self.unlock_slot(court_id, date, start_time)
        
        # Добавляем в подтверждённые
        confirmed_key = self._confirmed_key(court_id, date)
        slot_str = start_time.strftime('%H:%M')
        await self._redis.sadd(confirmed_key, slot_str)
    
    async def get_available_slots(self, court_id: str, date: date) -> List[Slot]:
        # Получить список доступных слотов на дату
        available = []
        
        for hour in range(8, 23):  # 08:00 - 22:00
            start = time(hour, 0)
            end = time(hour + 1, 0)
            
            if await self.is_available(court_id, date, start):
                available.append(Slot(
                    court_id=court_id,
                    date=date,
                    start_time=start,
                    end_time=end
                ))
        
        return available