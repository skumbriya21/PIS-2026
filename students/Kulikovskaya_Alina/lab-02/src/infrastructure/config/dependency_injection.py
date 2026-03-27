"""
DI Container - ручная реализация Dependency Injection.
"""

from src.infrastructure.adapters.outt.in_memory_booking_repository import InMemoryBookingRepository
from src.infrastructure.adapters.outt.in_memory_court_repository import InMemoryCourtRepository
from src.infrastructure.adapters.outt.in_memory_schedule_repository import InMemoryScheduleRepository
from src.infrastructure.adapters.outt.in_memory_user_repository import InMemoryUserRepository
from src.infrastructure.adapters.outt.mock_payment_gateway import MockPaymentGateway
from src.infrastructure.adapters.outt.mock_notification_service import MockNotificationService


class DIContainer:
    """Простой DI-контейнер."""
    
    def __init__(self):
        # Outgoing Adapters (реализации портов)
        self.booking_repository = InMemoryBookingRepository()
        self.court_repository = InMemoryCourtRepository()
        self.schedule_repository = InMemoryScheduleRepository()
        self.user_repository = InMemoryUserRepository()
        self.payment_gateway = MockPaymentGateway(failure_rate=0.1)
        self.notification_service = MockNotificationService()
    
    def get_booking_repository(self):
        return self.booking_repository
    
    def get_court_repository(self):
        return self.court_repository
    
    def get_schedule_repository(self):
        return self.schedule_repository
    
    def get_user_repository(self):
        return self.user_repository
    
    def get_payment_gateway(self):
        return self.payment_gateway
    
    def get_notification_service(self):
        return self.notification_service


# Singleton instance
container = DIContainer()