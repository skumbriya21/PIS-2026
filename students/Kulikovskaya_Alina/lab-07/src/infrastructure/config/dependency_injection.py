# DI Container - связывание всех компонентов.

from infrastructure.adapters.outt.in_memory_booking_repository import InMemoryBookingRepository
from infrastructure.adapters.outt.in_memory_court_repository import InMemoryCourtRepository
from infrastructure.adapters.outt.in_memory_schedule_repository import InMemoryScheduleRepository
from infrastructure.adapters.outt.in_memory_user_repository import InMemoryUserRepository
from infrastructure.adapters.outt.mock_payment_gateway import MockPaymentGateway
from infrastructure.adapters.outt.mock_notification_service import MockNotificationService

from application.services.booking_service_impl import BookingServiceImpl
from application.services.admin_service_impl import AdminServiceImpl

from infrastructure.adapters.inn.booking_controller import BookingController
from infrastructure.adapters.inn.admin_controller import AdminController


class DIContainer:
    # DI-контейнер с полной инициализацией
    
    def __init__(self):
        # Repositories (Outgoing Adapters)
        self.booking_repository = InMemoryBookingRepository()
        self.court_repository = InMemoryCourtRepository()
        self.schedule_repository = InMemoryScheduleRepository()
        self.user_repository = InMemoryUserRepository()
        
        # External Services (Outgoing Adapters)
        self.payment_gateway = MockPaymentGateway(failure_rate=0.1)
        self.notification_service = MockNotificationService()
        
        # Application Services
        self.booking_service = BookingServiceImpl(
            booking_repository=self.booking_repository,
            court_repository=self.court_repository,
            schedule_repository=self.schedule_repository,
            payment_gateway=self.payment_gateway,
            notification_service=self.notification_service
        )
        
        self.admin_service = AdminServiceImpl(
            booking_repository=self.booking_repository,
            court_repository=self.court_repository,
            schedule_repository=self.schedule_repository,
            notification_service=self.notification_service
        )
        
        # Controllers (Incoming Adapters)
        self.booking_controller = BookingController(self.booking_service)
        self.admin_controller = AdminController(self.admin_service)
    
    # Геттеры для доступа извне
    def get_booking_service(self):
        return self.booking_service
    
    def get_admin_service(self):
        return self.admin_service
    
    def get_booking_controller(self):
        return self.booking_controller
    
    def get_admin_controller(self):
        return self.admin_controller


# Singleton
container = DIContainer()