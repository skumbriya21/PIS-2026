# Настройки приложения из переменных окружения.

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Конфигурация приложения
    
    # App
    APP_NAME: str = "Бронь манежа 'Свободна площадка?'"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/manezh_booking"
    DATABASE_ECHO: bool = False  # Логирование SQL запросов
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Payment (Mock для разработки)
    PAYMENT_GATEWAY_URL: str = "https://api.yookassa.ru/v3"
    PAYMENT_SHOP_ID: str = ""
    PAYMENT_SECRET_KEY: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    # Получить настройки
    return Settings()


settings = get_settings()