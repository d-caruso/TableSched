# Phases 11–16 — Ops

Covers opportunistic background maintenance, the audit log, security hardening, the test strategy, observability, and deployment preparation.

---

## Phase 11 — Opportunistic Background Maintenance

Branch: `feature/backend-mvp-Phase11-opportunistic-maintenance`

No Celery/Redis (technical doc §8). Opportunistic maintenance runs lazily when staff loads the dashboard.

### Task 11.1 — Opportunistic maintenance service

`apps/bookings/services/opportunistic_maintenance.py`:

```python
from datetime import timedelta
from django.utils.timezone import now
from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services.state_machine import transition
from apps.payments.models import Payment, PaymentStatus
from apps.notifications import services as notifications

def run_opportunistic_maintenance():
    _expire_pending_payments()
    _expire_authorized_deposits()
    _reconcile_payments()

def _expire_pending_payments():
    # Long-term flow: payment link expired
    qs = Booking.objects.filter(
        status=BookingStatus.PENDING_PAYMENT,
        payment_due_at__lt=now(),
    )[:200]
    for b in qs:
        transition(b, BookingStatus.EXPIRED); b.save()
        notifications.notify_customer(b, "booking_expired")

def _expire_authorized_deposits():
    # Stripe pre-auth ~7 days; we do NOT auto-cancel the booking.
    # Staff must choose: confirm without deposit / request payment again / decline.
    qs = (
        Payment.objects
        .filter(
            status=PaymentStatus.AUTHORIZED,
            booking__status=BookingStatus.PENDING_REVIEW,
            created_at__lt=now() - timedelta(days=6),
        )[:200]
    )
    for p in qs:
        p.status = PaymentStatus.FAILED  # authorization no longer usable
        p.save()
        b = p.booking
        transition(b, BookingStatus.AUTHORIZATION_EXPIRED); b.save()
        notifications.notify_staff(b, "authorization_expired_staff")

def _reconcile_payments():
    # Best-effort reconciliation for items stuck PENDING beyond a small window.
    # Implementation queries Stripe for the latest state and updates Payment.status.
    ...
```

Each helper is bounded (`[:200]`) so dashboard load can never time out on a backlog. Idempotent - safe to call concurrently.

### Task 11.2 — Dashboard endpoint

`GET /api/v1/admin/dashboard` runs opportunistic maintenance then returns counts + recent bookings. Manager + staff allowed.

```python
class AdminDashboardView(APIView):
    permission_classes = [IsTenantMember]

    def get(self, request):
        opportunistic_maintenance.run_opportunistic_maintenance()
        data = {
            "counts_by_status": _counts_by_status(),
            "recent": list(
                Booking.objects.order_by("-created_at")[:50]
                .values("id", "status", "starts_at", "party_size")
            ),
        }
        return Response(data)
```

---

## Phase 12 — Audit Log

Branch: `feature/audit-log`

### Task 12.1 — AuditLog model

```python
class AuditLog(TimeStampedModel):
    actor = models.ForeignKey("memberships.StaffMembership", null=True,
                              on_delete=models.SET_NULL)
    action = models.CharField(max_length=64)         # booking.approve, payment.refund, ...
    target_type = models.CharField(max_length=64)
    target_id = models.UUIDField()
    payload = models.JSONField(default=dict)
```

### Task 12.2 — Single write helper

`apps/audit/services.py`:

```python
def record(*, actor, action, target, payload=None):
    AuditLog.objects.create(
        actor=actor, action=action,
        target_type=target.__class__.__name__,
        target_id=target.id, payload=payload or {},
    )
```

Called explicitly from booking, payment, and refund services. No automatic signals (Fail Fast + explicit > magic).

---

## Phase 13 — Security Hardening

Branch: `feature/security`

### Task 13.1 — Tenant isolation tests

Pytest with `django_tenants` fixtures. Create two tenants, ensure tenant A cannot access tenant B's bookings/payments via any endpoint or webhook path.

### Task 13.2 — Stripe signature verification

Already enforced (Phase 8). Add a regression test posting an unsigned payload → expect 400.

### Task 13.3 — Twilio + SMTP credentials

Loaded from env only; never echoed in API responses; redacted from logs via a small log filter.

### Task 13.4 — Token endpoint hardening

- Always compare hashes (no plaintext token in DB).
- Constant-time hash comparison via `hmac.compare_digest`.
- Rate-limit `/api/v1/public/bookings/<token>/` with DRF `AnonRateThrottle`.
- Never include the raw token in audit logs.

```python
import hmac

def verify_token(raw: str, stored_hash: str) -> bool:
    return hmac.compare_digest(hash_token(raw), stored_hash)
```

### Task 13.5 — Public booking-request rate limit

DRF `AnonRateThrottle` on `/api/v1/public/bookings`. No Redis: use the local-memory cache backend (acceptable per technical doc §8).

```python
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "30/min"},
}
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
```

---

## Phase 14 — Testing Strategy

Branch: `feature/test-suite`

Per CLAUDE.md "Test your code — no feature is complete without tests".

### Task 14.1 — Layered tests

- **Unit**: services (state machine, opening-hours, validators, opportunistic maintenance, gateway adapters with mocked Stripe/Twilio/SMTP).
- **API**: DRF `APIClient` against a tenant subdomain, full happy paths and code-form error responses.
- **Webhook**: Stripe event fixtures (`payment_intent.amount_capturable_updated`, `succeeded`, `canceled`, `checkout.session.completed`, etc.) → assert booking + payment transitions.
- **Tenant isolation**: cross-tenant access denied.
- **Token flow**: issue → use → expire → reject.
- **Localization**: each template renders in `en`, `it`, `de` and falls back to `en` for unknown locale.

### Task 14.2 — Tooling

- `pytest-django` with `--reuse-db`.
- `factory_boy` for fixtures (Restaurant, User, Membership, Customer, Booking, Payment).
- `responses` for Twilio + SMTP mocking, official Stripe test events.

Coverage target: ≥85% on `apps/bookings`, `apps/payments`, `apps/notifications`, `apps/customers`.

---

## Phase 15 — Observability

Branch: `feature/observability`

Technical doc §14 minimum:

- Structured JSON logging via stdlib `logging` (no extra dependency).
- Distinct loggers: `bookings`, `payments.webhook`, `notifications`, `audit`.
- Each booking/payment/notification action logs `tenant_schema`, `booking_id`, `action`, `result`.
- A `/healthz` endpoint on the public URLConf.

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        },
    },
    "handlers": {
        "stdout": {"class": "logging.StreamHandler", "formatter": "json"},
    },
    "loggers": {
        "bookings":           {"handlers": ["stdout"], "level": "INFO"},
        "payments.webhook":   {"handlers": ["stdout"], "level": "INFO"},
        "notifications":      {"handlers": ["stdout"], "level": "INFO"},
        "audit":              {"handlers": ["stdout"], "level": "INFO"},
    },
}
```

No APM/error-tracking dependency in MVP (YAGNI). Hosting platform logs are sufficient.

---

## Phase 16 — Deployment Prep (Hugging Face + managed Postgres)

Branch: `feature/deploy`

### Task 16.1 — Container

Single `Dockerfile` running `gunicorn config.wsgi`. No Redis, no worker. Migrations run on startup:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir .
COPY . .
CMD ["sh", "-lc", "python manage.py migrate_schemas --shared && python manage.py migrate_schemas && gunicorn config.wsgi --bind 0.0.0.0:$PORT"]
```

### Task 16.2 — Environment variables

Loaded via `django-environ`:

- `DJANGO_SECRET_KEY`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `STRIPE_API_KEY`, `STRIPE_WEBHOOK_SECRET`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM`
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
- `ALLOWED_HOSTS`, `PUBLIC_DOMAIN`
- `PUBLIC_BOOKING_RETURN_URL`, `PUBLIC_BOOKING_CANCEL_URL`

### Task 16.3 — Domain & subdomains

Per technical doc §13:
- Web app: `tablesched.domenicocaruso.com`
- API: `api.tablesched.domenicocaruso.com`

Tenants resolve via subdomains (e.g. `api.<tenant>.tablesched.domenicocaruso.com`) mapped to `Domain` rows. If Hugging Face cannot serve wildcard subdomains, switching backend host is the agreed contingency.
