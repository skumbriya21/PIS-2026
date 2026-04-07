# Управление сессиями базы данных

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from infrastructure.config.settings import settings


# Создание движка
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db_session() -> AsyncSession:
    # Получить сессию БД (для dependency injection)
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()