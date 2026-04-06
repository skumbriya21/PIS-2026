import pytest
from datetime import date, time


@pytest.fixture
def sample_slot():
    """Фикстура валидного слота."""
    from domain.models.value_objects.slot import Slot
    return Slot(
        court_id="court-001",
        date=date(2025, 3, 15),
        start_time=time(18, 0),
        end_time=time(19, 0)
    )


@pytest.fixture
def sample_money():
    """Фикстура денежной суммы."""
    from domain.models.value_objects.money import Money
    return Money(amount=35.0, currency="BYN")