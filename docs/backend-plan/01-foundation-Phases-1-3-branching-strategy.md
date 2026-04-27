# Branching Strategy — Phases 1–3: Foundation

References:
- Implementation plan: [`01-foundation-Phases-1-3.md`](./01-foundation-Phases-1-3.md)
- Branching rules: [`BRANCHING_STRATEGY.md`](../../BRANCHING_STRATEGY.md)

---

## Global Rules

- **No hardcoded user-facing strings.** All text shown to the user must use i18n translation keys. The API returns only `error_code`, `reason_code`, and `status` strings — never localized text (except staff-written `staff_message` fields).
- **Tests are mandatory** for every task that introduces logic. Write unit tests and integration tests in the same task branch, before merging.
- **Each task branch lifecycle:** create from parent → implement → commit → pre-merge checks → push → merge into parent.
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

All checks must pass (0 errors, 0 failures) before merging.

---

## Branch Hierarchy

```
develop
└── feature/backend-mvp                              ← created from develop
    ├── feature/backend-mvp-Phase1-bootstrap         ← created from feature/backend-mvp
    │   ├── task/backend-mvp-Task1.1-project-layout
    │   ├── task/backend-mvp-Task1.2-dependencies
    │   └── task/backend-mvp-Task1.3-settings
    ├── feature/backend-mvp-Phase2-multi-tenancy     ← created from feature/backend-mvp AFTER Phase 1 merged
    │   ├── task/backend-mvp-Task2.1-tenant-domain
    │   ├── task/backend-mvp-Task2.2-urlconfs
    │   ├── task/backend-mvp-Task2.3-tenant-provisioning
    │   └── task/backend-mvp-Task2.4-migrations
    └── feature/backend-mvp-Phase3-common-infra      ← created from feature/backend-mvp AFTER Phase 2 merged
        ├── task/backend-mvp-Task3.1-codes
        ├── task/backend-mvp-Task3.2-base-model
        └── task/backend-mvp-Task3.3-permissions
```

---

## Root Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b feature/backend-mvp
git push -u origin feature/backend-mvp
```

---

## ❌ Phase 1 — Repository & Project Bootstrap

Sets up the Django project skeleton: directory layout, dependencies, and settings split. No domain logic — just the scaffolding every subsequent phase builds on.

**Branch:** `feature/backend-mvp-Phase1-bootstrap` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase1-bootstrap
git push -u origin feature/backend-mvp-Phase1-bootstrap
```

---

### ✅ Task 1.1 — Project Layout

Create the directory structure for the entire backend. No logic, no user-facing strings.

**Branch:** `task/backend-mvp-Task1.1-project-layout` — created from `feature/backend-mvp-Phase1-bootstrap`

```bash
git checkout feature/backend-mvp-Phase1-bootstrap
git pull origin feature/backend-mvp-Phase1-bootstrap
git checkout -b task/backend-mvp-Task1.1-project-layout
```

**Directory structure to create:**

```
backend/
  manage.py
  pyproject.toml
  config/
    settings/
      base.py
      dev.py
      prod.py
    urls.py
    urls_public.py
  apps/
    tenants/
    accounts/
    memberships/
    customers/
    restaurants/
    bookings/
    payments/
    notifications/
    audit/
    common/
  tests/
```

**Tests:** None — no logic introduced.

**Commit:**
```bash
git add .
git commit -m "[TASK] 1.1 create backend project layout"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task1.1-project-layout
git checkout feature/backend-mvp-Phase1-bootstrap
git merge task/backend-mvp-Task1.1-project-layout
git push origin feature/backend-mvp-Phase1-bootstrap
```

---

### ❌ Task 1.2 — Dependencies

Define all project dependencies in `pyproject.toml`. No logic, no user-facing strings.

**Branch:** `task/backend-mvp-Task1.2-dependencies` — created from `feature/backend-mvp-Phase1-bootstrap`

```bash
git checkout feature/backend-mvp-Phase1-bootstrap
git pull origin feature/backend-mvp-Phase1-bootstrap
git checkout -b task/backend-mvp-Task1.2-dependencies
```

**`pyproject.toml`:**

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

No Celery, no Redis (technical doc §8).

**Tests:** None — no logic introduced.

**Commit:**
```bash
git add pyproject.toml
git commit -m "[TASK] 1.2 define project dependencies"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task1.2-dependencies
git checkout feature/backend-mvp-Phase1-bootstrap
git merge task/backend-mvp-Task1.2-dependencies
git push origin feature/backend-mvp-Phase1-bootstrap
```

---

### ❌ Task 1.3 — Settings Split

Create `config/settings/{base,dev,prod}.py`. No user-facing strings — all values from environment variables.

**Branch:** `task/backend-mvp-Task1.3-settings` — created from `feature/backend-mvp-Phase1-bootstrap`

```bash
git checkout feature/backend-mvp-Phase1-bootstrap
git pull origin feature/backend-mvp-Phase1-bootstrap
git checkout -b task/backend-mvp-Task1.3-settings
```

**`config/settings/base.py` (key sections):**

```python
import environ

env = environ.Env()

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
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
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

**Tests:**

```python
# tests/test_settings.py
def test_django_check_passes():
    """Django system check must pass with no errors."""
    from django.core.management import call_command
    call_command("check")
```

**Commit:**
```bash
git add config/
git commit -m "[TASK] 1.3 split settings into base/dev/prod"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/test_settings.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task1.3-settings
git checkout feature/backend-mvp-Phase1-bootstrap
git merge task/backend-mvp-Task1.3-settings
git push origin feature/backend-mvp-Phase1-bootstrap
```

---

### ❌ Phase 1 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase1-bootstrap
git push origin feature/backend-mvp
```

---

## ❌ Phase 2 — Multi-Tenancy Foundation

Establishes the django-tenants schema-per-tenant setup: the public-schema models (Restaurant, Domain), URL routing split, the operator provisioning command, and the migrations workflow.

**⚠️ Create this branch only after Phase 1 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase2-multi-tenancy` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase2-multi-tenancy
git push -u origin feature/backend-mvp-Phase2-multi-tenancy
```

---

### ❌ Task 2.1 — Tenant & Domain Models

Define `Restaurant` (TenantMixin) and `Domain` (DomainMixin) in the public schema. No user-facing strings.

**Branch:** `task/backend-mvp-Task2.1-tenant-domain` — created from `feature/backend-mvp-Phase2-multi-tenancy`

```bash
git checkout feature/backend-mvp-Phase2-multi-tenancy
git pull origin feature/backend-mvp-Phase2-multi-tenancy
git checkout -b task/backend-mvp-Task2.1-tenant-domain
```

**`apps/tenants/models.py`:**

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

Per-restaurant configuration (opening hours, deposit policy) belongs in the tenant schema under `apps.restaurants` — not here.

**Tests:**

```python
# tests/tenants/test_models.py

def test_restaurant_creates_schema(db):
    """Creating a Restaurant must auto-create its Postgres schema."""
    from apps.tenants.models import Restaurant, Domain
    r = Restaurant.objects.create(schema_name="test_rest", name="Test Restaurant")
    Domain.objects.create(domain="test-rest.localhost", tenant=r, is_primary=True)
    from django.db import connection
    schemas = connection.introspection.get_table_list(connection.cursor())
    assert any(s.name == "test_rest" for s in schemas)

def test_tenant_schema_isolation(db):
    """Booking created in tenant A must not appear in tenant B."""
    # Create two tenants and assert cross-schema isolation
    ...
```

**Commit:**
```bash
git add apps/tenants/
git commit -m "[TASK] 2.1 add Restaurant and Domain models"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/tenants/test_models.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task2.1-tenant-domain
git checkout feature/backend-mvp-Phase2-multi-tenancy
git merge task/backend-mvp-Task2.1-tenant-domain
git push origin feature/backend-mvp-Phase2-multi-tenancy
```

---

### ❌ Task 2.2 — URLConfs Split

Separate public schema routes (Stripe webhook, `/healthz`) from tenant-scoped API routes (`/api/v1/...`). Stripe webhook lives on the public URLConf because Stripe doesn't know the tenant subdomain; the handler resolves the tenant from `metadata.tenant_schema`.

**Branch:** `task/backend-mvp-Task2.2-urlconfs` — created from `feature/backend-mvp-Phase2-multi-tenancy`

```bash
git checkout feature/backend-mvp-Phase2-multi-tenancy
git pull origin feature/backend-mvp-Phase2-multi-tenancy
git checkout -b task/backend-mvp-Task2.2-urlconfs
```

**`config/urls_public.py`:**

```python
from django.urls import path
from apps.payments.views import stripe_webhook

urlpatterns = [
    path("stripe/webhook/", stripe_webhook, name="stripe-webhook"),
    path("healthz/", lambda request: HttpResponse("ok"), name="healthz"),
]
```

**`config/urls.py`:**

```python
from django.urls import path, include

urlpatterns = [
    path("api/v1/", include("apps.bookings.urls")),
    path("api/v1/", include("apps.restaurants.urls")),
    path("api/v1/", include("apps.payments.urls")),
    path("api/v1/", include("apps.notifications.urls")),
]
```

**Tests:**

```python
# tests/test_urls.py

def test_healthz_on_public_schema(client):
    """GET /healthz/ must return 200 from the public schema."""
    response = client.get("/healthz/")
    assert response.status_code == 200

def test_tenant_api_requires_tenant_host(client):
    """Tenant API routes must not be reachable from the public schema."""
    response = client.get("/api/v1/bookings/")
    assert response.status_code in (404, 400)
```

**Commit:**
```bash
git add config/urls.py config/urls_public.py
git commit -m "[TASK] 2.2 split public and tenant URLConfs"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/test_urls.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task2.2-urlconfs
git checkout feature/backend-mvp-Phase2-multi-tenancy
git merge task/backend-mvp-Task2.2-urlconfs
git push origin feature/backend-mvp-Phase2-multi-tenancy
```

---

### ❌ Task 2.3 — Tenant Provisioning (Operator Only)

Tenants are created exclusively by the operator via Django Admin or a management command. No self-service signup. No user-facing strings (the command prints internal status only, not localized text).

**Branch:** `task/backend-mvp-Task2.3-tenant-provisioning` — created from `feature/backend-mvp-Phase2-multi-tenancy`

```bash
git checkout feature/backend-mvp-Phase2-multi-tenancy
git pull origin feature/backend-mvp-Phase2-multi-tenancy
git checkout -b task/backend-mvp-Task2.3-tenant-provisioning
```

**`apps/tenants/management/commands/create_tenant.py`:**

```python
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
        self.stdout.write(f"Created tenant schema={schema} domain={domain}")
```

Register both models in Django Admin (`apps/tenants/admin.py`) for operator UI access.

**Tests:**

```python
# tests/tenants/test_management.py

def test_create_tenant_command(db):
    """create_tenant command must create Restaurant and Domain rows."""
    from django.core.management import call_command
    from apps.tenants.models import Restaurant, Domain

    call_command("create_tenant", name="Ristorante X", schema="rest_x", domain="rest-x.localhost")

    assert Restaurant.objects.filter(schema_name="rest_x").exists()
    assert Domain.objects.filter(domain="rest-x.localhost").exists()
```

**Commit:**
```bash
git add apps/tenants/
git commit -m "[TASK] 2.3 add tenant provisioning command and admin"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/tenants/test_management.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task2.3-tenant-provisioning
git checkout feature/backend-mvp-Phase2-multi-tenancy
git merge task/backend-mvp-Task2.3-tenant-provisioning
git push origin feature/backend-mvp-Phase2-multi-tenancy
```

---

### ❌ Task 2.4 — Migrations Workflow

Documents the migration commands. No new code — execution-only.

**Branch:** `task/backend-mvp-Task2.4-migrations` — created from `feature/backend-mvp-Phase2-multi-tenancy`

```bash
git checkout feature/backend-mvp-Phase2-multi-tenancy
git pull origin feature/backend-mvp-Phase2-multi-tenancy
git checkout -b task/backend-mvp-Task2.4-migrations
```

**Commands to run after any model change:**

```bash
# Public schema only
python manage.py migrate_schemas --shared

# All tenant schemas
python manage.py migrate_schemas
```

**Tests:** None — no logic introduced.

**Commit:**
```bash
git add .
git commit -m "[TASK] 2.4 run initial shared and tenant migrations"
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task2.4-migrations
git checkout feature/backend-mvp-Phase2-multi-tenancy
git merge task/backend-mvp-Task2.4-migrations
git push origin feature/backend-mvp-Phase2-multi-tenancy
```

---

### ❌ Phase 2 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase2-multi-tenancy
git push origin feature/backend-mvp
```

---

## ❌ Phase 3 — Common Infrastructure

Establishes the shared foundation: error/reason codes, the `DomainError` exception (code-only, no localized strings), the `TimeStampedModel` base, and the DRF permission classes + membership middleware.

**⚠️ Create this branch only after Phase 2 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase3-common-infra` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase3-common-infra
git push -u origin feature/backend-mvp-Phase3-common-infra
```

---

### ❌ Task 3.1 — Error & Reason Codes

Defines the complete set of error and reason codes and the `DomainError` exception. **No localized strings anywhere** — the API returns `error_code` + `params` only. The frontend maps codes to localized text.

**Branch:** `task/backend-mvp-Task3.1-codes` — created from `feature/backend-mvp-Phase3-common-infra`

```bash
git checkout feature/backend-mvp-Phase3-common-infra
git pull origin feature/backend-mvp-Phase3-common-infra
git checkout -b task/backend-mvp-Task3.1-codes
```

**`apps/common/codes.py`:**

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

**`apps/common/errors.py`:**

```python
from rest_framework.exceptions import APIException

class DomainError(APIException):
    status_code = 400

    def __init__(self, code: str, params: dict | None = None, status: int = 400):
        self.status_code = status
        super().__init__({"error_code": code, "params": params or {}})
```

**Custom DRF exception handler** (`apps/common/exception_handler.py`):

```python
from rest_framework.views import exception_handler as drf_handler

def custom_exception_handler(exc, context):
    response = drf_handler(exc, context)
    if response is not None and not isinstance(response.data, dict):
        response.data = {"error_code": "validation_failed", "params": response.data}
    return response
```

Register in settings: `REST_FRAMEWORK = {"EXCEPTION_HANDLER": "apps.common.exception_handler.custom_exception_handler"}`.

**Tests:**

```python
# tests/common/test_errors.py

def test_domain_error_shape():
    """DomainError must return error_code + params, no localized strings."""
    from apps.common.errors import DomainError
    from apps.common.codes import ErrorCode

    exc = DomainError(ErrorCode.VALIDATION_FAILED, {"field": "starts_at"})
    assert exc.detail == {"error_code": "validation_failed", "params": {"field": "starts_at"}}

def test_domain_error_no_localized_string():
    """DomainError detail must not contain human-readable sentences."""
    from apps.common.errors import DomainError
    exc = DomainError("booking_cutoff_passed")
    assert isinstance(exc.detail["error_code"], str)
    assert " " not in exc.detail["error_code"]  # codes use underscores, not spaces
```

**Commit:**
```bash
git add apps/common/codes.py apps/common/errors.py apps/common/exception_handler.py
git commit -m "[TASK] 3.1 add error and reason codes, DomainError, exception handler"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/common/test_errors.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task3.1-codes
git checkout feature/backend-mvp-Phase3-common-infra
git merge task/backend-mvp-Task3.1-codes
git push origin feature/backend-mvp-Phase3-common-infra
```

---

### ❌ Task 3.2 — Base Model

Adds `TimeStampedModel` with UUID primary key and auto timestamps. All tenant-schema models inherit from this.

**Branch:** `task/backend-mvp-Task3.2-base-model` — created from `feature/backend-mvp-Phase3-common-infra`

```bash
git checkout feature/backend-mvp-Phase3-common-infra
git pull origin feature/backend-mvp-Phase3-common-infra
git checkout -b task/backend-mvp-Task3.2-base-model
```

**`apps/common/models.py`:**

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

**Tests:**

```python
# tests/common/test_models.py

def test_timestamped_model_uuid_pk(db):
    """TimeStampedModel subclass must get a UUID PK and auto timestamps."""
    from apps.common.models import TimeStampedModel
    from django.db import models

    class SampleModel(TimeStampedModel):
        class Meta:
            app_label = "common"

    instance = SampleModel()
    assert isinstance(instance.id, uuid.UUID)

def test_timestamped_model_created_at(db):
    from django.utils import timezone
    # Verify created_at is set on save
    ...
```

**Commit:**
```bash
git add apps/common/models.py
git commit -m "[TASK] 3.2 add TimeStampedModel base class"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/common/test_models.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task3.2-base-model
git checkout feature/backend-mvp-Phase3-common-infra
git merge task/backend-mvp-Task3.2-base-model
git push origin feature/backend-mvp-Phase3-common-infra
```

---

### ❌ Task 3.3 — Permissions & Membership Middleware

Implements `IsTenantMember`, `IsManager` DRF permission classes and `MembershipMiddleware` which resolves `request.membership` once per tenant request.

**Branch:** `task/backend-mvp-Task3.3-permissions` — created from `feature/backend-mvp-Phase3-common-infra`

```bash
git checkout feature/backend-mvp-Phase3-common-infra
git pull origin feature/backend-mvp-Phase3-common-infra
git checkout -b task/backend-mvp-Task3.3-permissions
```

**`apps/common/permissions.py`:**

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

**`apps/memberships/middleware.py`:**

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

**Tests:**

```python
# tests/common/test_permissions.py

def test_is_tenant_member_allows_with_membership(rf):
    from apps.common.permissions import IsTenantMember
    request = rf.get("/")
    request.membership = object()   # any truthy value
    assert IsTenantMember().has_permission(request, None) is True

def test_is_tenant_member_denies_without_membership(rf):
    from apps.common.permissions import IsTenantMember
    request = rf.get("/")
    request.membership = None
    assert IsTenantMember().has_permission(request, None) is False

def test_is_manager_denies_staff_role(rf):
    from apps.common.permissions import IsManager
    from unittest.mock import MagicMock
    request = rf.get("/")
    request.membership = MagicMock(role="staff")
    assert IsManager().has_permission(request, None) is False

def test_is_manager_allows_manager_role(rf):
    from apps.common.permissions import IsManager
    from unittest.mock import MagicMock
    request = rf.get("/")
    request.membership = MagicMock(role="manager")
    assert IsManager().has_permission(request, None) is True

# tests/memberships/test_middleware.py (integration)

def test_middleware_sets_membership_for_authenticated_staff(tenant_client, staff_user, membership):
    """Middleware must populate request.membership for authenticated staff."""
    tenant_client.force_login(staff_user)
    response = tenant_client.get("/api/v1/admin/dashboard/")
    assert response.wsgi_request.membership == membership

def test_middleware_sets_none_for_anonymous(tenant_client):
    response = tenant_client.get("/api/v1/admin/dashboard/")
    assert response.wsgi_request.membership is None
```

**Commit:**
```bash
git add apps/common/permissions.py apps/memberships/middleware.py
git commit -m "[TASK] 3.3 add permission classes and membership middleware"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/common/test_permissions.py tests/memberships/test_middleware.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task3.3-permissions
git checkout feature/backend-mvp-Phase3-common-infra
git merge task/backend-mvp-Task3.3-permissions
git push origin feature/backend-mvp-Phase3-common-infra
```

---

### ❌ Phase 3 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase3-common-infra
git push origin feature/backend-mvp
```
