from application.ports.outt.email_sender import IEmailSender
from application.ports.outt.sms_sender import ISmsSender


class NotificationEventHandlers:
    """Обработчики событий для отправки уведомлений."""
    
    def __init__(
        self,
        email_sender: IEmailSender,
        sms_sender: ISmsSender
    ):
        self._email = email_sender
        self._sms = sms_sender
    
    async def on_booking_created(self, event_data: dict) -> None:
        """Уведомление о создании бронирования."""
        user_id = event_data["user_id"]
        
        # Получаем контакты пользователя (из User Context)
        # user = await user_client.get_user(user_id)
        
        message = (
            f"Забронирована площадка {event_data['court_id']} "
            f"на {event_data['slot_date']} в {event_data['slot_time']}. "
            f"Сумма: {event_data['amount']} {event_data['currency']}"
        )
        
        # Отправляем email
        # await self._email.send(to=user.email, subject="Бронирование подтверждено", body=message)
        
        # Отправляем SMS
        # await self._sms.send(to=user.phone, text=message)
        
        print(f"[Notification] Booking created: {message}")
    
    async def on_booking_confirmed(self, event_data: dict) -> None:
        """Уведомление о подтверждении."""
        message = (
            f"Бронирование {event_data['booking_id']} подтверждено! "
            f"Ждём вас на площадке."
        )
        print(f"[Notification] Booking confirmed: {message}")
    
    async def on_payment_initiated(self, event_data: dict) -> None:
        """Уведомление со ссылкой на оплату."""
        message = (
            f"Для завершения бронирования оплатите: "
            f"{event_data['payment_url']}"
        )
        print(f"[Notification] Payment link: {message}")