# Архитектурная диаграмма

## Диаграмма слоёв
```
┌───────────────────────────────────────────────────────────────────────────────┐
│                             ВНЕШНИЙ МИР                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐  ┌─────────────────────┐ │
│  │   Web UI    │  │  Admin Panel│  │Payment Gateway│  │Notification Service │ │
│  │  (React)    │  │   (React)   │  │  (YooKassa)   │  │  (Email/SMS)        │ │
│  └──────┬──────┘  └──────┬──────┘  └───────┬───────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼─────────────────┼─────────────────────┼────────────┘
          │                │                 │                     │
          ▼                ▼                 ▼                     ▼
┌───────────────────────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE LAYER (Адаптеры)                          │
│                                                                               │
│  ┌─────────────────────────────────┐    ┌─────────────────────────────────┐   │
│  │      ВХОДЯЩИЕ АДАПТЕРЫ          │    │      ИСХОДЯЩИЕ АДАПТЕРЫ         │   │
│  │  ┌─────────────────────────┐    │    │  ┌─────────────────────────┐    │   │
│  │  │  BookingController      │◄───┼────┼──┤  BookingRepository      │    │   │
│  │  │  (REST API)             │    │    │  │  (PostgreSQL)           │    │   │
│  │  └─────────────────────────┘    │    │  └─────────────────────────┘    │   │
│  │  ┌─────────────────────────┐    │    │  ┌─────────────────────────┐    │   │
│  │  │  AdminController        │◄───┼────┼──┤  CourtRepository        │    │   │
│  │  │  (REST API)             │    │    │  │  (PostgreSQL)           │    │   │
│  │  └─────────────────────────┘    │    │  └─────────────────────────┘    │   │
│  │  ┌─────────────────────────┐    │    │  ┌─────────────────────────┐    │   │
│  │  │ PaymentWebhookController│◄───┼────┼──┤  ScheduleRepository     │    │   │
│  │  │  (REST API)             │    │    │  │  (Redis/PostgreSQL)     │    │   │
│  │  └─────────────────────────┘    │    │  └─────────────────────────┘    │   │
│  │                                 │    │  ┌─────────────────────────┐    │   │
│  │                                 │    │  │  PaymentGatewayClient   │───►│   │
│  │                                 │    │  │  (HTTP Client)          │    │   │
│  │                                 │    │  └─────────────────────────┘    │   │
│  │                                 │    │  ┌─────────────────────────┐    │   │
│  │                                 │    │  │  NotificationClient     │───►│   │
│  │                                 │    │  │  (HTTP Client)          │    │   │
│  │                                 │    │  └─────────────────────────┘    │   │
│  └─────────────────────────────────┘    └─────────────────────────────────┘   │
│                               ▲                                   ▲           │
│                               │                                   │           │
│                               └───────────────────┬───────────────┘           │
│                                                   │                           │
└───────────────────────────────────────────────────┼───────────────────────────┘
                                                    │
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 APPLICATION LAYER (Порты)                              │
│                                                                                        │
│  ┌───────────────────────────────────────┐    ┌──────────────────────────────────────┐ │
│  │   ВХОДЯЩИЕ ПОРТЫ (Интерфейсы)         │    │   ИСХОДЯЩИЕ ПОРТЫ (Интерфейсы)       │ │
│  │                                       │    │                                      │ │
│  │  interface IBookingService {          │    │  interface IBookingRepository {      │ │
│  │    createBooking(cmd): BookingId      │    │    save(booking): void               │ │
│  │    cancelBooking(id): void            │    │    findById(id): Booking             │ │
│  │    getBooking(id): BookingDTO         │    │    findByUser(userId): List          │ │
│  │    listAvailableSlots(): List         │    │    findActiveByCourt(court,          │ │
│  │  }                                    │    │                         date)        │ │
│  │                                       │    │  }                                   │ │
│  │  interface IAdminService {            │    │                                      │ │
│  │    createPhoneBooking(cmd): BookingId │ interface ICourtRepository {              │ │
│  │    confirmPayment(id): void           │    │    findById(id): Court               │ │
│  │  }                                    │    │    findByType(type): List            │ │
│  │                                       │    │    findAll(): List                   │ │
│  │  interface IPaymentService {          │    │  }                                   │ │
│  │    processPayment(cmd): Result        │    │                                      │ │
│  │    verifyPayment(id): Status          │    │  interface IScheduleRepository{      │ │
│  │  }                                    │    │    isAvailable(court, slot): bool    │ │
│  │                                       │    │    lockSlot(court, slot): bool       │ │
│  │                                       │    │    unlockSlot(court, slot): void     │ │
│  │                                       │    │    confirmSlot(court, slot): void    │ │
│  │                                       │    │  }                                   │ │
│  │                                       │    │                                      │ │
│  │                                       │    │  interface IPaymentGateway {         │ │
│  │                                       │    │    charge(amount, currency): Result  │ │
│  │                                       │    │    refund(paymentId): Result         │ │
│  │                                       │    │    getStatus(paymentId): Status      │ │
│  │                                       │    │  }                                   │ │
│  │                                       │    │                                      │ │
│  │                                       │    │  interface INotificationService{     │ │
│  │                                       │    │    sendBookingConfirmation(to,       │ │
│  │                                       │    │                              booking)│ │
│  │                                       │    │    sendReminder(to, booking): void   │ │
│  │                                       │    │  }                                   │ │
│  └───────────────────────────────────────┘    └──────────────────────────────────────┘ │
│                                 ▲                                ▲                     │
│                                 │                                │                     │
│                                 └─────────────────┬──────────────┘                     │
│                                                   │                                    │
└───────────────────────────────────────────────────┼────────────────────────────────────┘
                                                    │
                                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      DOMAIN LAYER (Ядро)                                     │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────────┐│
│  │                          Entities (Сущности)                             ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐ ││
│  │  │   Booking   │  │    Court    │  │     Slot     │  │    Payment      │ ││
│  │  │  (Aggregate)│  │   (Entity)  │  │(Value Object)│  │   (Entity)      │ ││
│  │  │             │  │             │  │              │  │                 │ ││
│  │  │ - id: UUID  │  │ - id: UUID  │  │ - start: Time│  │ - id: UUID      │ ││
│  │  │ - userId    │  │ - name      │  │ - end: Time  │  │ - bookingId     │ ││
│  │  │ - courtId   │  │ - type      │  │ - date: Date │  │ - amount        │ ││
│  │  │ - slot      │  │ - capacity  │  │              │  │ - status        │ ││
│  │  │ - status    │  │ - price     │  │              │  │ - method        │ ││
│  │  │ - payment   │  │ - isActive  │  │              │  │                 │ ││
│  │  │             │  │             │  │              │  │                 │ ││
│  │  │ confirm()   │  │ activate()  │  │  overlaps()? │  │ refund()        │ ││
│  │  │ cancel()    │  │ deactivate()│  │              │  │ confirm()       │ ││
│  │  │ isExpired() │  │             │  │              │  │                 │ ││
│  │  └─────────────┘  └─────────────┘  └──────────────┘  └─────────────────┘ ││
│  │                                                                          ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐ ││
│  │  │    User     │  │  CourtType  │  │ BookingStatus│  │  PaymentStatus  │ ││
│  │  │  (Entity)   │  │ (Enum/VO)   │  │   (Enum)     │  │    (Enum)       │ ││
│  │  │             │  │             │  │              │  │                 │ ││
│  │  │ - id        │  │ VOLLEYBALL  │  │ PENDING      │  │ PENDING         │ ││
│  │  │ - email     │  │ BASKETBALL  │  │ RESERVED     │  │ PROCESSING      │ ││
│  │  │ - phone     │  │ BADMINTON   │  │ CONFIRMED    │  │ SUCCESS         │ ││
│  │  │ - role      │  │ TABLE_TENNIS│  │ CANCELLED    │  │ FAILED          │ ││
│  │  │             │  │             │  │ EXPIRED      │  │ REFUNDED        │ ││
│  │  └─────────────┘  └─────────────┘  └──────────────┘  └─────────────────┘ ││
│  │                                                                          ││
│  └──────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────────┐│
│  │                      Domain Events (События)                             ││
│  │                                                                          ││
│  │  BookingCreatedEvent    → После создания бронирования                    ││
│  │  BookingConfirmedEvent  → После подтверждения оплаты                     ││
│  │  BookingCancelledEvent  → После отмены                                   ││
│  │  PaymentReceivedEvent   → После получения платежа                        ││
│  │  SlotLockedEvent        → После блокировки слота                         ││
│  │                                                                          ││
│  └──────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

```


---

## Описание портов и адаптеров

| Тип | Название | Назначение |
| --- | --- | --- |
| **Входящий порт** | IBookingService | *Интерфейс для управления бронированиями клиентов (создание, отмена, просмотр)* |
| **Входящий порт** | IAdminService | *Интерфейс для административных операций (бронирование по телефону, подтверждение оплаты)* |
| **Входящий порт** | IPaymentService | *Интерфейс для обработки платежей (списание, возврат, проверка статуса)* |
| **Исходящий порт** | IBookingRepository | *Интерфейс для хранения и извлечения бронирований из БД* |
| **Исходящий порт** | ICourtRepository | *Интерфейс для доступа к данным спортивных площадок* |
| **Исходящий порт** | IScheduleRepository | *Интерфейс для управления расписанием, блокировки и проверки доступности слотов* |
| **Исходящий порт** | IPaymentGateway | *Интерфейс для интеграции с внешними платёжными системами (YooKassa, Stripe)* |
| **Исходящий порт** | INotificationService | *Интерфейс для отправки уведомлений пользователям (email, SMS, push)* |
| **Входящий адаптер** | BookingController (REST) | *REST API эндпоинты для операций бронирования (/api/bookings)* |
| **Входящий адаптер** | AdminController (REST) | *REST API для административной панели (/api/admin/bookings)* |
| **Входящий адаптер** | PaymentWebhookController (REST) | *Обработка вебхуков от платёжных систем (/api/webhooks/payment)* |
| **Исходящий адаптер** | InMemoryBookingRepository | *Реализация хранилища бронирований в памяти (для тестов и разработки)* |
| **Исходящий адаптер** | InMemoryCourtRepository | *Реализация хранилища площадок в памяти* |
| **Исходящий адаптер** | InMemoryScheduleRepository | *Реализация расписания и блокировок в памяти (имитация Redis)* |
| **Исходящий адаптер** | MockPaymentGateway | *Mock-реализация платёжного шлюза для тестирования* |
| **Исходящий адаптер** | MockNotificationService | *Mock-реализация сервиса уведомлений (логирование вместо отправки)* |

---
