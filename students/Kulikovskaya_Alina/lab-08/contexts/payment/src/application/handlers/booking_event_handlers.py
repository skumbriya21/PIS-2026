from domain.models.payment import Payment
from application.ports.outt.payment_repository import IPaymentRepository
from application.ports.outt.payment_gateway import IPaymentGateway
from application.ports.outt.event_publisher import IEventPublisher


class BookingEventHandlers:
    """Обработчики событий бронирования."""
    
    def __init__(
        self,
        payment_repo: IPaymentRepository,
        payment_gateway: IPaymentGateway,
        event_publisher: IEventPublisher
    ):
        self._repo = payment_repo
        self._gateway = payment_gateway
        self._events = event_publisher
    
    async def on_booking_created(self, event_data: dict) -> None:
        """Обработка BookingCreatedEvent."""
        # Создаём платёж
        payment = Payment(
            booking_id=event_data["booking_id"],
            user_id=event_data["user_id"],
            amount=event_data["amount"],
            currency=event_data["currency"],
            payment_method="card"  # По умолчанию
        )
        
        await self._repo.save(payment)
        
        # Инициируем платёж в шлюзе
        payment_url = await self._gateway.create_payment(
            amount=payment.amount,
            currency=payment.currency,
            description=f"Бронирование {event_data['court_id']} на {event_data['slot_date']}",
            return_url=f"https://igraem.by/payment/callback/{payment.id}"
        )
        
        # Отправляем событие с ссылкой на оплату
        await self._events.publish({
            "event_type": "payment.initiated",
            "payment_id": payment.id,
            "booking_id": payment.booking_id,
            "payment_url": payment_url
        })
    
    async def on_booking_cancelled(self, event_data: dict) -> None:
        """Обработка BookingCancelledEvent — возврат средств."""
        payment = await self._repo.find_by_booking_id(event_data["booking_id"])
        
        if payment and payment.status == "success":
            # Возврат через шлюз
            await self._gateway.refund(
                payment.external_payment_id,
                payment.amount
            )
            
            payment.refund()
            await self._repo.save(payment)