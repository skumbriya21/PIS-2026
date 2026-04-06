from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class SlotDTO:
    """DTO для временного слота."""
    start_time: time
    end_time: time
    is_available: bool
    price: float