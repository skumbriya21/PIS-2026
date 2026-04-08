import aio_pika
import json

from application.ports.outt.event_publisher import IEventPublisher


class RabbitMQEventPublisher(IEventPublisher):
    """RabbitMQ публикатор событий."""
    
    def __init__(self, connection: aio_pika.RobustConnection):
        self._connection = connection
        self._channel = None
    
    async def connect(self):
        """Установить соединение."""
        self._channel = await self._connection.channel()
        await self._channel.declare_exchange(
            "booking.events", aio_pika.ExchangeType.TOPIC, durable=True
        )
    
    async def publish(self, event) -> None:
        """Опубликовать событие."""
        exchange = await self._channel.get_exchange("booking.events")
        
        message = aio_pika.Message(
            body=json.dumps({
                "event_type": event.event_name,
                "payload": event.__dict__
            }).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        
        await exchange.publish(message, routing_key=event.event_name)