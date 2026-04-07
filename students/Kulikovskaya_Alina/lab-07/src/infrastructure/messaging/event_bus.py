from typing import List, Callable, Dict
from abc import ABC, abstractmethod

from domain.events.domain_event import DomainEvent


class EventBus(ABC):
    """Абстракция шины событий."""
    
    @abstractmethod
    def publish(self, event: DomainEvent) -> None:
        pass
    
    @abstractmethod
    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        pass


class InMemoryEventBus(EventBus):
    """In-memory реализация для разработки и тестов."""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
    
    def publish(self, event: DomainEvent) -> None:
        handlers = self._handlers.get(event.event_name(), [])
        for handler in handlers:
            handler(event)
    
    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)