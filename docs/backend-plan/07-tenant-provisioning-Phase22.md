# Phase 22 — Tenant Provisioning Command

Introduces a single atomic management command `provision_tenant` that replaces the manual multi-step process of onboarding a new restaurant. The existing `create_tenant` command remains for backward compatibility.

The command creates in one shot:
1. The `Restaurant` + `Domain` in the public schema
2. The tenant schema (via `migrate_schemas`)
3. The `accounts.User` in the public schema
4. The `StaffMembership(role=manager)` in the tenant schema

```bash
python manage.py provision_tenant \
    --name "Rome Restaurant" \
    --schema "rome" \
    --admin-email "owner@rome.com" \
    --admin-password "secret"
```

Output:
```
Tenant API prefix: /restaurants/rome/
Login: /auth/login/ (email: owner@rome.com)
```

---

## Why two transaction blocks

`migrate_schemas` runs DDL (CREATE SCHEMA, CREATE TABLE) which cannot run inside a PostgreSQL transaction. The command therefore uses two separate `transaction.atomic()` blocks:

1. First block: create `Restaurant` + `Domain`
2. `migrate_schemas` (outside any transaction)
3. Second block: create `User` + `StaffMembership`

If step 3 fails, steps 1–2 are already committed (the schema exists). The operator must manually drop the schema or re-run with `--force`. This is acceptable for an operator-only command.

---

## Audit note

The existing `AuditLog` model is tenant-scoped — it cannot log platform-level events like tenant creation. Provisioning is auditable via server logs only. A public-schema `ProvisioningLog` is noted in `GAPS_AND_IMPROVEMENTS.md` as a future improvement.

---

## Phase 22 — Tenant Provisioning Command

Branch: `feature/backend-mvp-Phase22-tenant-provisioning`

---

### Task 22.3 — init_platform command

One-time platform setup command. Must be run once after a fresh database is created (local or production) before any other commands or requests.

```bash
python manage.py init_platform
```

What it does:
1. Runs `migrate_schemas --shared` (creates shared tables in the public schema)
2. Creates `Restaurant(schema_name="public", name="Public")` if it doesn't exist
3. Prints confirmation

Idempotent — safe to run multiple times.

**Files:**
- `apps/tenants/management/commands/init_platform.py` — NEW
- `tests/tenants/test_init_platform.py` — NEW

**`apps/tenants/management/commands/init_platform.py`:**

```python
"""One-time platform initialisation command."""

from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.tenants.models import Restaurant


class Command(BaseCommand):
    help = "One-time setup: run shared migrations and create the public tenant row."

    def handle(self, *args, **options):
        call_command("migrate_schemas", "--shared", interactive=False, verbosity=0)
        _, created = Restaurant.objects.get_or_create(
            schema_name="public", defaults={"name": "Public"}
        )
        if created:
            self.stdout.write("Created public tenant row.")
        else:
            self.stdout.write("Public tenant row already exists.")
        self.stdout.write("Platform initialised.")
```

**Tests:**

```python
# tests/tenants/test_init_platform.py

@pytest.mark.django_db(transaction=True)
def test_init_platform_creates_public_tenant():
    from apps.tenants.models import Restaurant
    Restaurant.objects.filter(schema_name="public").delete()
    call_command("init_platform")
    assert Restaurant.objects.filter(schema_name="public").exists()

@pytest.mark.django_db(transaction=True)
def test_init_platform_is_idempotent():
    call_command("init_platform")
    call_command("init_platform")
    from apps.tenants.models import Restaurant
    assert Restaurant.objects.filter(schema_name="public").count() == 1
```

---

### Task 22.2 — Tenant directory endpoint

Public unauthenticated endpoint returning the list of active tenants. Used by the frontend to render a tenant directory when `EXPO_PUBLIC_SHOW_TENANT_DIRECTORY=true`.

```
GET /api/tenants/
```

Response:
```json
[
  {"name": "Rome Restaurant", "schema": "rome", "api_prefix": "/restaurants/rome/"},
  {"name": "Milan Restaurant", "schema": "milan", "api_prefix": "/restaurants/milan/"}
]
```

- Filters `Restaurant.objects.filter(is_active=True).exclude(schema_name="public")`
- No authentication required
- Registered on the **public schema** urlconf (`config/urls_public.py`)

**Files:**
- `apps/tenants/views.py` — NEW
- `apps/tenants/urls.py` — NEW
- `config/urls_public.py` — add `include("apps.tenants.urls")`
- `tests/tenants/test_tenant_directory.py` — NEW

**`apps/tenants/views.py`:**

```python
from django.http import JsonResponse, HttpRequest
from apps.tenants.models import Restaurant


def tenant_directory(request: HttpRequest) -> JsonResponse:
    tenants = (
        Restaurant.objects.filter(is_active=True)
        .exclude(schema_name="public")
        .values("name", "schema_name")
        .order_by("name")
    )
    data = [
        {
            "name": t["name"],
            "schema": t["schema_name"],
            "api_prefix": f"/restaurants/{t['schema_name']}/",
        }
        for t in tenants
    ]
    return JsonResponse(data, safe=False)
```

**`apps/tenants/urls.py`:**

```python
from django.urls import path
from apps.tenants.views import tenant_directory

urlpatterns = [
    path("api/tenants/", tenant_directory, name="tenant-directory"),
]
```

**`config/urls_public.py`** — add:
```python
path("", include("apps.tenants.urls")),
```

**Tests:**

```python
# tests/tenants/test_tenant_directory.py

@pytest.mark.django_db(transaction=True)
def test_tenant_directory_lists_active_tenants(client, public_tenant):
    Restaurant.objects.create(schema_name="rome", name="Rome Restaurant", is_active=True)
    Restaurant.objects.create(schema_name="milan", name="Milan Restaurant", is_active=True)
    Restaurant.objects.create(schema_name="inactive", name="Inactive", is_active=False)

    response = client.get("/api/tenants/")

    assert response.status_code == 200
    data = response.json()
    schemas = [t["schema"] for t in data]
    assert "rome" in schemas
    assert "milan" in schemas
    assert "inactive" not in schemas
    assert "public" not in schemas
    assert data[0]["api_prefix"] == f"/restaurants/{data[0]['schema']}/"


@pytest.mark.django_db(transaction=True)
def test_tenant_directory_requires_no_auth(client, public_tenant):
    response = client.get("/api/tenants/")
    assert response.status_code == 200
```

---

### Task 22.1 — provision_tenant command

**Files:**
- `apps/tenants/management/commands/provision_tenant.py` — NEW
- `tests/tenants/test_provision_tenant.py` — NEW

**`apps/tenants/management/commands/provision_tenant.py`:**

```python
"""Provision a new tenant in one atomic operation."""

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction
from django_tenants.utils import schema_context

from apps.memberships.models import StaffMembership
from apps.tenants.models import Domain, Restaurant

User = get_user_model()


class Command(BaseCommand):
    help = "Provision a new tenant: schema + domain + admin user + manager membership."

    def add_arguments(self, parser):
        parser.add_argument("--name", required=True)
        parser.add_argument("--schema", required=True)
        parser.add_argument("--admin-email", required=True)
        parser.add_argument("--admin-password", required=True)

    def handle(self, *args, **options):
        name = options["name"]
        schema = options["schema"]
        email = options["admin_email"]
        password = options["admin_password"]

        with transaction.atomic():
            restaurant = Restaurant.objects.create(schema_name=schema, name=name)
            Domain.objects.create(domain=schema, tenant=restaurant, is_primary=True)

        call_command("migrate_schemas", schema_name=schema, interactive=False, verbosity=0)

        with transaction.atomic():
            user = User.objects.create_user(username=email, email=email, password=password)
            with schema_context(schema):
                StaffMembership.objects.create(
                    user=user,
                    role=StaffMembership.ROLE_MANAGER,
                    is_active=True,
                )

        self.stdout.write(f"Tenant API prefix: /restaurants/{schema}/")
        self.stdout.write(f"Login: /auth/login/ (email: {email})")
```

**Tests:**

```python
# tests/tenants/test_provision_tenant.py

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django_tenants.utils import schema_context

from apps.memberships.models import StaffMembership
from apps.tenants.models import Domain, Restaurant

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_provision_tenant_creates_all_objects():
    call_command(
        "provision_tenant",
        name="Rome Restaurant",
        schema="rome_test",
        admin_email="owner@rome.com",
        admin_password="testpass123",
    )

    assert Restaurant.objects.filter(schema_name="rome_test").exists()
    assert Domain.objects.filter(domain="rome_test").exists()
    user = User.objects.get(email="owner@rome.com")
    with schema_context("rome_test"):
        assert StaffMembership.objects.filter(
            user=user, role=StaffMembership.ROLE_MANAGER, is_active=True
        ).exists()


@pytest.mark.django_db(transaction=True)
def test_provision_tenant_prints_prefix_and_login(capsys):
    call_command(
        "provision_tenant",
        name="Rome Restaurant",
        schema="rome_print",
        admin_email="print@rome.com",
        admin_password="testpass123",
    )

    out = capsys.readouterr().out
    assert "/restaurants/rome_print/" in out
    assert "print@rome.com" in out


@pytest.mark.django_db(transaction=True)
def test_provision_tenant_fails_if_schema_exists():
    call_command(
        "provision_tenant",
        name="Rome Restaurant",
        schema="rome_dup",
        admin_email="a@rome.com",
        admin_password="testpass123",
    )
    with pytest.raises(Exception):
        call_command(
            "provision_tenant",
            name="Rome 2",
            schema="rome_dup",
            admin_email="b@rome.com",
            admin_password="testpass123",
        )
```

---

### Task 22.5 — Provisioned user utility (verified email for all operator-created users)

Operator-provisioned accounts (tenant admins, manager-invited staff) must skip the self-signup email verification flow. A shared `create_provisioned_user()` utility centralises this: any future staff invitation feature must call it instead of `create_user()` directly.

**Why:** allauth requires an `EmailAddress(verified=True)` row to issue JWT tokens. `create_user()` alone does not create this row. Without it, login returns 403 and sends a verification email.

**Files:**
- `apps/accounts/utils.py` — NEW
- `apps/tenants/management/commands/provision_tenant.py` — updated to use utility
- `tests/accounts/test_provisioned_user.py` — NEW

**`apps/accounts/utils.py`:**

```python
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress

User = get_user_model()

def create_provisioned_user(email: str, password: str) -> User:
    """Create a user with a pre-verified email address.

    Used for operator-provisioned accounts (tenant admins, manager-invited staff)
    that bypass the self-signup email verification flow.
    """
    user = User.objects.create_user(username=email, email=email, password=password)
    EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)
    return user
```

**Tests:**

```python
# tests/accounts/test_provisioned_user.py

@pytest.mark.django_db
def test_creates_user_with_verified_email(public_tenant):
    user = create_provisioned_user("staff@example.com", "pass1234")
    email_addr = EmailAddress.objects.get(user=user)
    assert email_addr.verified is True
    assert email_addr.primary is True

@pytest.mark.django_db
def test_user_can_login_without_verification(client, public_tenant):
    create_provisioned_user("staff2@example.com", "pass1234")
    response = client.post(
        "/_allauth/app/v1/auth/login",
        {"login": "staff2@example.com", "password": "pass1234"},
        content_type="application/json",
    )
    assert response.status_code == 200
```
