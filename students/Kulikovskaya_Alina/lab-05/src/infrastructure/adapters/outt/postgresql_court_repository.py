# PostgreSQL реализация репозитория площадок

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.court import Court
from domain.models.value_objects.court_type import CourtType
from application.ports.outt.court_repository import ICourtRepository

from infrastructure.database.models.court_model import CourtModel


class PostgreSQLCourtRepository(ICourtRepository):
    # PostgreSQL реализация репозитория площадок
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    def _to_domain(self, model: CourtModel) -> Court:
        # Конвертация ORM в домен
        return Court(
            id=model.id,
            name=model.name,
            court_type=CourtType.from_code(model.court_type),
            description=model.description,
            is_active=model.is_active
        )
    
    async def save(self, court: Court) -> None:
        # Сохранить площадку
        result = await self._session.execute(
            select(CourtModel).where(CourtModel.id == court.id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.name = court.name
            existing.is_active = court.is_active
            existing.description = court.description or ""
        else:
            model = CourtModel(
                id=court.id,
                name=court.name,
                court_type=court.court_type.code,
                hourly_rate=court.court_type.hourly_rate,
                description=court.description or "",
                is_active=court.is_active
            )
            self._session.add(model)
        
        await self._session.commit()
    
    async def find_by_id(self, court_id: str) -> Optional[Court]:
        # Найти площадку по ID
        result = await self._session.execute(
            select(CourtModel).where(CourtModel.id == court_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None
    
    async def find_by_type(self, court_type: CourtType) -> List[Court]:
        # Найти площадки по типу
        result = await self._session.execute(
            select(CourtModel).where(CourtModel.court_type == court_type.code)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]
    
    async def find_all_active(self) -> List[Court]:
        # Найти все активные площадки
        result = await self._session.execute(
            select(CourtModel).where(CourtModel.is_active == True)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]