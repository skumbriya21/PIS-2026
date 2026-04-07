from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from application.read_models.booking_read_model import BookingReadModel, BookingListView


class IBookingReadRepository(ABC):
    """
    Репозиторий чтения для бронирований.
    
    Оптимизирован для сложных запросов с фильтрами и сортировкой.
    """
    
    @abstractmethod
    def get_by_id(self, booking_id: str) -> Optional[BookingReadModel]:
        """Получить бронирование по ID."""
        pass
    
    @abstractmethod
    def list_by_user(
        self, 
        user_id: str,
        status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[BookingListView]:
        """
        Список бронирований пользователя с фильтрами.
        
        Поддерживает:
        - Фильтрацию по статусу
        - Диапазон дат
        - Пагинацию
        """
        pass
    
    @abstractmethod
    def list_by_court(
        self,
        court_id: str,
        date: Optional[date] = None,
        status: Optional[str] = None
    ) -> List[BookingReadModel]:
        """Список бронирований площадки."""
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,  # Поиск по имени пользователя, email, телефону
        court_type: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> List[BookingReadModel]:
        """Полнотекстовый поиск бронирований."""
        pass
    
    @abstractmethod
    def get_upcoming_for_reminders(self, hours_ahead: int = 24) -> List[BookingReadModel]:
        """Получить бронирования для отправки напоминаний."""
        pass