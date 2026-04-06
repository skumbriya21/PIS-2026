from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.config.settings import settings
from infrastructure.database.session import engine
from infrastructure.database.base import Base

from infrastructure.api.routes import courts, bookings, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Startup: создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


def create_app() -> FastAPI:
    """Фабрика приложения FastAPI."""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API для бронирования спортивных площадок в манеже",
        lifespan=lifespan
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # В продакшене указать конкретные домены
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Роуты
    app.include_router(courts.router, prefix="/api/courts", tags=["courts"])
    app.include_router(bookings.router, prefix="/api/bookings", tags=["bookings"])
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
    
    @app.get("/health")
    async def health_check():
        """Проверка здоровья сервиса."""
        return {"status": "ok", "version": settings.APP_VERSION}
    
    return app