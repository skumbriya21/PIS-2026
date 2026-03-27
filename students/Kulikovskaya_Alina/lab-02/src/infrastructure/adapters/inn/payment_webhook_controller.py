class PaymentWebhookController:
    """Webhook controller для callback от платёжной системы."""
    
    def __init__(self, payment_service):
        self._service = payment_service
    
    def handle_payment_success(self, payment_id: str, 
                               external_id: str) -> dict:
        """POST /webhooks/payment/success"""
        raise NotImplementedError("Реализовать в Lab #4-5")
    
    def handle_payment_failure(self, payment_id: str,
                               error_code: str) -> dict:
        """POST /webhooks/payment/failure"""
        raise NotImplementedError("Реализовать в Lab #4-5")