from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="Играем? API Gateway")

# Конфигурация сервисов
BOOKING_SERVICE = "http://booking-service:8000"
COURT_SERVICE = "http://court-service:8000"
PAYMENT_SERVICE = "http://payment-service:8000"


@app.post("/api/bookings")
async def create_booking(data: dict):
    """Создать бронирование (прокси на Booking Service)."""
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{BOOKING_SERVICE}/bookings", json=data)
        
        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        
        return response.json()


@app.get("/api/courts")
async def list_courts():
    """Список площадок (прокси на Court Service)."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{COURT_SERVICE}/courts")
        return response.json()


@app.get("/api/courts/{court_id}/availability")
async def check_availability(court_id: str, date: str):
    """Проверка доступности."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{COURT_SERVICE}/courts/{court_id}/availability",
            params={"date": date}
        )
        return response.json()


@app.get("/api/users/{user_id}/bookings")
async def get_user_bookings(user_id: str):
    """Бронирования пользователя."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BOOKING_SERVICE}/users/{user_id}/bookings"
        )
        return response.json()


@app.post("/api/payments/webhook")
async def payment_webhook(data: dict):
    """Webhook от платёжной системы."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PAYMENT_SERVICE}/webhook",
            json=data
        )
        return response.json()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)