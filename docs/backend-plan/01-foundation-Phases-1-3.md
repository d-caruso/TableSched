# Phases 1–3 — Foundation

Covers project bootstrap, multi-tenancy, and shared infrastructure (error codes, base classes, permissions). Anything domain-specific lives in later phase groups.

---

## Phase 1 — Repository & Project Bootstrap

Branch: `feature/backend-bootstrap`

### Task 1.1 — Backend project layout

```
backend/
  manage.py
  pyproject.toml
  config/                      # Django project
    settings/{base,dev,prod}.py
    urls.py                    # tenant URLs
    urls_public.py             # public URLs (Stripe webhook, healthz)
  apps/
    tenants/                   # public schema: Restaurant (TenantMixin), Domain
    accounts/                  # public schema: User (staff only), allauth glue
    memberships/               # tenant schema: StaffMembership
    customers/                 # tenant schema: Customer (guest), BookingAccessToken
    restaurants/               # tenant schema: settings, opening hours, rooms, tables
    bookings/                  # tenant schema: Booking, Walkin, state machine, sweeps
    payments/                  # tenant schema: Payment + Stripe gateway + webhook handlers
    notifications/             # tenant schema: NotificationLog + Twilio + SMTP gateways + i18n templates
    audit/                     # tenant schema: AuditLog
    common/                    # codes, errors, base models, permissions
  tests/
```

Single-responsibility apps; no domain logic in `common`.

### Task 1.2 — Dependencies

`pyproject.toml`:

```toml
[project]
dependencies = [
  "Django>=5.0,<6.0",
  "djangorestframework",
  "django-tenants",
  "django-allauth",
  "psycopg[binary]",
  "stripe",
  "twilio",
  "django-environ",
]

[project.optional-dependencies]
dev = ["pytest", "pytest-django", "factory-boy", "responses", "ruff", "mypy"]
```

No Celery, no Redis, no broker (technical doc §8). Email uses Django's SMTP backend.

### Task 1.3 — Settings split

`config/settings/base.py` (key bits):

```python
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT", default="5432"),
    }
}
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

SHARED_APPS = (
    "django_tenants",
    "apps.tenants",
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "apps.accounts",
    "allauth",
    "allauth.account",
)
TENANT_APPS = (
    "apps.memberships",
    "apps.customers",
    "apps.restaurants",
    "apps.bookings",
    "apps.payments",
    "apps.notifications",
    "apps.audit",
)
INSTALLED_APPS = list(SHARED_APPS) + [a for a in TENANT_APPS if a not in SHARED_APPS]

TENANT_MODEL = "tenants.Restaurant"
TENANT_DOMAIN_MODEL = "tenants.Domain"

MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    # ... standard Django middleware ...
    "apps.memberships.middleware.MembershipMiddleware",
]
ROOT_URLCONF = "config.urls"
PUBLIC_SCHEMA_URLCONF = "config.urls_public"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
```

---

## Phase 2 — Multi-Tenancy Foundation

Branch: `feature/multi-tenancy`

### Task 2.1 — Tenant + Domain (public schema)

`apps/tenants/models.py`:

```python
from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Restaurant(TenantMixin):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)
    auto_create_schema = True

class Domain(DomainMixin):
    pass
```

Per-restaurant *configuration* (opening hours, deposit policy, etc.) lives in `apps.restaurants` inside the **tenant** schema, not here.

### Task 2.2 — URLConfs

- `config/urls_public.py` → Stripe webhook receiver, `/healthz`. **No** tenant signup endpoint (technical doc: tenants are created by operator only via Django Admin or management command).
- `config/urls.py` → all tenant-scoped APIs under `/api/v1/...`.

Stripe webhook MUST live on the public URLConf because Stripe doesn't know the tenant subdomain. The handler resolves the tenant from `metadata.tenant_schema` and switches schema explicitly (Phase 8).

### Task 2.3 — Tenant provisioning (operator only)

Per technical doc: tenants are created **by the operator only**.

- `apps/tenants/management/commands/create_tenant.py`: thin wrapper that creates the `Restaurant`, the `Domain`, and runs `migrate_schemas` for the new schema. Used in dev and ops.
- Django Admin registration for `Restaurant` and `Domain` so the operator can also create tenants from the admin UI.

```python
# apps/tenants/management/commands/create_tenant.py
from django.core.management.base import BaseCommand
from apps.tenants.models import Restaurant, Domain

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--name", required=True)
        parser.add_argument("--schema", required=True)
        parser.add_argument("--domain", required=True)

    def handle(self, *, name, schema, domain, **_):
        r = Restaurant.objects.create(schema_name=schema, name=name)
        Domain.objects.create(domain=domain, tenant=r, is_primary=True)
```

### Task 2.4 — Migrations workflow

- `python manage.py migrate_schemas --shared` → public schema.
- `python manage.py migrate_schemas` → all tenant schemas.

---

## Phase 3 — Common Infrastructure (codes, errors, base classes)

Branch: `feature/common-infra`

### Task 3.1 — Code-only API responses (i18n constraint, technical doc §9)

The API never returns localized strings (the only exception is staff-written messages, which are passed through as-is). Implement once, reuse everywhere.

`apps/common/codes.py`:

```python
class ErrorCode:
    VALIDATION_FAILED = "validation_failed"
    BOOKING_OUTSIDE_OPENING_HOURS = "booking_outside_opening_hours"
    BOOKING_CUTOFF_PASSED = "booking_cutoff_passed"
    BOOKING_BEYOND_ADVANCE_LIMIT = "booking_beyond_advance_limit"
    BOOKING_SLOT_MISALIGNED = "booking_slot_misaligned"
    BOOKING_TRANSITION_INVALID = "booking_transition_invalid"
    PAYMENT_REQUIRED = "payment_required"
    PAYMENT_AUTHORIZATION_FAILED = "payment_authorization_failed"
    PAYMENT_AUTHORIZATION_EXPIRED = "payment_authorization_expired"
    PAYMENT_CAPTURE_FAILED = "payment_capture_failed"
    NOT_TENANT_MEMBER = "not_tenant_member"
    PERMISSION_DENIED = "permission_denied"
    TOKEN_INVALID = "token_invalid"
    TOKEN_EXPIRED = "token_expired"
    CUTOFF_PASSED = "cutoff_passed"

class ReasonCode:
    STAFF_REJECTION_GENERIC = "staff_rejection_generic"
    PAYMENT_NOT_RECEIVED = "payment_not_received"
    NO_SHOW = "no_show"
    AUTHORIZATION_EXPIRED = "authorization_expired"
```

`apps/common/errors.py`:

```python
from rest_framework.exceptions import APIException

class DomainError(APIException):
    status_code = 400

    def __init__(self, code: str, params: dict | None = None, status: int = 400):
        self.status_code = status
        super().__init__({"error_code": code, "params": params or {}})
```

A DRF custom exception handler returns `{"error_code": "...", "params": {...}}` for every error path. Never a localized string.

### Task 3.2 — Base model

`apps/common/models.py`:

```python
import uuid
from django.db import models

class TimeStampedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

### Task 3.3 — Permissions & membership middleware

`apps/common/permissions.py`:

```python
from rest_framework.permissions import BasePermission

class IsTenantMember(BasePermission):
    def has_permission(self, request, view):
        return getattr(request, "membership", None) is not None

class IsManager(BasePermission):
    def has_permission(self, request, view):
        m = getattr(request, "membership", None)
        return bool(m and m.role == "manager")
```

`apps/memberships/middleware.py` populates `request.membership` once per tenant request:

```python
class MembershipMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.membership = None
        if request.user.is_authenticated:
            from apps.memberships.models import StaffMembership
            request.membership = (
                StaffMembership.objects
                .filter(user=request.user, is_active=True)
                .first()
            )
        return self.get_response(request)
```

Membership lookup is automatically tenant-scoped because `StaffMembership` lives in the tenant schema.
