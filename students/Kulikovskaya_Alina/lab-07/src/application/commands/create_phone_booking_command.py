from dataclasses import dataclass
from datetime import date, time


@dataclass(frozen=True)
class CreatePhoneBookingCommand:
    """Команда создания бронирования администратором по телефону."""
    admin_id: str
    court_id: str
    date: date
    start_time: time
    customer_name: str
    customer_phone: str
    notes: str = ""