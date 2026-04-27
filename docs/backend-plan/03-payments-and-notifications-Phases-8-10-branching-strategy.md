# Branching Strategy — Phases 8–10: Payments & Notifications & Walk-ins

References:
- Implementation plan: [`03-payments-and-notifications-Phases-8-10.md`](./03-payments-and-notifications-Phases-8-10.md)
- Branching rules: [`BRANCHING_STRATEGY.md`](../../BRANCHING_STRATEGY.md)

---

## Global Rules

- **No hardcoded user-facing strings.** All text shown to the user must use i18n translation keys. The API returns only `error_code`, `reason_code`, and `status` strings — never localized text (except staff-written `staff_message` fields). SMS/email templates are localized server-side from `Customer.locale`.
- **Tests are mandatory** for every task that introduces logic. Write unit tests and integration tests in the same task branch, before merging.
- **Each task branch lifecycle:** create from parent → implement → commit → pre-merge checks → push → PR → merge into parent.
- **Progress markers:** ❌ not done · ✅ done. Update in place as work completes.

## Pre-Merge Checks (Django backend — run in this order, one at a time)

```bash
# 1. Lint
ruff check backend/

# 2. Type check
mypy backend/

# 3. Tests — specific file(s) for changed code only
pytest tests/<specific_test_file>.py

# 4. Full test suite — only if step 3 passes
pytest
```

All checks must pass (0 errors, 0 failures) before creating a PR.

---

## Branch Hierarchy

```
develop
└── feature/backend-mvp
    ├── feature/backend-mvp-Phase8-payments           ← created from feature/backend-mvp AFTER Phase 7 merged
    │   ├── task/backend-mvp-Task8.1-payment-model
    │   ├── task/backend-mvp-Task8.2-gateway-abstraction
    │   ├── task/backend-mvp-Task8.3-stripe-preauth
    │   ├── task/backend-mvp-Task8.4-capture-refund
    │   ├── task/backend-mvp-Task8.5-webhook-handler
    │   └── task/backend-mvp-Task8.6-refund-endpoint
    ├── feature/backend-mvp-Phase9-notifications      ← created from feature/backend-mvp AFTER Phase 8 merged
    │   ├── task/backend-mvp-Task9.1-notification-log
    │   ├── task/backend-mvp-Task9.2-localized-templates
    │   ├── task/backend-mvp-Task9.3-routing-rules
    │   └── task/backend-mvp-Task9.4-synchronous-send
    └── feature/backend-mvp-Phase10-walkins           ← created from feature/backend-mvp AFTER Phase 9 merged
        └── task/backend-mvp-Task10.1-walkin-model
```

---

## ❌ Phase 8 — Payments (Stripe only)

Implements the full Stripe payment lifecycle: Payment model, gateway abstraction, Payment Element pre-authorization flow (near-term), Stripe Checkout session links (long-term), webhook handler, and manual refunds. PayPal is out of scope.

**⚠️ Create this branch only after Phase 7 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase8-payments` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase8-payments
git push -u origin feature/backend-mvp-Phase8-payments
```

---

### ❌ Task 8.1 — Payment Model & Statuses

Canonical payment statuses tracked separately from booking status. No user-facing strings.

**Branch:** `task/backend-mvp-Task8.1-payment-model` — created from `feature/backend-mvp-Phase8-payments`

```bash
git checkout feature/backend-mvp-Phase8-payments
git pull origin feature/backend-mvp-Phase8-payments
git checkout -b task/backend-mvp-Task8.1-payment-model
```

**`apps/payments/models.py`:**

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

**Tests:**

```python
# tests/payments/test_models.py

def test_all_payment_statuses_defined():
    from apps.payments.models import PaymentStatus
    expected = {"pending", "authorized", "captured", "failed",
                "refund_pending", "refunded", "refund_failed"}
    assert set(PaymentStatus.values) == expected

def test_payment_is_one_to_one_with_booking(tenant_db, booking):
    from apps.payments.models import Payment, PaymentStatus
    from django.db import IntegrityError
    import pytest
    Payment.objects.create(booking=booking, kind="preauth", amount_cents=1000,
                           status=PaymentStatus.PENDING)
    with pytest.raises(IntegrityError):
        Payment.objects.create(booking=booking, kind="link", amount_cents=1000,
                               status=PaymentStatus.PENDING)
```

**Commit:**
```bash
git add apps/payments/models.py
git commit -m "[TASK] 8.1 add Payment model and status set"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/payments/test_models.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task8.1-payment-model
# Open PR: "[TASK 8.1] Add Payment model and status set" → feature/backend-mvp-Phase8-payments
git checkout feature/backend-mvp-Phase8-payments
git merge task/backend-mvp-Task8.1-payment-model
git push origin feature/backend-mvp-Phase8-payments
```

---

### ❌ Task 8.2 — Gateway Abstraction

Protocol-based interface designed to support PayPal later. Only `StripeGateway` is implemented. No PayPal stub.

**Branch:** `task/backend-mvp-Task8.2-gateway-abstraction` — created from `feature/backend-mvp-Phase8-payments`

```bash
git checkout feature/backend-mvp-Phase8-payments
git pull origin feature/backend-mvp-Phase8-payments
git checkout -b task/backend-mvp-Task8.2-gateway-abstraction
```

**`apps/payments/gateways/base.py`:**

```python
from typing import Protocol
from apps.payments.models import Payment

class PaymentGateway(Protocol):
    def create_preauth(self, *, booking, amount_cents) -> Payment: ...
    def capture(self, payment: Payment) -> Payment: ...
    def cancel_authorization(self, payment: Payment) -> Payment: ...
    def create_payment_link(self, *, booking, amount_cents, expires_at) -> Payment: ...
    def refund(self, payment: Payment) -> Payment: ...
```

**Tests:**

```python
# tests/payments/test_gateway_protocol.py

def test_stripe_gateway_satisfies_protocol():
    from apps.payments.gateways.stripe import StripeGateway
    from apps.payments.gateways.base import PaymentGateway
    import typing
    # Runtime check: StripeGateway implements all methods of PaymentGateway
    for method in ("create_preauth", "capture", "cancel_authorization",
                   "create_payment_link", "refund"):
        assert hasattr(StripeGateway, method)
```

**Commit:**
```bash
git add apps/payments/gateways/
git commit -m "[TASK] 8.2 add PaymentGateway protocol and Stripe skeleton"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/payments/test_gateway_protocol.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task8.2-gateway-abstraction
# Open PR: "[TASK 8.2] Add PaymentGateway protocol" → feature/backend-mvp-Phase8-payments
git checkout feature/backend-mvp-Phase8-payments
git merge task/backend-mvp-Task8.2-gateway-abstraction
git push origin feature/backend-mvp-Phase8-payments
```

---

### ❌ Task 8.3 — Stripe Pre-Authorization (Payment Element Flow)

Booking is created first; PaymentIntent created afterwards with `capture_method=manual`. Returns `client_secret` to frontend for the Payment Element. `Payment.status` becomes `authorized` on Stripe webhook — booking remains `pending_review`.

**Branch:** `task/backend-mvp-Task8.3-stripe-preauth` — created from `feature/backend-mvp-Phase8-payments`

```bash
git checkout feature/backend-mvp-Phase8-payments
git pull origin feature/backend-mvp-Phase8-payments
git checkout -b task/backend-mvp-Task8.3-stripe-preauth
```

**`apps/payments/gateways/stripe.py`:**

```python
import stripe
from django.db import connection
from apps.payments.models import Payment, PaymentStatus

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
        status=PaymentStatus.PENDING,
    )
    return intent  # frontend uses intent.client_secret in the Payment Element
```

**Tests (mocked Stripe):**

```python
# tests/payments/test_preauth.py
import responses as resp

def test_create_preauth_creates_payment_record(tenant_db, booking, settings, mock_stripe_intent):
    from apps.payments.gateways.stripe import create_preauth
    from apps.payments.models import Payment, PaymentStatus

    intent = create_preauth(booking=booking, settings=settings)

    payment = Payment.objects.get(booking=booking)
    assert payment.kind == "preauth"
    assert payment.status == PaymentStatus.PENDING
    assert payment.stripe_payment_intent_id == mock_stripe_intent.id

def test_preauth_metadata_contains_tenant_schema(tenant_db, booking, settings, mock_stripe):
    from apps.payments.gateways.stripe import create_preauth
    create_preauth(booking=booking, settings=settings)
    call_kwargs = mock_stripe.PaymentIntent.create.call_args.kwargs
    assert "tenant_schema" in call_kwargs["metadata"]
    assert "booking_id" in call_kwargs["metadata"]

def test_booking_stays_pending_review_after_preauth(tenant_db, booking, settings, mock_stripe_intent):
    from apps.payments.gateways.stripe import create_preauth
    from apps.bookings.models import BookingStatus
    create_preauth(booking=booking, settings=settings)
    booking.refresh_from_db()
    assert booking.status == BookingStatus.PENDING_REVIEW
```

**Commit:**
```bash
git add apps/payments/gateways/stripe.py
git commit -m "[TASK] 8.3 add Stripe pre-authorization via Payment Element"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/payments/test_preauth.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task8.3-stripe-preauth
# Open PR: "[TASK 8.3] Add Stripe pre-authorization" → feature/backend-mvp-Phase8-payments
git checkout feature/backend-mvp-Phase8-payments
git merge task/backend-mvp-Task8.3-stripe-preauth
git push origin feature/backend-mvp-Phase8-payments
```

---

### ❌ Task 8.4 — Capture, Cancel Authorization, Payment Link, Refund

Manual refunds only — no automation, no partial refunds.

**Branch:** `task/backend-mvp-Task8.4-capture-refund` — created from `feature/backend-mvp-Phase8-payments`

```bash
git checkout feature/backend-mvp-Phase8-payments
git pull origin feature/backend-mvp-Phase8-payments
git checkout -b task/backend-mvp-Task8.4-capture-refund
```

**`apps/payments/gateways/stripe.py` (continued):**

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
    from django.conf import settings as django_settings
    from django.utils.timezone import now
    from datetime import timedelta
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
        success_url=django_settings.PUBLIC_BOOKING_RETURN_URL,
        cancel_url=django_settings.PUBLIC_BOOKING_CANCEL_URL,
        expires_at=int(expires_at.timestamp()),
        metadata={"tenant_schema": connection.schema_name, "booking_id": str(booking.id)},
    )
    return Payment.objects.update_or_create(
        booking=booking,
        defaults=dict(kind=Payment.KIND_LINK,
                      stripe_checkout_session_id=session.id,
                      amount_cents=settings.deposit_amount_cents,
                      status=PaymentStatus.PENDING,
                      expires_at=expires_at),
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

**Tests:**

```python
# tests/payments/test_capture_refund.py

def test_capture_sets_status_captured(tenant_db, authorized_payment, mock_stripe):
    from apps.payments.gateways.stripe import capture
    capture(authorized_payment)
    authorized_payment.refresh_from_db()
    assert authorized_payment.status == "captured"

def test_refund_sets_status_refunded(tenant_db, captured_payment, mock_stripe_refund):
    from apps.payments.gateways.stripe import refund
    refund(captured_payment)
    captured_payment.refresh_from_db()
    assert captured_payment.status == "refunded"

def test_refund_on_stripe_error_sets_refund_failed(tenant_db, captured_payment, mock_stripe_error):
    from apps.payments.gateways.stripe import refund
    refund(captured_payment)
    captured_payment.refresh_from_db()
    assert captured_payment.status == "refund_failed"
```

**Commit:**
```bash
git add apps/payments/gateways/stripe.py
git commit -m "[TASK] 8.4 add capture, cancel, payment link, refund"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/payments/test_capture_refund.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task8.4-capture-refund
# Open PR: "[TASK 8.4] Add capture, cancel, payment link, refund" → feature/backend-mvp-Phase8-payments
git checkout feature/backend-mvp-Phase8-payments
git merge task/backend-mvp-Task8.4-capture-refund
git push origin feature/backend-mvp-Phase8-payments
```

---

### ❌ Task 8.5 — Stripe Webhook Handler (Public URL)

Receives Stripe events, verifies signature, resolves tenant from metadata, dispatches to idempotent handlers. Lives on the public URLConf.

**Branch:** `task/backend-mvp-Task8.5-webhook-handler` — created from `feature/backend-mvp-Phase8-payments`

```bash
git checkout feature/backend-mvp-Phase8-payments
git pull origin feature/backend-mvp-Phase8-payments
git checkout -b task/backend-mvp-Task8.5-webhook-handler
```

**`apps/payments/views.py`:**

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

**Event → handler mapping (`apps/payments/handlers.py`):**

| Stripe event | Effect |
|---|---|
| `payment_intent.amount_capturable_updated` | `Payment.status = authorized` |
| `payment_intent.succeeded` | `Payment.status = captured` |
| `payment_intent.payment_failed` | `Payment.status = failed` |
| `payment_intent.canceled` | `Payment.status = failed` |
| `checkout.session.completed` | `Payment.status = captured` → `Booking.status = confirmed` → notify customer |
| `checkout.session.expired` | `Payment.status = failed` |
| `charge.refunded` | `REFUND_PENDING` → `REFUNDED` |
| `charge.refund.failed` | `REFUND_PENDING` → `REFUND_FAILED` |

Handlers are idempotent: dedupe by `event.id` in a `StripeEvent` table.

**Tests:**

```python
# tests/payments/test_webhook.py

def test_unsigned_webhook_returns_400(client):
    response = client.post("/stripe/webhook/", data=b"{}", content_type="application/json")
    assert response.status_code == 400

def test_missing_tenant_schema_returns_400(client, valid_stripe_signature):
    payload = build_event_payload(metadata={})
    response = client.post("/stripe/webhook/", data=payload,
                           HTTP_STRIPE_SIGNATURE=valid_stripe_signature,
                           content_type="application/json")
    assert response.status_code == 400

def test_payment_intent_capturable_sets_authorized(client, tenant, payment,
                                                    stripe_capturable_event):
    response = client.post("/stripe/webhook/", data=stripe_capturable_event,
                           HTTP_STRIPE_SIGNATURE=compute_sig(stripe_capturable_event),
                           content_type="application/json")
    assert response.status_code == 200
    payment.refresh_from_db()
    assert payment.status == "authorized"

def test_webhook_is_idempotent(client, tenant, payment, stripe_capturable_event):
    sig = compute_sig(stripe_capturable_event)
    client.post("/stripe/webhook/", data=stripe_capturable_event,
                HTTP_STRIPE_SIGNATURE=sig, content_type="application/json")
    client.post("/stripe/webhook/", data=stripe_capturable_event,
                HTTP_STRIPE_SIGNATURE=sig, content_type="application/json")
    payment.refresh_from_db()
    assert payment.status == "authorized"  # processed once, not twice
```

**Commit:**
```bash
git add apps/payments/views.py apps/payments/handlers.py
git commit -m "[TASK] 8.5 add Stripe webhook handler with signature verification"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/payments/test_webhook.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task8.5-webhook-handler
# Open PR: "[TASK 8.5] Add Stripe webhook handler" → feature/backend-mvp-Phase8-payments
git checkout feature/backend-mvp-Phase8-payments
git merge task/backend-mvp-Task8.5-webhook-handler
git push origin feature/backend-mvp-Phase8-payments
```

---

### ❌ Task 8.6 — Manual Refund Endpoint

Manager-only. No partial refunds. No automation.

**Branch:** `task/backend-mvp-Task8.6-refund-endpoint` — created from `feature/backend-mvp-Phase8-payments`

```bash
git checkout feature/backend-mvp-Phase8-payments
git pull origin feature/backend-mvp-Phase8-payments
git checkout -b task/backend-mvp-Task8.6-refund-endpoint
```

`POST /api/v1/payments/{id}/refund` — permission: `IsManager`. Calls `gateway.refund(payment)`.

**Tests:**

```python
# tests/payments/test_refund_endpoint.py

def test_refund_requires_manager_role(staff_client, tenant, payment):
    response = staff_client.post(f"/api/v1/payments/{payment.id}/refund/",
                                 HTTP_HOST=tenant.domain)
    assert response.status_code == 403

def test_refund_succeeds_for_manager(manager_client, tenant, captured_payment, mock_stripe):
    response = manager_client.post(f"/api/v1/payments/{captured_payment.id}/refund/",
                                   HTTP_HOST=tenant.domain)
    assert response.status_code == 200
    captured_payment.refresh_from_db()
    assert captured_payment.status in ("refunded", "refund_pending")
```

**Commit:**
```bash
git add apps/payments/views.py apps/payments/urls.py
git commit -m "[TASK] 8.6 add manager-only manual refund endpoint"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/payments/test_refund_endpoint.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task8.6-refund-endpoint
# Open PR: "[TASK 8.6] Add manual refund endpoint" → feature/backend-mvp-Phase8-payments
git checkout feature/backend-mvp-Phase8-payments
git merge task/backend-mvp-Task8.6-refund-endpoint
git push origin feature/backend-mvp-Phase8-payments
```

---

### ❌ Phase 8 complete — merge into feature branch

```bash
# Open PR: "[PHASE 8] Payments (Stripe)" → feature/backend-mvp
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase8-payments
git push origin feature/backend-mvp
```

---

## ❌ Phase 9 — Notifications (Twilio SMS + Django SMTP, synchronous)

Implements synchronous, localized notifications. SMS is always sent (phone mandatory). Email is sent when `Customer.email` is set. Templates stored per code per locale (`en`, `it`, `de`). Failures are logged and never block the booking flow.

**⚠️ Create this branch only after Phase 8 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase9-notifications` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase9-notifications
git push -u origin feature/backend-mvp-Phase9-notifications
```

---

### ❌ Task 9.1 — NotificationLog

Audit trail for every sent/failed notification. No user-facing strings.

**Branch:** `task/backend-mvp-Task9.1-notification-log` — created from `feature/backend-mvp-Phase9-notifications`

```bash
git checkout feature/backend-mvp-Phase9-notifications
git pull origin feature/backend-mvp-Phase9-notifications
git checkout -b task/backend-mvp-Task9.1-notification-log
```

**`apps/notifications/models.py`:**

```python
from django.db import models
from apps.common.models import TimeStampedModel

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

**Tests:**

```python
# tests/notifications/test_models.py

def test_notification_log_channels():
    from apps.notifications.models import NotificationLog
    valid = {c[0] for c in NotificationLog.CHANNEL_CHOICES}
    assert valid == {"sms", "email"}
```

**Commit:**
```bash
git add apps/notifications/models.py
git commit -m "[TASK] 9.1 add NotificationLog model"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/notifications/test_models.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task9.1-notification-log
# Open PR: "[TASK 9.1] Add NotificationLog model" → feature/backend-mvp-Phase9-notifications
git checkout feature/backend-mvp-Phase9-notifications
git merge task/backend-mvp-Task9.1-notification-log
git push origin feature/backend-mvp-Phase9-notifications
```

---

### ❌ Task 9.2 — Localized Templates

Per-code, per-locale template modules. Fallback to `en`. No hardcoded user-facing strings elsewhere in the codebase — all SMS/email text lives here.

**Branch:** `task/backend-mvp-Task9.2-localized-templates` — created from `feature/backend-mvp-Phase9-notifications`

```bash
git checkout feature/backend-mvp-Phase9-notifications
git pull origin feature/backend-mvp-Phase9-notifications
git checkout -b task/backend-mvp-Task9.2-localized-templates
```

**`apps/notifications/templates/en.py`:**

```python
TEMPLATES = {
    "booking_request_received": {
        "sms": "Your booking at {restaurant} on {when} for {party} was received. Manage it: {url}",
        "email_subject": "Booking request received",
        "email_body": "Your booking at {restaurant} on {when} for {party} was received. Manage it: {url}",
    },
    "booking_approved": {
        "sms": "Your booking at {restaurant} on {when} is confirmed.",
        "email_subject": "Booking confirmed",
        "email_body": "Your booking at {restaurant} on {when} for {party} is confirmed.",
    },
    "booking_declined": {
        "sms": "Your booking at {restaurant} on {when} was declined.",
        "email_subject": "Booking declined",
        "email_body": "Your booking at {restaurant} on {when} was declined.",
    },
    "payment_required": {
        "sms": "Please complete payment for your booking: {url}",
        "email_subject": "Payment required",
        "email_body": "Please complete payment for your booking at {restaurant}: {url}",
    },
    "authorization_expired_staff": {
        "sms": "Pre-authorization expired for booking {booking_id}. Action required.",
        "email_subject": "Pre-authorization expired",
        "email_body": "Pre-authorization expired for booking {booking_id}. Please review.",
    },
}
```

Identical structure for `it.py` and `de.py`.

**`apps/notifications/i18n.py`:**

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

**Tests:**

```python
# tests/notifications/test_i18n.py

def test_render_sms_english():
    from apps.notifications.i18n import render
    text = render("booking_approved", "en", "sms",
                  {"restaurant": "Ristorante X", "when": "Mon 20:00", "party": 2, "url": ""})
    assert "confirmed" in text

def test_render_falls_back_to_english_for_unknown_locale():
    from apps.notifications.i18n import render
    text = render("booking_approved", "zh", "sms",
                  {"restaurant": "R", "when": "Mon", "party": 1, "url": ""})
    assert isinstance(text, str)

def test_render_email_returns_subject_and_body():
    from apps.notifications.i18n import render
    subject, body = render("booking_approved", "it", "email",
                           {"restaurant": "R", "when": "Mon", "party": 2, "url": ""})
    assert isinstance(subject, str)
    assert isinstance(body, str)

def test_all_codes_present_in_all_locales():
    from apps.notifications.templates import en, it, de
    for code in en.TEMPLATES:
        assert code in it.TEMPLATES, f"Missing in it: {code}"
        assert code in de.TEMPLATES, f"Missing in de: {code}"
```

**Commit:**
```bash
git add apps/notifications/templates/ apps/notifications/i18n.py
git commit -m "[TASK] 9.2 add localized notification templates (en, it, de)"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/notifications/test_i18n.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task9.2-localized-templates
# Open PR: "[TASK 9.2] Add localized notification templates" → feature/backend-mvp-Phase9-notifications
git checkout feature/backend-mvp-Phase9-notifications
git merge task/backend-mvp-Task9.2-localized-templates
git push origin feature/backend-mvp-Phase9-notifications
```

---

### ❌ Task 9.3 — Routing Rules

Phone is mandatory → SMS always sent. Email optional → sent only when `Customer.email` is set. Staff notifications are in-app only in MVP.

**Branch:** `task/backend-mvp-Task9.3-routing-rules` — created from `feature/backend-mvp-Phase9-notifications`

```bash
git checkout feature/backend-mvp-Phase9-notifications
git pull origin feature/backend-mvp-Phase9-notifications
git checkout -b task/backend-mvp-Task9.3-routing-rules
```

**`apps/notifications/services.py`:**

```python
def notify_customer(booking, code: str, *, raw_token: str | None = None):
    customer = booking.customer
    ctx = _build_ctx(booking, raw_token)
    _send_sms(booking, code, customer.locale, customer.phone, ctx)
    if customer.email:
        _send_email(booking, code, customer.locale, customer.email, ctx)

def notify_staff(booking, code: str):
    from apps.notifications.models import InAppNotification
    InAppNotification.objects.create(booking=booking, code=code)

def _build_ctx(booking, raw_token):
    from django.conf import settings
    url = f"{settings.PUBLIC_BOOKING_BASE_URL}/{raw_token}" if raw_token else ""
    return {
        "restaurant": booking.customer._state.db,  # resolved from tenant context
        "when": booking.starts_at.strftime("%a %d %b %H:%M"),
        "party": booking.party_size,
        "url": url,
        "booking_id": str(booking.id),
    }
```

**Tests:**

```python
# tests/notifications/test_routing.py

def test_sms_always_sent(tenant_db, booking_no_email, mock_twilio):
    from apps.notifications.services import notify_customer
    notify_customer(booking_no_email, "booking_approved")
    assert mock_twilio.messages.create.called

def test_email_sent_when_email_present(tenant_db, booking_with_email, mock_send_mail):
    from apps.notifications.services import notify_customer
    notify_customer(booking_with_email, "booking_approved")
    assert mock_send_mail.called

def test_email_not_sent_when_no_email(tenant_db, booking_no_email, mock_send_mail):
    from apps.notifications.services import notify_customer
    notify_customer(booking_no_email, "booking_approved")
    assert not mock_send_mail.called
```

**Commit:**
```bash
git add apps/notifications/services.py
git commit -m "[TASK] 9.3 add notification routing rules"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/notifications/test_routing.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task9.3-routing-rules
# Open PR: "[TASK 9.3] Add notification routing rules" → feature/backend-mvp-Phase9-notifications
git checkout feature/backend-mvp-Phase9-notifications
git merge task/backend-mvp-Task9.3-routing-rules
git push origin feature/backend-mvp-Phase9-notifications
```

---

### ❌ Task 9.4 — Synchronous Send + Non-Blocking Failure

SMS and email sent synchronously. Failures are logged to `NotificationLog` and never raised to the caller — the booking flow must never be blocked by a notification failure.

**Branch:** `task/backend-mvp-Task9.4-synchronous-send` — created from `feature/backend-mvp-Phase9-notifications`

```bash
git checkout feature/backend-mvp-Phase9-notifications
git pull origin feature/backend-mvp-Phase9-notifications
git checkout -b task/backend-mvp-Task9.4-synchronous-send
```

**`apps/notifications/services.py` (continued):**

```python
from django.core.mail import send_mail
from twilio.base.exceptions import TwilioRestException
from apps.notifications.i18n import render
from apps.notifications.models import NotificationLog
import logging

logger = logging.getLogger("notifications")

def _send_sms(booking, code, locale, phone, ctx):
    text = render(code, locale, "sms", ctx)
    log = NotificationLog.objects.create(
        booking=booking, template_code=code, locale=locale,
        channel="sms", recipient=phone, status="queued",
    )
    try:
        from django.conf import settings
        from apps.notifications.twilio_client import client as twilio_client
        msg = twilio_client.messages.create(to=phone, from_=settings.TWILIO_FROM, body=text)
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
        from django.conf import settings as django_settings
        send_mail(subject, body, django_settings.DEFAULT_FROM_EMAIL,
                  [email], fail_silently=False)
        log.status = "sent"
    except Exception as e:
        log.status = "failed"; log.error_code = e.__class__.__name__
        logger.exception("email_failed", extra={"booking_id": str(booking.id)})
    log.save()
```

**Tests:**

```python
# tests/notifications/test_send.py

def test_sms_failure_does_not_raise(tenant_db, booking, mock_twilio_error):
    from apps.notifications.services import _send_sms
    # Must not raise
    _send_sms(booking, "booking_approved", "en", "+39123", {})

def test_sms_failure_logs_failed_status(tenant_db, booking, mock_twilio_error):
    from apps.notifications.services import _send_sms
    from apps.notifications.models import NotificationLog
    _send_sms(booking, "booking_approved", "en", "+39123", {})
    log = NotificationLog.objects.get(booking=booking, channel="sms")
    assert log.status == "failed"

def test_email_failure_does_not_raise(tenant_db, booking, mock_smtp_error):
    from apps.notifications.services import _send_email
    _send_email(booking, "booking_approved", "en", "a@b.com", {})

def test_sms_success_logs_sent_status(tenant_db, booking, mock_twilio_success):
    from apps.notifications.services import _send_sms
    from apps.notifications.models import NotificationLog
    _send_sms(booking, "booking_approved", "en", "+39123", {})
    log = NotificationLog.objects.get(booking=booking, channel="sms")
    assert log.status == "sent"
```

**Commit:**
```bash
git add apps/notifications/services.py
git commit -m "[TASK] 9.4 add synchronous non-blocking SMS and email send"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/notifications/test_send.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task9.4-synchronous-send
# Open PR: "[TASK 9.4] Add synchronous non-blocking SMS/email send" → feature/backend-mvp-Phase9-notifications
git checkout feature/backend-mvp-Phase9-notifications
git merge task/backend-mvp-Task9.4-synchronous-send
git push origin feature/backend-mvp-Phase9-notifications
```

---

### ❌ Phase 9 complete — merge into feature branch

```bash
# Open PR: "[PHASE 9] Notifications" → feature/backend-mvp
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase9-notifications
git push origin feature/backend-mvp
```

---

## ❌ Phase 10 — Walk-ins

Walk-ins are staff-only records that occupy capacity and can have a table assigned. They are not bookings: no customer link, no status machine, no notifications.

**⚠️ Create this branch only after Phase 9 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase10-walkins` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase10-walkins
git push -u origin feature/backend-mvp-Phase10-walkins
```

---

### ❌ Task 10.1 — Walk-in Model & Endpoint

**Branch:** `task/backend-mvp-Task10.1-walkin-model` — created from `feature/backend-mvp-Phase10-walkins`

```bash
git checkout feature/backend-mvp-Phase10-walkins
git pull origin feature/backend-mvp-Phase10-walkins
git checkout -b task/backend-mvp-Task10.1-walkin-model
```

**`apps/bookings/models.py` (continued):**

```python
class Walkin(TimeStampedModel):
    starts_at = models.DateTimeField()
    party_size = models.PositiveSmallIntegerField()
    table = models.ForeignKey("restaurants.Table", null=True, blank=True,
                              on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
```

Endpoint: `POST /api/v1/walkins` — staff-only (`IsTenantMember`). No phone, no customer FK, no status workflow.

**Tests:**

```python
# tests/bookings/test_walkins.py

def test_create_walkin_staff_only(client, tenant, booking_data):
    response = client.post("/api/v1/walkins/", booking_data, HTTP_HOST=tenant.domain)
    assert response.status_code == 403  # anonymous

def test_create_walkin_succeeds_for_staff(staff_client, tenant):
    from django.utils.timezone import now
    response = staff_client.post("/api/v1/walkins/",
                                 {"starts_at": now().isoformat(), "party_size": 3},
                                 HTTP_HOST=tenant.domain, content_type="application/json")
    assert response.status_code == 201

def test_walkin_has_no_customer_field(tenant_db):
    from apps.bookings.models import Walkin
    assert not hasattr(Walkin, "customer")
```

**Commit:**
```bash
git add apps/bookings/models.py apps/bookings/views.py apps/bookings/urls.py
git commit -m "[TASK] 10.1 add Walkin model and staff endpoint"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/bookings/test_walkins.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task10.1-walkin-model
# Open PR: "[TASK 10.1] Add Walkin model and endpoint" → feature/backend-mvp-Phase10-walkins
git checkout feature/backend-mvp-Phase10-walkins
git merge task/backend-mvp-Task10.1-walkin-model
git push origin feature/backend-mvp-Phase10-walkins
```

---

### ❌ Phase 10 complete — merge into feature branch

```bash
# Open PR: "[PHASE 10] Walk-ins" → feature/backend-mvp
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase10-walkins
git push origin feature/backend-mvp
```
