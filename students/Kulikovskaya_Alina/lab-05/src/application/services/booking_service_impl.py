from datetime import datetime
from typing import List, Optional

from domain.models.booking import Booking
from domain.models.value_objects.booking_status import BookingStatus
from domain.factories.booking_factory import BookingFactory
from domain.services.pricing_service import PricingService
from domain.services.conflict_checker import ConflictChecker
from domain.specifications.cancellation_policy import CancellationPolicy
from domain.specifications.booking_rules import MinAdvanceBookingRule, PeakHoursRule
from domain.exceptions.domain_exception import DomainException, SlotNotAvailableException

from application.ports.inn.booking_service import IBookingService
from application.ports.outt.booking_repository import IBookingRepository
from application.ports.outt.court_repository import ICourtRepository
from application.ports.outt.schedule_repository import IScheduleRepository
from application.ports.outt.payment_gateway import IPaymentGateway
from application.ports.outt.notification_service import INotificationService

from application.commands.create_booking_command import CreateBookingCommand
from application.commands.cancel_booking_command import CancelBookingCommand
from application.commands.confirm_payment_command import ConfirmPaymentCommand
from application.dto.booking_dto import BookingDTO, BookingListItemDTO


class BookingServiceImpl(IBookingService):
    """
    Application Service: реализация use cases для бронирования.
    
    Координирует:
    - Domain objects (Booking, Slot, Money)
    - Repositories (чтение/запись)
    - Domain Services (Pricing, ConflictChecker)
    - Specifications (CancellationPolicy, BookingRules)
    - External services (Payment, Notification)
    """
    
    def __init__(
        self,
        booking_repository: IBookingRepository,
        court_repository: ICourtRepository,
        schedule_repository: IScheduleRepository,
        payment_gateway: IPaymentGateway,
        notification_service: INotificationService
    ):
        self._booking_repo = booking_repository
        self._court_repo = court_repository
        self._schedule_repo = schedule_repository
        self._payment_gateway = payment_gateway
        self._notification_service = notification_service
        
        # Domain services
        self._pricing = PricingService()
        self._conflict_checker = ConflictChecker()
        self._factory = BookingFactory(self._pricing)
        
        # Specifications
        self._cancellation_policy = CancellationPolicy()
        self._min_advance_rule = MinAdvanceBookingRule()
        self._peak_rule = PeakHoursRule()
    
    # Commands
    
    def create_booking(self, command: CreateBookingCommand) -> str:
        """
        Создать online-бронирование с оплатой.
        
        Algorithm:
        1. Проверить существование площадки
        2. Проверить бизнес-правила (минимум 30 минут до начала)
        3. Проверить доступность слота
        4. Проверить конфликты с другими бронированиями
        5. Заблокировать слот
        6. Создать бронирование через Factory
        7. Сохранить в БД
        8. Вернуть ID для редиректа на оплату
        """
        # 1. Проверка площадки
        court = self._court_repo.find_by_id(command.court_id)
        if court is None:
            raise DomainException(f"Площадка {command.court_id} не найдена")
        
        if not court.is_active:
            raise DomainException("Площадка временно недоступна")
        
        # 2. Проверка бизнес-правил
        if not self._min_advance_rule.is_satisfied(
            court.court_type, command.date, command.start_time
        ):
            raise DomainException(self._min_advance_rule.error_message())
        
        # 3. Проверка доступности слота
        if not self._schedule_repo.is_available(
            command.court_id, command.date, command.start_time
        ):
            raise SlotNotAvailableException("Слот уже занят")
        
        # 4. Проверка конфликтов с существующими бронями пользователя
        user_bookings = self._booking_repo.find_by_user_id(command.user_id)
        from domain.models.value_objects.slot import Slot
        
        proposed_slot = Slot(
            court_id=command.court_id,
            date=command.date,
            start_time=command.start_time,
            end_time=command.end_time
        )
        
        if self._conflict_checker.has_double_booking(
            command.user_id, proposed_slot, user_bookings
        ):
            raise DomainException("У вас уже есть бронирование на это время")
        
        # 5. Блокировка слота (10 минут на оплату)
        lock_success = self._schedule_repo.lock_slot(
            court_id=command.court_id,
            date=command.date,
            start_time=command.start_time,
            booking_id="PENDING",  # Временный ID
            ttl_minutes=10
        )
        
        if not lock_success:
            raise SlotNotAvailableException("Слот только что заняли, попробуйте другой")
        
        try:
            # 6. Создание бронирования через Factory
            booking = self._factory.create_online_booking(
                user_id=command.user_id,
                court_id=command.court_id,
                slot_date=command.date,
                start_time=command.start_time,
                court_type=court.court_type,
                notes=command.notes
            )
            
            # 7. Сохранение
            self._booking_repo.save(booking)
            
            # Обновляем блокировку с реальным ID
            self._schedule_repo.unlock_slot(
                command.court_id, command.date, command.start_time
            )
            self._schedule_repo.lock_slot(
                court_id=command.court_id,
                date=command.date,
                start_time=command.start_time,
                booking_id=booking.id,
                ttl_minutes=10
            )
            
            return booking.id
            
        except Exception as e:
            # Откат блокировки при ошибке
            self._schedule_repo.unlock_slot(
                command.court_id, command.date, command.start_time
            )
            raise e
    
    def cancel_booking(self, command: CancelBookingCommand) -> None:
        """
        Отменить бронирование с учётом политики возврата.
        
        Algorithm:
        1. Найти бронирование
        2. Проверить права (пользователь или админ)
        3. Проверить политику отмены
        4. Выполнить возврат если была оплата
        5. Отменить бронирование
        6. Освободить слот
        7. Отправить уведомление
        """
        # 1. Поиск бронирования
        booking = self._booking_repo.find_by_id(command.booking_id)
        if booking is None:
            raise DomainException("Бронирование не найдено")
        
        # 2. Проверка прав (простая версия)
        if booking.user_id != command.user_id and not command.force:
            raise DomainException("Нет прав для отмены")
        
        # 3. Проверка политики отмены
        if not command.force:  # Админ может отменить в любое время
            policy_result = self._cancellation_policy.can_cancel(booking)
            if not policy_result.can_cancel:
                raise DomainException(
                    f"Нельзя отменить: {policy_result.reason}. "
                    f"Обратитесь к администратору."
                )
            
            # Возврат средств если была оплата
            if booking.payment_id and policy_result.refund_amount > 0:
                self._payment_gateway.refund(booking.payment_id)
        
        # 4. Отмена бронирования
        booking.cancel(
            reason=command.reason,
            cancelled_by=command.user_id if not command.force else "admin"
        )
        
        # 5. Освобождение слота
        self._schedule_repo.unlock_slot(
            booking.court_id,
            booking.slot.date,
            booking.slot.start_time
        )
        
        # 6. Сохранение
        self._booking_repo.save(booking)
        
        # 7. Уведомление (асинхронно)
        # TODO: получить email пользователя из UserRepository
        # self._notification_service.send_cancellation_notice(...)
    
    def confirm_payment(self, booking_id: str, payment_id: str) -> None:
        """
        Подтвердить оплату бронирования.
        
        Algorithm:
        1. Найти бронирование
        2. Проверить статус (должно быть PENDING_PAYMENT)
        3. Проверить статус платежа в шлюзе
        4. Подтвердить бронирование
        5. Подтвердить слот в расписании
        6. Отправить подтверждение
        """
        # 1. Поиск
        booking = self._booking_repo.find_by_id(booking_id)
        if booking is None:
            raise DomainException("Бронирование не найдено")
        
        # 2. Проверка статуса
        if not booking.is_pending_payment():
            raise DomainException(f"Нельзя оплатить бронирование в статусе {booking.status.value}")
        
        # 3. Проверка платежа
        payment_status = self._payment_gateway.get_status(payment_id)
        if payment_status.value != "success":
            raise DomainException("Платёж не подтверждён")
        
        # 4. Подтверждение бронирования
        booking.confirm(payment_id=payment_id)
        
        # 5. Подтверждение слота (убираем блокировку, ставим подтверждённое)
        self._schedule_repo.confirm_slot(
            booking.court_id,
            booking.slot.date,
            booking.slot.start_time
        )
        
        # 6. Сохранение
        self._booking_repo.save(booking)
        
        # 7. Уведомление
        # self._notification_service.send_booking_confirmation(...)
    
    # Queries
    
    def get_booking(self, booking_id: str) -> Optional[BookingDTO]:
        """Получить детали бронирования."""
        booking = self._booking_repo.find_by_id(booking_id)
        if booking is None:
            return None
        
        court = self._court_repo.find_by_id(booking.court_id)
        
        return BookingDTO(
            id=booking.id,
            user_id=booking.user_id,
            court_id=booking.court_id,
            court_name=court.name if court else "Unknown",
            court_type=court.court_type.code if court else "unknown",
            date=booking.slot.date,
            start_time=booking.slot.start_time,
            end_time=booking.slot.end_time,
            status=booking.status.value,
            total_amount=booking.total_amount.amount if booking.total_amount else 0,
            currency=booking.total_amount.currency if booking.total_amount else "BYN",
            payment_id=booking.payment_id,
            created_by_admin=booking.created_by_admin,
            notes=booking.notes,
            created_at=booking.created_at.isoformat(),
            confirmed_at=booking.confirmed_at.isoformat() if booking.confirmed_at else None,
            cancelled_at=booking.cancelled_at.isoformat() if booking.cancelled_at else None
        )
    
    def list_user_bookings(self, user_id: str) -> List[BookingListItemDTO]:
        """Получить список бронирований пользователя."""
        bookings = self._booking_repo.find_by_user_id(user_id)
        result = []
        
        for booking in bookings:
            court = self._court_repo.find_by_id(booking.court_id)
            
            result.append(BookingListItemDTO(
                id=booking.id,
                court_name=court.name if court else "Unknown",
                court_type=court.court_type.display_name if court else "Unknown",
                date=booking.slot.date,
                start_time=booking.slot.start_time,
                status=booking.status.value,
                total_amount=booking.total_amount.amount if booking.total_amount else 0
            ))
        
        return result