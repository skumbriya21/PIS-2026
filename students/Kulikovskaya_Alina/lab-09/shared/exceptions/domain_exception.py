class DomainException(Exception):
    """Базовое исключение домена."""
    pass


class NotFoundException(DomainException):
    """Ресурс не найден."""
    pass


class ConflictException(DomainException):
    """Конфликт состояния."""
    pass