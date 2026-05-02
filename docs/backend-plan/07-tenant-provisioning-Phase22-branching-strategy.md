# Branching Strategy — Phase 22: Tenant Provisioning Command

References:
- Implementation plan: [`07-tenant-provisioning-Phase22.md`](./07-tenant-provisioning-Phase22.md)
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
pytest backend/tests/tenants/test_provision_tenant.py

# 4. Full test suite — only if step 3 passes
pytest backend/
```

All checks must pass (0 errors, 0 failures) before merging.

---

## Branch Hierarchy

```
develop
└── feature/backend-mvp
    └── feature/backend-mvp-Phase22-tenant-provisioning
        ├── task/backend-mvp-Task22.1-provision-tenant-command
        ├── task/backend-mvp-Task22.2-tenant-directory-endpoint
        ├── task/backend-mvp-Task22.3-init-platform-command
        └── task/backend-mvp-Task22.4-allauth-headless-jwt
```

---

## ❌ Phase 22 — Tenant Provisioning Command

Single atomic command to onboard a new restaurant: schema, domain, user, and manager membership in one shot.

**Branch:** `feature/backend-mvp-Phase22-tenant-provisioning` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase22-tenant-provisioning
git push -u origin feature/backend-mvp-Phase22-tenant-provisioning
```

---

### ✅ Task 22.1 — provision_tenant command (amended by Task 22.4)

Create `provision_tenant` management command and its tests. The existing `create_tenant` command is unchanged.

**Branch:** `task/backend-mvp-Task22.1-provision-tenant-command` — created from `feature/backend-mvp-Phase22-tenant-provisioning`

```bash
git checkout feature/backend-mvp-Phase22-tenant-provisioning
git pull origin feature/backend-mvp-Phase22-tenant-provisioning
git checkout -b task/backend-mvp-Task22.1-provision-tenant-command
```

See [`07-tenant-provisioning-Phase22.md`](./07-tenant-provisioning-Phase22.md) for full code.

**i18n rule:** Command output is operator-facing only — no translation key required.

**Commit:**
```bash
git add apps/tenants/management/commands/provision_tenant.py tests/tenants/test_provision_tenant.py
git commit -m "[TASK] 22.1 add provision_tenant atomic onboarding command"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest backend/tests/tenants/test_provision_tenant.py
pytest backend/
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task22.1-provision-tenant-command
git checkout feature/backend-mvp-Phase22-tenant-provisioning
git merge task/backend-mvp-Task22.1-provision-tenant-command
git push origin feature/backend-mvp-Phase22-tenant-provisioning
```

---

### ✅ Task 22.2 — Tenant directory endpoint

Public unauthenticated `GET /api/tenants/` endpoint returning active tenants with their API prefix. Registered on the public schema urlconf.

**Branch:** `task/backend-mvp-Task22.2-tenant-directory-endpoint` — created from `feature/backend-mvp-Phase22-tenant-provisioning`

```bash
git checkout feature/backend-mvp-Phase22-tenant-provisioning
git pull origin feature/backend-mvp-Phase22-tenant-provisioning
git checkout -b task/backend-mvp-Task22.2-tenant-directory-endpoint
```

See [`07-tenant-provisioning-Phase22.md`](./07-tenant-provisioning-Phase22.md) for full code.

**i18n rule:** Response contains only data fields — no user-facing strings.

**Commit:**
```bash
git add apps/tenants/views.py apps/tenants/urls.py config/urls_public.py tests/tenants/test_tenant_directory.py
git commit -m "[TASK] 22.2 add public tenant directory endpoint"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest backend/tests/tenants/test_tenant_directory.py
pytest backend/
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task22.2-tenant-directory-endpoint
git checkout feature/backend-mvp-Phase22-tenant-provisioning
git merge task/backend-mvp-Task22.2-tenant-directory-endpoint
git push origin feature/backend-mvp-Phase22-tenant-provisioning
```

---

### ❌ Task 22.3 — init_platform command

One-time idempotent setup command: runs shared migrations and creates the public tenant row required by `TenantSubfolderMiddleware`.

**Branch:** `task/backend-mvp-Task22.3-init-platform-command` — created from `feature/backend-mvp-Phase22-tenant-provisioning`

```bash
git checkout feature/backend-mvp-Phase22-tenant-provisioning
git pull origin feature/backend-mvp-Phase22-tenant-provisioning
git checkout -b task/backend-mvp-Task22.3-init-platform-command
```

See [`07-tenant-provisioning-Phase22.md`](./07-tenant-provisioning-Phase22.md) for full code.

**i18n rule:** Command output is operator-facing only — no translation key required.

**Commit:**
```bash
git add apps/tenants/management/commands/init_platform.py tests/tenants/test_init_platform.py
git commit -m "[TASK] 22.3 add init_platform one-time setup command"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest backend/tests/tenants/test_init_platform.py
pytest backend/
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task22.3-init-platform-command
git checkout feature/backend-mvp-Phase22-tenant-provisioning
git merge task/backend-mvp-Task22.3-init-platform-command
git push origin feature/backend-mvp-Phase22-tenant-provisioning
```

---

### ❌ Task 22.4 — Allauth headless JWT auth

Switch allauth to headless mode with JWT token strategy so the frontend (different domain) can authenticate without session cookies. Also fixes `provision_tenant` to create a verified `EmailAddress` row — without it, allauth returns 403 and sends a verification email on every login attempt.

**Amendment to Task 22.1:** `provision_tenant` must also create `EmailAddress(verified=True)` for operator-provisioned accounts. The same pattern applies to future manager-invited staff accounts.

**Branch:** `task/backend-mvp-Task22.4-allauth-headless-jwt` — created from `feature/backend-mvp-Phase22-tenant-provisioning`

```bash
git checkout feature/backend-mvp-Phase22-tenant-provisioning
git pull origin feature/backend-mvp-Phase22-tenant-provisioning
git checkout -b task/backend-mvp-Task22.4-allauth-headless-jwt
```

See [`07-tenant-provisioning-Phase22.md`](./07-tenant-provisioning-Phase22.md) for full code.

**Commit:**
```bash
git add config/settings/base.py apps/tenants/management/commands/provision_tenant.py tests/accounts/test_headless_auth.py
git commit -m "[TASK] 22.4 enable allauth headless JWT; fix provision_tenant email verification"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest backend/tests/accounts/test_headless_auth.py
pytest backend/tests/tenants/test_provision_tenant.py
pytest backend/
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task22.4-allauth-headless-jwt
git checkout feature/backend-mvp-Phase22-tenant-provisioning
git merge task/backend-mvp-Task22.4-allauth-headless-jwt
git push origin feature/backend-mvp-Phase22-tenant-provisioning
```

---

### ❌ Phase 22 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase22-tenant-provisioning
git push origin feature/backend-mvp
```
