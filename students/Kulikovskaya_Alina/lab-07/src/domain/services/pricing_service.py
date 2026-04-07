from datetime import date, time
from typing import Optional

from domain.models.value_objects.court_type import CourtType
from domain.models.value_objects.money import Money
from domain.specifications.booking_rules import PeakHoursRule


class PricingService:
    """
    Доменный сервис: расчёт стоимости бронирования.
    
    Учитывает:
    - Базовую стоимость типа площадки
    - Пиковые часы (наценка 20%)
    - Длительность (пока только 1 час)
    """
    
    PEAK_SURCHARGE_PERCENT = 20  # Наценка в пиковые часы
    
    def calculate_price(self, court_type: CourtType, slot_date: date,
                        slot_time: time, hours: int = 1) -> Money:
        """
        Рассчитать стоимость бронирования.
        
        Args:
            court_type: Тип площадки
            slot_date: Дата слота
            slot_time: Время начала
            hours: Количество часов (по умолчанию 1)
        
        Returns:
            Итоговая стоимость
        """
        base_rate = court_type.hourly_rate
        base_amount = base_rate * hours
        
        # Проверка на пиковые часы
        peak_rule = PeakHoursRule()
        if peak_rule.is_peak(court_type, slot_date, slot_time):
            surcharge = base_amount * (self.PEAK_SURCHARGE_PERCENT / 100)
            total = base_amount + surcharge
        else:
            total = base_amount
        
        return Money(amount=round(total, 2), currency="BYN")
    
    def calculate_cancellation_fee(self, original_amount: Money,
                                   refund_percent: float) -> Money:
        """
        Рассчитать комиссию за отмену.
        
        Returns:
            Сумма комиссии (не возвращается клиенту)
        """
        fee_percent = 100 - refund_percent
        fee_amount = original_amount.amount * (fee_percent / 100)
        return Money(amount=round(fee_amount, 2), currency=original_amount.currency)