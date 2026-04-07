from typing import List

from domain.models.booking import Booking
from domain.models.value_objects.booking_status import BookingStatus
from domain.factories.booking_factory import BookingFactory
from domain.services.pricing_service import PricingService
from domain.exceptions.domain_exception import DomainException

from application.ports.inn.admin_service import IAdminService
from application.ports.outt.booking_repository import IBookingRepository
from application.ports.outt.court_repository import ICourtRepository
from application.ports.outt.schedule_repository import IScheduleRepository
from application.ports.outt.notification_service import INotificationService

from application.commands.create_phone_booking_command import CreatePhoneBookingCommand
from application.dto.booking_dto import BookingDTO, BookingListItemDTO


class AdminServiceImpl(IAdminService):
    # Application Service для операций администратора
    
    def __init__(
        self,
        booking_repository: IBookingRepository,
        court_repository: ICourtRepository,
        schedule_repository: IScheduleRepository,
        notification_service: INotificationService
    ):
        self._booking_repo = booking_repository
        self._court_repo = court_repository
        self._schedule_repo = schedule_repository
        self._notification_service = notification_service
        
        self._factory = BookingFactory(PricingService())
    
    def create_phone_booking(self, command: CreatePhoneBookingCommand) -> str:
        """
        Создать бронирование по телефону (администратором).
        
        Особенности:
        - Сразу CONFIRMED (без online-оплаты)
        - Слот сразу подтверждён (не заблокирован)
        - Отправляется SMS клиенту
        """
        # Проверка площадки
        court = self._court_repo.find_by_id(command.court_id)
        if court is None:
            raise DomainException("Площадка не найдена")
        
        # Проверка доступности
        if not self._schedule_repo.is_available(
            command.court_id, command.date, command.start_time
        ):
            raise DomainException("Слот занят")
        
        # Создание бронирования
        booking = self._factory.create_phone_booking(
            admin_id=command.admin_id,
            court_id=command.court_id,
            slot_date=command.date,
            start_time=command.start_time,
            court_type=court.court_type,
            customer_name=command.customer_name,
            customer_phone=command.customer_phone,
            notes=command.notes
        )
        
        # Сразу подтверждаем слот (не блокируем, а сразу занимаем)
        self._schedule_repo.confirm_slot(
            command.court_id, command.date, command.start_time
        )
        
        # Сохранение
        self._booking_repo.save(booking)
        
        # Отправка SMS клиенту
        self._notification_service.send_sms(
            to_phone=command.customer_phone,
            message=f"Здравствуйте, {command.customer_name}! "
                   f"Забронирован {court.name} на {command.date} "
                   f"в {command.start_time.strftime('%H:%M')}. "
                   f"Ждём вас! Оплата на месте."
        )
        
        return booking.id
    
    def cancel_any_booking(self, booking_id: str, reason: str) -> None:
        # Отменить любое бронирование (админская функция)
        from application.commands.cancel_booking_command import CancelBookingCommand
        
        booking = self._booking_repo.find_by_id(booking_id)
        if booking is None:
            raise DomainException("Бронирование не найдено")
        
        # Админ может отменить всё (force=True)
        booking.cancel(reason=reason, cancelled_by="admin", force=True)
        
        # Освобождение слота
        self._schedule_repo.unlock_slot(
            booking.court_id,
            booking.slot.date,
            booking.slot.start_time
        )
        
        self._booking_repo.save(booking)
    
    def get_all_bookings(self, date=None) -> List[BookingListItemDTO]:
        # Получить все бронирования (с опциональным фильтром по дате)
        # TODO: добавить метод в репозиторий для получения всех
        # Пока заглушка
        return []
    
    def block_slot(self, court_id: str, date, start_time: str, reason: str) -> None:
        # Заблокировать слот для технического обслуживания
        # TODO: реализовать блокировку без бронирования
        pass