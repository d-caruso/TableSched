# Phase 21 — Path-Based Tenant Routing

Replaces subdomain-based tenant resolution with path-based routing using `TenantSubfolderMiddleware`. This enables deployment on hosting providers that do not support wildcard subdomains (e.g. Hugging Face Spaces).

Tenant API URLs change from:
```
resto-a.api.tablesched.domenicocaruso.com/api/v1/bookings/
```
to:
```
api.tablesched.domenicocaruso.com/restaurants/resto-a/api/v1/bookings/
```

All views, services, models, URL patterns, and the Stripe webhook handler are unaffected.

This phase also introduces the standard Django settings/env split so that `pytest` works without any prefix:

- `config/settings/test.py` — new, reads `.env.test` (local PostgreSQL)
- `config/settings/dev.py` — reads `.env` (Supabase)
- `config/settings/prod.py` — reads `.env.prod`
- `pyproject.toml` — pins `DJANGO_SETTINGS_MODULE = "config.settings.test"` for pytest
- `base.py` — no longer calls `read_env` directly The Stripe webhook already resolves the tenant via `metadata.tenant_schema` and `schema_context` — it is fully path-independent.

---

## Phase 21 — Path-Based Tenant Routing

Branch: `feature/backend-mvp-Phase21-path-based-routing`

---

### Task 21.1 — Switch middleware and add subfolder prefix

Replace `TenantMainMiddleware` with `TenantSubfolderMiddleware` in `config/settings/base.py` and set the subfolder prefix.

Required changes in `config/settings/base.py`:

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

No other settings change. `ROOT_URLCONF` and `PUBLIC_SCHEMA_URLCONF` remain the same.

Tests:
- A request to `/restaurants/resto-a/api/v1/bookings/` resolves to tenant `resto_a`.
- A request to `/admin/` resolves to the public schema.
- A request with an unknown slug returns 404.

---

### Task 21.2 — Update tenant provisioning command

With subfolder routing, tenant resolution is by `schema_name` extracted from the URL path — not by `Domain`. The `Domain` model is still required by `django-tenants` internally but no longer drives HTTP routing.

Update `apps/tenants/management/commands/create_tenant.py`:

Required behavior:
- The `--domain` argument becomes optional (default: empty string).
- A `Domain` row is still created if `--domain` is provided, for forward compatibility.
- The command output must include the resulting API path prefix so the operator knows the correct URL: `Tenant API prefix: /restaurants/<schema>/`.
- No other behavior changes.

Tests:
- Command with only `--name` and `--schema` creates the `Restaurant` row and prints the API prefix.
- Command with `--domain` additionally creates the `Domain` row.

---

### Task 21.3 — Update integration test fixtures

Integration tests currently set `HTTP_HOST` to route to a tenant. With subfolder routing, tenant resolution uses the URL path instead.

Required changes in `tests/`:
- Remove `HTTP_HOST=tenant.domain` from all test client calls.
- Prefix tenant API paths with `/restaurants/<schema_name>/` in all tenant-scoped requests.
- Update `conftest.py` tenant fixtures to expose the path prefix rather than a domain string.
- Public schema tests (healthz, stripe webhook, admin) require no path prefix and are unaffected.

Tests:
- All existing tenant-scoped tests pass with the updated path prefix.
- Public schema tests pass unchanged.

---

### Task 21.4 — Update environment variables and deployment config

The URL shape used in tokenized booking links, Stripe metadata, and deployment configuration changes.

Required changes:

**`backend/.env.example`** — update comments to reflect new URL shape:
```
# Tenant API base: api.tablesched.domenicocaruso.com/restaurants/<slug>
PUBLIC_BOOKING_BASE_URL=https://tablesched.domenicocaruso.com
```

**Stripe metadata** — `tenant_schema` is already stored in `metadata` on every PaymentIntent and Checkout Session (see `apps/payments/gateways/stripe.py`). No change needed — the webhook resolves the tenant by schema name, not by domain.

**Tokenized booking links** — the `PUBLIC_BOOKING_BASE_URL` env var drives the URL included in customer SMS/email notifications. This points to the **frontend** URL, not the API. No change needed as long as the env var is set correctly.

**`Dockerfile` / deployment** — no structural changes. The single backend process serves all tenants via path prefix. Document in deployment notes that `ALLOWED_HOSTS` must include the single API domain (`api.tablesched.domenicocaruso.com`) rather than a wildcard.

Tests:
- `test_env.py` validates that `PUBLIC_BOOKING_BASE_URL` is set and does not contain a tenant slug.
- Stripe webhook integration test confirms tenant resolution works via `metadata.tenant_schema` without any domain header.

---

## Phase 21 (additional) — Supabase Keepalive

### Task 21.5 — GitHub Actions keepalive

Supabase free tier pauses the entire project after 7 days of inactivity. A scheduled GitHub Actions workflow pings `/healthz/` every 6 days to prevent this. No secrets required.

Create `.github/workflows/keepalive.yml`:

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

Free on public repositories and within the 2,000 free minutes/month limit for private repositories (each run uses ~1 second).
