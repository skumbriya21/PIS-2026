from abc import ABC, abstractmethod


class IEventPublisher(ABC):
    """Интерфейс публикации событий."""
    
    @abstractmethod
    async def publish(self, event) -> None:
        """Опубликовать событие."""
        pass