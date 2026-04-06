class DomainException(Exception):
    """Базовое исключение для ошибок домена."""
    pass


class SlotNotAvailableException(DomainException):
    """Слот уже занят."""
    pass


class PaymentRequiredException(DomainException):
    """Требуется оплата для операции."""
    pass


class BookingNotFoundException(DomainException):
    """Бронирование не найдено."""
    pass


class InvalidBookingStatusException(DomainException):
    """Недопустимый статус бронирования."""
    pass