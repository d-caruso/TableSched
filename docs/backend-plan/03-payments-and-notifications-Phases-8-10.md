# Phases 8–10 — Payments & Notifications & Walk-ins

Covers the Stripe payment lifecycle (Payment Element + payment links + webhooks), synchronous localized notifications (Twilio SMS + Django SMTP), and walk-in management.

---

## Phase 8 — Payments (Stripe only)

Branch: `feature/payments-stripe`

### Task 8.1 — Payment model & statuses

Canonical Payment statuses (business doc §2):

```python
from django.db import models
from apps.common.models import TimeStampedModel

class PaymentStatus(models.TextChoices):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUND_PENDING = "refund_pending"
    REFUNDED = "refunded"
    REFUND_FAILED = "refund_failed"

class Payment(TimeStampedModel):
    KIND_PREAUTH, KIND_LINK = "preauth", "link"
    KIND_CHOICES = [(KIND_PREAUTH, "preauth"), (KIND_LINK, "link")]

    booking = models.OneToOneField("bookings.Booking", on_delete=models.PROTECT)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    stripe_payment_intent_id = models.CharField(max_length=128, blank=True, db_index=True)
    stripe_checkout_session_id = models.CharField(max_length=128, blank=True, db_index=True)
    amount_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=8, default="eur")
    status = models.CharField(max_length=32, choices=PaymentStatus.choices,
                              default=PaymentStatus.PENDING)
    expires_at = models.DateTimeField(null=True, blank=True)
```

### Task 8.2 — Gateway abstraction (designed for PayPal later, not implemented)

`apps/payments/gateways/base.py`:

```python
from typing import Protocol

class PaymentGateway(Protocol):
    def create_preauth(self, *, booking, amount_cents) -> "Payment": ...
    def capture(self, payment) -> "Payment": ...
    def cancel_authorization(self, payment) -> "Payment": ...
    def create_payment_link(self, *, booking, amount_cents, expires_at) -> "Payment": ...
    def refund(self, payment) -> "Payment": ...
```

Only `StripeGateway` is implemented in MVP. **Do not** create a PayPal stub.

### Task 8.3 — Stripe pre-authorization (Payment Element flow)

Booking is created first; then this is called:

```python
import stripe
from django.db import connection

def create_preauth(*, booking, settings):
    intent = stripe.PaymentIntent.create(
        amount=settings.deposit_amount_cents,
        currency="eur",
        capture_method="manual",
        automatic_payment_methods={"enabled": True},
        metadata={
            "tenant_schema": connection.schema_name,
            "booking_id": str(booking.id),
        },
    )
    Payment.objects.create(
        booking=booking,
        kind=Payment.KIND_PREAUTH,
        stripe_payment_intent_id=intent.id,
        amount_cents=settings.deposit_amount_cents,
        status=PaymentStatus.PENDING,   # becomes AUTHORIZED on webhook
    )
    return intent  # client_secret returned to frontend for the Payment Element
```

The frontend Payment Element confirms the intent client-side. Stripe then sends `payment_intent.amount_capturable_updated` (or `requires_capture` event) → webhook flips `Payment.status` to `AUTHORIZED`. Booking status stays `pending_review` per the agreed flow.

### Task 8.4 — Capture, cancel, payment link, refund

```python
def capture(payment):
    stripe.PaymentIntent.capture(payment.stripe_payment_intent_id)
    payment.status = PaymentStatus.CAPTURED
    payment.save()
    return payment

def cancel_authorization(payment):
    stripe.PaymentIntent.cancel(payment.stripe_payment_intent_id)
    payment.status = PaymentStatus.FAILED
    payment.save()
    return payment

def create_payment_link(*, booking, settings):
    expires_at = now() + timedelta(hours=settings.long_term_payment_window_hours)
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "eur",
                "unit_amount": settings.deposit_amount_cents,
                "product_data": {"name": f"Deposit booking {booking.id}"},
            },
            "quantity": 1,
        }],
        success_url=settings_module.PUBLIC_BOOKING_RETURN_URL,
        cancel_url=settings_module.PUBLIC_BOOKING_CANCEL_URL,
        expires_at=int(expires_at.timestamp()),
        metadata={
            "tenant_schema": connection.schema_name,
            "booking_id": str(booking.id),
        },
    )
    return Payment.objects.update_or_create(
        booking=booking,
        defaults=dict(
            kind=Payment.KIND_LINK,
            stripe_checkout_session_id=session.id,
            amount_cents=settings.deposit_amount_cents,
            status=PaymentStatus.PENDING,
            expires_at=expires_at,
        ),
    )[0]

def refund(payment):
    payment.status = PaymentStatus.REFUND_PENDING
    payment.save()
    try:
        stripe.Refund.create(payment_intent=payment.stripe_payment_intent_id)
        payment.status = PaymentStatus.REFUNDED
    except stripe.error.StripeError:
        payment.status = PaymentStatus.REFUND_FAILED
    payment.save()
    return payment
```

Refunds are **always** triggered manually by staff (business doc §4). No automation. No partial refunds.

### Task 8.5 — Webhook handler (public URL)

`apps/payments/views.py`:

```python
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from django_tenants.utils import schema_context
import stripe

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(
            payload, sig, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    obj = event["data"]["object"]
    tenant_schema = (obj.get("metadata") or {}).get("tenant_schema")
    if not tenant_schema:
        return HttpResponse(status=400)

    with schema_context(tenant_schema):
        from apps.payments import handlers
        handlers.dispatch(event)
    return HttpResponse(status=200)
```

Handler dispatch table (`apps/payments/handlers.py`):

| Stripe event | Effect |
|---|---|
| `payment_intent.amount_capturable_updated` | `Payment.status = authorized` |
| `payment_intent.succeeded` | `Payment.status = captured` |
| `payment_intent.payment_failed` | `Payment.status = failed` |
| `payment_intent.canceled` | `Payment.status = failed` |
| `checkout.session.completed` (payment link) | `Payment.status = captured` → `transition(booking, CONFIRMED)` → notify customer |
| `checkout.session.expired` | `Payment.status = failed` (sweep handles booking expiration) |
| `charge.refunded` | reconciles `REFUND_PENDING` → `REFUNDED` |
| `charge.refund.failed` | `REFUND_PENDING` → `REFUND_FAILED` |

Webhook handlers must be **idempotent**: keyed by `event.id` stored in a small dedupe table to skip already-processed events.

### Task 8.6 — Manual refund endpoint

`POST /api/v1/payments/{id}/refund` — manager-only (`IsManager`). No partial refunds.

---

## Phase 9 — Notifications (Twilio SMS + Django SMTP, synchronous)

Branch: `feature/notifications`

### Task 9.1 — NotificationLog

```python
class NotificationLog(TimeStampedModel):
    CHANNEL_SMS, CHANNEL_EMAIL = "sms", "email"
    CHANNEL_CHOICES = [(CHANNEL_SMS, "sms"), (CHANNEL_EMAIL, "email")]

    booking = models.ForeignKey("bookings.Booking", null=True, blank=True,
                                on_delete=models.SET_NULL)
    template_code = models.CharField(max_length=64)
    locale = models.CharField(max_length=8)
    channel = models.CharField(max_length=16, choices=CHANNEL_CHOICES)
    recipient = models.CharField(max_length=128)
    status = models.CharField(max_length=16)             # queued, sent, failed
    provider_message_id = models.CharField(max_length=128, blank=True)
    error_code = models.CharField(max_length=64, blank=True)
```

### Task 9.2 — Localized templates

`apps/notifications/templates/`:

```
templates/
  en.py
  it.py
  de.py
```

Each module exports a `TEMPLATES` dict keyed by template code:

```python
# en.py
TEMPLATES = {
    "booking_request_received": {
        "sms": "Your booking at {restaurant} on {when} for {party} was received. Manage it: {url}",
        "email_subject": "Booking request received",
        "email_body": "Your booking at {restaurant} on {when} for {party} was received. Manage it: {url}",
    },
    "booking_approved":            {...},
    "booking_declined":            {...},
    "payment_required":            {...},
    "new_booking_request":         {...},   # staff-targeted (in-app only in MVP)
    "authorization_expired_staff": {...},
}
```

`apps/notifications/i18n.py`:

```python
import importlib

SUPPORTED = {"en", "it", "de"}
DEFAULT = "en"

def render(code: str, locale: str, channel: str, ctx: dict):
    locale = locale if locale in SUPPORTED else DEFAULT
    tpl = importlib.import_module(
        f"apps.notifications.templates.{locale}"
    ).TEMPLATES[code]
    if channel == "sms":
        return tpl["sms"].format(**ctx)
    return tpl["email_subject"].format(**ctx), tpl["email_body"].format(**ctx)
```

### Task 9.3 — Routing rules (business doc §9)

- Phone is mandatory → SMS is **always** sent.
- Email is optional → email is sent **only if** `customer.email` is set.
- Staff notifications are **in-app only** in MVP (technical doc §7 "in-app basics").

```python
def notify_customer(booking, code: str, *, raw_token: str | None = None):
    customer = booking.customer
    ctx = _build_ctx(booking, raw_token)
    _send_sms(booking, code, customer.locale, customer.phone, ctx)
    if customer.email:
        _send_email(booking, code, customer.locale, customer.email, ctx)

def notify_staff(booking, code: str):
    InAppNotification.objects.create(...)  # no SMS/email to staff in MVP
```

### Task 9.4 — Synchronous send + non-blocking failure

Hard rule (technical doc §8): SMS / email failure must **never** block the booking flow.

```python
from django.core.mail import send_mail
from twilio.base.exceptions import TwilioRestException

def _send_sms(booking, code, locale, phone, ctx):
    text = render(code, locale, "sms", ctx)
    log = NotificationLog.objects.create(
        booking=booking, template_code=code, locale=locale,
        channel="sms", recipient=phone, status="queued",
    )
    try:
        msg = twilio_client.messages.create(
            to=phone, from_=settings.TWILIO_FROM, body=text,
        )
        log.status = "sent"; log.provider_message_id = msg.sid
    except TwilioRestException as e:
        log.status = "failed"; log.error_code = str(e.code)
        logger.exception("sms_failed", extra={"booking_id": str(booking.id)})
    log.save()

def _send_email(booking, code, locale, email, ctx):
    subject, body = render(code, locale, "email", ctx)
    log = NotificationLog.objects.create(
        booking=booking, template_code=code, locale=locale,
        channel="email", recipient=email, status="queued",
    )
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL,
                  [email], fail_silently=False)
        log.status = "sent"
    except Exception as e:
        log.status = "failed"; log.error_code = e.__class__.__name__
        logger.exception("email_failed", extra={"booking_id": str(booking.id)})
    log.save()
```

Neither helper raises out.

---

## Phase 10 — Walk-ins

Branch: `feature/walkins`

```python
class Walkin(TimeStampedModel):
    starts_at = models.DateTimeField()
    party_size = models.PositiveSmallIntegerField()
    table = models.ForeignKey("restaurants.Table", null=True, blank=True,
                              on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
```

No phone, no Customer FK, no status workflow (business doc §10). Endpoint: `POST /api/v1/walkins` (staff-only).
