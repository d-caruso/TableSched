# Branching Strategy — Phase 21: Path-Based Tenant Routing

References:
- Implementation plan: [`06-path-based-routing-Phase21.md`](./06-path-based-routing-Phase21.md)
- Branching rules: [`BRANCHING_STRATEGY.md`](../../BRANCHING_STRATEGY.md)

---

## Global Rules

- **No hardcoded user-facing strings.** The API returns only `error_code`, `reason_code`, and `status` strings — never localized text.
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
└── feature/backend-mvp
    └── feature/backend-mvp-Phase21-path-based-routing   ← created from feature/backend-mvp AFTER Phase 20 merged
        ├── task/backend-mvp-Task21.1-subfolder-middleware
        ├── task/backend-mvp-Task21.2-provisioning-command
        ├── task/backend-mvp-Task21.3-test-fixtures
        ├── task/backend-mvp-Task21.4-env-and-deploy
        └── task/backend-mvp-Task21.5-keepalive
```

---

## ✅ Phase 21 — Path-Based Tenant Routing

Replaces subdomain-based tenant resolution with `TenantSubfolderMiddleware` so tenants are identified by a URL path prefix (`/restaurants/<slug>/`). Enables deployment on Hugging Face Spaces and any other host without wildcard subdomain support. All views, services, models, URL patterns, and the Stripe webhook are unaffected.

**⚠️ Create this branch only after Phase 20 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase21-path-based-routing` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase21-path-based-routing
git push -u origin feature/backend-mvp-Phase21-path-based-routing
```

---

### ✅ Task 21.1 — Switch Middleware, Subfolder Prefix, and Settings/Env Split

Replace `TenantMainMiddleware` with `TenantSubfolderMiddleware` and set `TENANT_SUBFOLDER_PREFIX`. Also introduce the standard Django settings/env split so `pytest` works without any prefix (`pytest backend/`).

**Branch:** `task/backend-mvp-Task21.1-subfolder-middleware` — created from `feature/backend-mvp-Phase21-path-based-routing`

```bash
git checkout feature/backend-mvp-Phase21-path-based-routing
git pull origin feature/backend-mvp-Phase21-path-based-routing
git checkout -b task/backend-mvp-Task21.1-subfolder-middleware
```

**`config/settings/base.py`:**

Remove the `environ.Env.read_env()` call — `base.py` no longer loads any env file directly.

```python
MIDDLEWARE = [
    "django_tenants.middleware.TenantSubfolderMiddleware",  # replaces TenantMainMiddleware
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "apps.memberships.middleware.MembershipMiddleware",
]

TENANT_SUBFOLDER_PREFIX = "restaurants"
```

**`config/settings/dev.py`** — add at the top:
```python
import environ, pathlib
environ.Env.read_env(pathlib.Path(__file__).resolve().parents[2] / ".env")
```

**`config/settings/prod.py`** — add at the top:
```python
import environ, pathlib
environ.Env.read_env(pathlib.Path(__file__).resolve().parents[2] / ".env.prod")
```

**`config/settings/test.py`** (NEW):
```python
"""Test settings — uses local PostgreSQL via .env.test."""
import environ, pathlib
environ.Env.read_env(pathlib.Path(__file__).resolve().parents[2] / ".env.test")

from .base import *  # noqa: F401, F403
```

**`pyproject.toml`** — add pytest config:
```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
```

**`.env.test`** (gitignored) — local PostgreSQL credentials for tests.
**`.env.prod`** (gitignored) — production credentials, set as HF Spaces secret.

Tenant API URLs become:
```
api.tablesched.domenicocaruso.com/restaurants/sushi-new-york/api/v1/bookings/
api.tablesched.domenicocaruso.com/restaurants/trattoria-rome/api/v1/bookings/
```

Public schema URLs are unchanged:
```
api.tablesched.domenicocaruso.com/admin/
api.tablesched.domenicocaruso.com/auth/
api.tablesched.domenicocaruso.com/stripe/webhook/
api.tablesched.domenicocaruso.com/healthz/
```

**i18n rule:** No user-facing strings introduced — no action required.

**Tests:**

```python
# tests/test_urls.py

def test_tenant_path_resolves_to_correct_schema(client, tenant):
    """Request to /restaurants/<slug>/ must activate the correct tenant schema."""
    response = client.get(f"/restaurants/{tenant.schema_name}/api/v1/admin/dashboard/")
    # Unauthenticated → 403, but schema was resolved (not 404)
    assert response.status_code == 403

def test_unknown_tenant_slug_returns_404(client):
    response = client.get("/restaurants/does-not-exist/api/v1/bookings/")
    assert response.status_code == 404

def test_public_schema_healthz_unchanged(client):
    response = client.get("/healthz/")
    assert response.status_code == 200

def test_public_schema_admin_unchanged(client):
    response = client.get("/admin/")
    assert response.status_code in (200, 302)
```

**Commit:**
```bash
git add config/settings/ backend/pyproject.toml tests/test_urls.py
git commit -m "[TASK] 21.1 switch to TenantSubfolderMiddleware with restaurants prefix and settings/env split"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest backend/tests/test_urls.py
pytest backend/
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task21.1-subfolder-middleware
git checkout feature/backend-mvp-Phase21-path-based-routing
git merge task/backend-mvp-Task21.1-subfolder-middleware
git push origin feature/backend-mvp-Phase21-path-based-routing
```

---

### ✅ Task 21.2 — Update Tenant Provisioning Command

With subfolder routing, tenant resolution uses `schema_name` extracted from the URL path — not the `Domain` model. The `Domain` model is still required by `django-tenants` internally but no longer drives HTTP routing. The `--domain` argument becomes optional.

**Branch:** `task/backend-mvp-Task21.2-provisioning-command` — created from `feature/backend-mvp-Phase21-path-based-routing`

```bash
git checkout feature/backend-mvp-Phase21-path-based-routing
git pull origin feature/backend-mvp-Phase21-path-based-routing
git checkout -b task/backend-mvp-Task21.2-provisioning-command
```

**`apps/tenants/management/commands/create_tenant.py`:**

```python
from django.core.management.base import BaseCommand
from apps.tenants.models import Restaurant, Domain

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--name", required=True)
        parser.add_argument("--schema", required=True)
        parser.add_argument("--domain", default="")  # optional with subfolder routing

    def handle(self, *, name, schema, domain, **_):
        r = Restaurant.objects.create(schema_name=schema, name=name)
        if domain:
            Domain.objects.create(domain=domain, tenant=r, is_primary=True)
        self.stdout.write(f"Created tenant schema={schema}")
        self.stdout.write(f"Tenant API prefix: /restaurants/{schema}/")
```

**i18n rule:** Command output is operator-facing only — not user-facing. No translation key required.

**Tests:**

```python
# tests/tenants/test_management.py

def test_create_tenant_without_domain(db):
    """create_tenant must succeed without --domain when using subfolder routing."""
    from django.core.management import call_command
    from apps.tenants.models import Restaurant, Domain
    from io import StringIO

    out = StringIO()
    call_command("create_tenant", name="Sushi New York", schema="sushi_new_york", stdout=out)

    assert Restaurant.objects.filter(schema_name="sushi_new_york").exists()
    assert not Domain.objects.filter(tenant__schema_name="sushi_new_york").exists()
    assert "/restaurants/sushi_new_york/" in out.getvalue()

def test_create_tenant_with_domain_still_works(db):
    """--domain arg must still create a Domain row when provided."""
    from django.core.management import call_command
    from apps.tenants.models import Restaurant, Domain

    call_command("create_tenant", name="Trattoria Rome",
                 schema="trattoria_rome", domain="trattoria-rome.localhost")

    assert Restaurant.objects.filter(schema_name="trattoria_rome").exists()
    assert Domain.objects.filter(domain="trattoria-rome.localhost").exists()
```

**Commit:**
```bash
git add apps/tenants/management/commands/create_tenant.py
git commit -m "[TASK] 21.2 make --domain optional in create_tenant command"
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
git push origin task/backend-mvp-Task21.2-provisioning-command
git checkout feature/backend-mvp-Phase21-path-based-routing
git merge task/backend-mvp-Task21.2-provisioning-command
git push origin feature/backend-mvp-Phase21-path-based-routing
```

---

### ✅ Task 21.3 — Update Integration Test Fixtures

Integration tests currently pass `HTTP_HOST=tenant.domain` to route requests to a tenant schema. With subfolder routing, tenant resolution uses the URL path. All tenant-scoped test client calls must be updated to use the `/restaurants/<schema_name>/` prefix instead.

**Branch:** `task/backend-mvp-Task21.3-test-fixtures` — created from `feature/backend-mvp-Phase21-path-based-routing`

```bash
git checkout feature/backend-mvp-Phase21-path-based-routing
git pull origin feature/backend-mvp-Phase21-path-based-routing
git checkout -b task/backend-mvp-Task21.3-test-fixtures
```

**`tests/conftest.py` — update tenant fixtures:**

```python
import pytest
from apps.tenants.models import Restaurant

@pytest.fixture
def tenant(db):
    return Restaurant.objects.create(schema_name="test_tenant", name="Test Restaurant")

@pytest.fixture
def tenant_prefix(tenant):
    """URL prefix for all tenant-scoped API calls."""
    return f"/restaurants/{tenant.schema_name}"

@pytest.fixture
def tenant_client(client, tenant_prefix):
    """Django test client with tenant prefix pre-applied."""
    class PrefixedClient:
        def get(self, path, **kwargs):
            return client.get(tenant_prefix + path, **kwargs)
        def post(self, path, *args, **kwargs):
            return client.post(tenant_prefix + path, *args, **kwargs)
    return PrefixedClient()
```

All existing test calls using `HTTP_HOST=tenant.domain` must be replaced with the path-prefix approach. Public schema tests (`/healthz/`, `/stripe/webhook/`, `/admin/`) are unchanged — they require no prefix.

**i18n rule:** No user-facing strings introduced.

**Tests:**

```python
# tests/bookings/test_views.py (example updated call)

def test_booking_list_requires_auth(tenant_client):
    response = tenant_client.get("/api/v1/bookings/")
    assert response.status_code == 403  # not 404 — schema was resolved

def test_dashboard_requires_auth(tenant_client):
    response = tenant_client.get("/api/v1/admin/dashboard/")
    assert response.status_code == 403
```

**Commit:**
```bash
git add tests/
git commit -m "[TASK] 21.3 update test fixtures for subfolder tenant routing"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/bookings/test_views.py tests/bookings/test_customer_endpoints.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task21.3-test-fixtures
git checkout feature/backend-mvp-Phase21-path-based-routing
git merge task/backend-mvp-Task21.3-test-fixtures
git push origin feature/backend-mvp-Phase21-path-based-routing
```

---

### ✅ Task 21.4 — Update Env Vars and Deployment Config

Document the new URL shape in `.env.example` and verify that all env-var-driven URL construction is correct for the subfolder architecture. The Stripe webhook and tokenized booking links are unaffected in logic but the deployment notes must reflect the single-domain setup.

**Branch:** `task/backend-mvp-Task21.4-env-and-deploy` — created from `feature/backend-mvp-Phase21-path-based-routing`

```bash
git checkout feature/backend-mvp-Phase21-path-based-routing
git pull origin feature/backend-mvp-Phase21-path-based-routing
git checkout -b task/backend-mvp-Task21.4-env-and-deploy
```

**`backend/.env.example` — update comments:**

```bash
# Tenant API base (subfolder routing):
#   api.tablesched.domenicocaruso.com/restaurants/<schema>/api/v1/
#
# PUBLIC_BOOKING_BASE_URL points to the FRONTEND, not the API.
# It is used to build the tokenized booking link sent to customers via SMS/email.
PUBLIC_BOOKING_BASE_URL=https://tablesched.domenicocaruso.com

# ALLOWED_HOSTS must include only the single API domain (no wildcard needed).
ALLOWED_HOSTS=api.tablesched.domenicocaruso.com
```

**Stripe webhook** — no code change needed. The webhook handler already resolves the tenant via `metadata.tenant_schema` using `schema_context`. It does not depend on the `Host` header or domain routing.

**`Dockerfile`** — no structural changes. The single process serves all tenants via path prefix. Verify `ALLOWED_HOSTS` in `prod.py` reads from the env var (already done in `config/settings/prod.py`).

**i18n rule:** No user-facing strings introduced.

**Tests:**

```python
# tests/test_env.py

def test_public_booking_base_url_has_no_tenant_slug(settings):
    """PUBLIC_BOOKING_BASE_URL must be the frontend root, not a tenant path."""
    url = getattr(settings, "PUBLIC_BOOKING_BASE_URL", "")
    assert url, "PUBLIC_BOOKING_BASE_URL must be set"
    assert "/restaurants/" not in url

# tests/payments/test_webhook.py

def test_stripe_webhook_resolves_tenant_from_metadata(client, tenant, mock_stripe_event):
    """Webhook must resolve tenant via metadata.tenant_schema, not Host header."""
    mock_stripe_event["data"]["object"]["metadata"]["tenant_schema"] = tenant.schema_name
    response = client.post(
        "/stripe/webhook/",
        data=mock_stripe_event,
        content_type="application/json",
    )
    assert response.status_code == 200
```

**Commit:**
```bash
git add backend/.env.example
git commit -m "[TASK] 21.4 update env example and deployment notes for subfolder routing"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/test_env.py tests/payments/test_webhook.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task21.4-env-and-deploy
git checkout feature/backend-mvp-Phase21-path-based-routing
git merge task/backend-mvp-Task21.4-env-and-deploy
git push origin feature/backend-mvp-Phase21-path-based-routing
```

---

### ✅ Task 21.5 — Supabase Keepalive (GitHub Actions)

Supabase free tier pauses the entire project after 7 days of inactivity. A scheduled GitHub Actions workflow pings `/healthz/` every 6 days to prevent this.

**Branch:** `task/backend-mvp-Task21.5-keepalive` — created from `feature/backend-mvp-Phase21-path-based-routing`

```bash
git checkout feature/backend-mvp-Phase21-path-based-routing
git pull origin feature/backend-mvp-Phase21-path-based-routing
git checkout -b task/backend-mvp-Task21.5-keepalive
```

**`.github/workflows/keepalive.yml`:**

```yaml
name: Keepalive
on:
  schedule:
    - cron: '0 9 */6 * *'  # every 6 days at 09:00 UTC

jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - run: curl -f https://tablesched.hf.space/healthz/
```

No secrets required. Free on public repositories and within the 2,000 free minutes/month limit for private repositories (each run uses ~1 second).

**Commit:**
```bash
git add .github/workflows/keepalive.yml
git commit -m "[TASK] 21.5 add GitHub Actions keepalive to prevent Supabase free tier pause"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task21.5-keepalive
git checkout feature/backend-mvp-Phase21-path-based-routing
git merge task/backend-mvp-Task21.5-keepalive
git push origin feature/backend-mvp-Phase21-path-based-routing
```

---

### ✅ Phase 21 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase21-path-based-routing
git push origin feature/backend-mvp
```

When ready to integrate:

```bash
# ⚠️ Only after explicit confirmation
git checkout develop
git merge feature/backend-mvp
git push origin develop
```
