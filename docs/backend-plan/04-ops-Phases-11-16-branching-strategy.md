# Branching Strategy — Phases 11–16: Ops

References:
- Implementation plan: [`04-ops-Phases-11-16.md`](./04-ops-Phases-11-16.md)
- Branching rules: [`BRANCHING_STRATEGY.md`](../../BRANCHING_STRATEGY.md)

---

## Global Rules

- **No hardcoded user-facing strings.** All text shown to the user must use i18n translation keys. The API returns only `error_code`, `reason_code`, and `status` strings — never localized text.
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
    ├── feature/backend-mvp-Phase11-opportunistic-maintenance         ← created from feature/backend-mvp AFTER Phase 10 merged
    │   ├── task/backend-mvp-Task11.1-opportunistic-maintenance-service
    │   └── task/backend-mvp-Task11.2-dashboard-endpoint
    ├── feature/backend-mvp-Phase12-audit           ← created from feature/backend-mvp AFTER Phase 11 merged
    │   ├── task/backend-mvp-Task12.1-audit-model
    │   └── task/backend-mvp-Task12.2-audit-service
    ├── feature/backend-mvp-Phase13-security        ← created from feature/backend-mvp AFTER Phase 12 merged
    │   ├── task/backend-mvp-Task13.1-tenant-isolation-tests
    │   ├── task/backend-mvp-Task13.2-webhook-regression
    │   ├── task/backend-mvp-Task13.3-credential-hardening
    │   ├── task/backend-mvp-Task13.4-token-hardening
    │   └── task/backend-mvp-Task13.5-rate-limiting
    ├── feature/backend-mvp-Phase14-tests           ← created from feature/backend-mvp AFTER Phase 13 merged
    │   ├── task/backend-mvp-Task14.1-layered-tests
    │   └── task/backend-mvp-Task14.2-test-tooling
    ├── feature/backend-mvp-Phase15-observability   ← created from feature/backend-mvp AFTER Phase 14 merged
    │   └── task/backend-mvp-Task15.1-logging-healthz
    └── feature/backend-mvp-Phase16-deploy          ← created from feature/backend-mvp AFTER Phase 15 merged
        ├── task/backend-mvp-Task16.1-dockerfile
        ├── task/backend-mvp-Task16.2-env-vars
        └── task/backend-mvp-Task16.3-domain-subdomains
```

---

## ❌ Phase 11 — Opportunistic Maintenance

No Celery/Redis. Opportunistic maintenance runs lazily on each admin dashboard load. Each opportunistic maintenance is bounded (`[:200]`) and idempotent. Handles: expired pending payments, expired pre-authorizations (→ `authorization_expired`), and payment reconciliation.

**⚠️ Create this branch only after Phase 10 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase11-opportunistic-maintenance` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase11-opportunistic-maintenance
git push -u origin feature/backend-mvp-Phase11-opportunistic-maintenance
```

---

### ❌ Task 11.1 — Opportunistic Maintenance Service

Expires `pending_payment` bookings past their `payment_due_at`. Transitions pre-authorized payments older than 6 days to `authorization_expired` (Stripe auth expires ~7 days). Notifies staff on authorization expiry — does NOT auto-cancel the booking.

**Branch:** `task/backend-mvp-Task11.1-opportunistic-maintenance-service` — created from `feature/backend-mvp-Phase11-opportunistic-maintenance`

```bash
git checkout feature/backend-mvp-Phase11-opportunistic-maintenance
git pull origin feature/backend-mvp-Phase11-opportunistic-maintenance
git checkout -b task/backend-mvp-Task11.1-opportunistic-maintenance-service
```

**`apps/bookings/services/opportunistic_maintenance.py`:**

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
    qs = Booking.objects.filter(
        status=BookingStatus.PENDING_PAYMENT,
        payment_due_at__lt=now(),
    )[:200]
    for b in qs:
        transition(b, BookingStatus.EXPIRED)
        b.save()
        notifications.notify_customer(b, "booking_expired")

def _expire_authorized_deposits():
    # Do NOT auto-cancel the booking. Staff must decide: confirm without deposit /
    # request payment again / decline. The booking transitions to authorization_expired
    # so staff can see it needs attention.
    qs = (
        Payment.objects
        .filter(
            status=PaymentStatus.AUTHORIZED,
            booking__status=BookingStatus.PENDING_REVIEW,
            created_at__lt=now() - timedelta(days=6),
        )
        .select_related("booking")[:200]
    )
    for p in qs:
        p.status = PaymentStatus.FAILED
        p.save()
        b = p.booking
        transition(b, BookingStatus.AUTHORIZATION_EXPIRED)
        b.save()
        notifications.notify_staff(b, "authorization_expired_staff")

def _reconcile_payments():
    # Best-effort: query Stripe for payments stuck PENDING beyond a threshold.
    # Implementation queries Stripe for latest status and updates Payment.status.
    pass
```

**Tests:**

```python
# tests/bookings/test_opportunistic_maintenance.py

def test_expire_pending_payment_past_due(tenant_db, pending_payment_booking):
    from apps.bookings.services.opportunistic_maintenance import _expire_pending_payments
    from apps.bookings.models import BookingStatus
    _expire_pending_payments()
    pending_payment_booking.refresh_from_db()
    assert pending_payment_booking.status == BookingStatus.EXPIRED

def test_expire_pending_payment_not_yet_due(tenant_db, pending_payment_booking_future):
    from apps.bookings.services.opportunistic_maintenance import _expire_pending_payments
    from apps.bookings.models import BookingStatus
    _expire_pending_payments()
    pending_payment_booking_future.refresh_from_db()
    assert pending_payment_booking_future.status == BookingStatus.PENDING_PAYMENT

def test_expire_authorized_deposit_old(tenant_db, old_authorized_payment):
    from apps.bookings.services.opportunistic_maintenance import _expire_authorized_deposits
    from apps.bookings.models import BookingStatus
    from apps.payments.models import PaymentStatus
    _expire_authorized_deposits()
    old_authorized_payment.booking.refresh_from_db()
    old_authorized_payment.refresh_from_db()
    assert old_authorized_payment.booking.status == BookingStatus.AUTHORIZATION_EXPIRED
    assert old_authorized_payment.status == PaymentStatus.FAILED

def test_opportunistic_maintenance_is_idempotent(tenant_db, pending_payment_booking):
    from apps.bookings.services.opportunistic_maintenance import _expire_pending_payments
    _expire_pending_payments()
    _expire_pending_payments()  # second call must not error or double-process
    pending_payment_booking.refresh_from_db()
    assert pending_payment_booking.status == "expired"

def test_opportunistic_maintenance_bounded_at_200(tenant_db, many_expired_bookings):
    """Opportunistic maintenance must process at most 200 items per run."""
    from apps.bookings.services.opportunistic_maintenance import _expire_pending_payments
    from apps.bookings.models import Booking, BookingStatus
    _expire_pending_payments()
    expired_count = Booking.objects.filter(status=BookingStatus.EXPIRED).count()
    assert expired_count <= 200
```

**Commit:**
```bash
git add apps/bookings/services/opportunistic_maintenance.py
git commit -m "[TASK] 11.1 add dashboard opportunistic maintenance service"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/bookings/test_opportunistic_maintenance.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task11.1-opportunistic-maintenance-service
git checkout feature/backend-mvp-Phase11-opportunistic_maintenance
git merge task/backend-mvp-Task11.1-opportunistic-maintenance-service
git push origin feature/backend-mvp-Phase11-opportunistic-maintenance
```

---

### ❌ Task 11.2 — Dashboard Endpoint

Runs opportunistic maintenance then returns counts by status and the 50 most recent bookings. Manager + staff allowed. Response is code-form only — no localized strings.

**Branch:** `task/backend-mvp-Task11.2-dashboard-endpoint` — created from `feature/backend-mvp-Phase11-opportunistic-maintenance`

```bash
git checkout feature/backend-mvp-Phase11-opportunistic-maintenance
git pull origin feature/backend-mvp-Phase11-opportunistic-maintenance
git checkout -b task/backend-mvp-Task11.2-dashboard-endpoint
```

**`apps/bookings/views.py` (dashboard):**

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.common.permissions import IsTenantMember
from apps.bookings.models import Booking
from apps.bookings.services import OpportunisticMaintenance

class AdminDashboardView(APIView):
    permission_classes = [IsTenantMember]

    def get(self, request):
        opportunisticMaintenance.run_opportunistic_maintenance()
        data = {
            "counts_by_status": _counts_by_status(),
            "recent": list(
                Booking.objects.order_by("-created_at")[:50]
                .values("id", "status", "starts_at", "party_size")
            ),
        }
        return Response(data)

def _counts_by_status():
    from django.db.models import Count
    return {
        row["status"]: row["count"]
        for row in Booking.objects.values("status").annotate(count=Count("id"))
    }
```

**Tests:**

```python
# tests/bookings/test_dashboard.py

def test_dashboard_requires_auth(client, tenant):
    response = client.get("/api/v1/admin/dashboard/", HTTP_HOST=tenant.domain)
    assert response.status_code == 403

def test_dashboard_returns_counts_and_recent(staff_client, tenant, bookings):
    response = staff_client.get("/api/v1/admin/dashboard/", HTTP_HOST=tenant.domain)
    assert response.status_code == 200
    assert "counts_by_status" in response.data
    assert "recent" in response.data

def test_dashboard_triggers_opportunistic_maintenance(staff_client, tenant, expired_booking, mock_opportunistic_maintenance):
    staff_client.get("/api/v1/admin/dashboard/", HTTP_HOST=tenant.domain)
    assert mock_opportunistic_maintenance.run_opportunistic_maintenance.called
```

**Commit:**
```bash
git add apps/bookings/views.py apps/bookings/urls.py
git commit -m "[TASK] 11.2 add admin dashboard endpoint with opportunistic maintenance trigger"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/bookings/test_dashboard.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task11.2-dashboard-endpoint
git checkout feature/backend-mvp-Phase11-opportunistic-maintenance
git merge task/backend-mvp-Task11.2-dashboard-endpoint
git push origin feature/backend-mvp-Phase11-opportunistic-maintenance
```

---

### ❌ Phase 11 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase11-opportunistic-maintenance
git push origin feature/backend-mvp
```

---

## ❌ Phase 12 — Audit Log

Explicit audit trail for booking, payment, and refund actions. Written directly by service layer — no automatic signals.

**⚠️ Create this branch only after Phase 11 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase12-audit` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase12-audit
git push -u origin feature/backend-mvp-Phase12-audit
```

---

### ✅ Task 12.1 — AuditLog Model

**Branch:** `task/backend-mvp-Task12.1-audit-model` — created from `feature/backend-mvp-Phase12-audit`

```bash
git checkout feature/backend-mvp-Phase12-audit
git pull origin feature/backend-mvp-Phase12-audit
git checkout -b task/backend-mvp-Task12.1-audit-model
```

**`apps/audit/models.py`:**

```python
from django.db import models
from apps.common.models import TimeStampedModel

class AuditLog(TimeStampedModel):
    actor = models.ForeignKey("memberships.StaffMembership", null=True,
                              on_delete=models.SET_NULL)
    action = models.CharField(max_length=64)         # e.g. booking.approve
    target_type = models.CharField(max_length=64)
    target_id = models.UUIDField()
    payload = models.JSONField(default=dict)
```

**Tests:**

```python
# tests/audit/test_models.py

def test_audit_log_fields(tenant_db, membership, booking):
    from apps.audit.models import AuditLog
    log = AuditLog.objects.create(
        actor=membership, action="booking.approve",
        target_type="Booking", target_id=booking.id,
        payload={"to_status": "confirmed"},
    )
    assert log.action == "booking.approve"
    assert log.payload["to_status"] == "confirmed"
```

**Commit:**
```bash
git add apps/audit/models.py
git commit -m "[TASK] 12.1 add AuditLog model"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/audit/test_models.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task12.1-audit-model
git checkout feature/backend-mvp-Phase12-audit
git merge task/backend-mvp-Task12.1-audit-model
git push origin feature/backend-mvp-Phase12-audit
```

---

### ✅ Task 12.2 — Audit Record Service

Single write helper called explicitly by booking, payment, and refund services.

**Branch:** `task/backend-mvp-Task12.2-audit-service` — created from `feature/backend-mvp-Phase12-audit`

```bash
git checkout feature/backend-mvp-Phase12-audit
git pull origin feature/backend-mvp-Phase12-audit
git checkout -b task/backend-mvp-Task12.2-audit-service
```

**`apps/audit/services.py`:**

```python
from apps.audit.models import AuditLog

def record(*, actor, action, target, payload=None):
    AuditLog.objects.create(
        actor=actor, action=action,
        target_type=target.__class__.__name__,
        target_id=target.id, payload=payload or {},
    )
```

**Tests:**

```python
# tests/audit/test_services.py

def test_record_creates_audit_log(tenant_db, membership, booking):
    from apps.audit.services import record
    from apps.audit.models import AuditLog
    record(actor=membership, action="booking.decline", target=booking,
           payload={"reason_code": "staff_rejection_generic"})
    log = AuditLog.objects.get(action="booking.decline")
    assert log.target_id == booking.id
    assert log.payload["reason_code"] == "staff_rejection_generic"

def test_record_with_no_payload(tenant_db, membership, booking):
    from apps.audit.services import record
    from apps.audit.models import AuditLog
    record(actor=membership, action="booking.approve", target=booking)
    log = AuditLog.objects.get(action="booking.approve")
    assert log.payload == {}
```

**Commit:**
```bash
git add apps/audit/services.py
git commit -m "[TASK] 12.2 add audit record service"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/audit/test_services.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task12.2-audit-service
git checkout feature/backend-mvp-Phase12-audit
git merge task/backend-mvp-Task12.2-audit-service
git push origin feature/backend-mvp-Phase12-audit
```

---

### ❌ Phase 12 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase12-audit
git push origin feature/backend-mvp
```

---

## ❌ Phase 13 — Security Hardening

Tenant isolation tests, Stripe signature regression, credential handling, token endpoint hardening, and rate limiting.

**⚠️ Create this branch only after Phase 12 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase13-security` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase13-security
git push -u origin feature/backend-mvp-Phase13-security
```

---

### ❌ Task 13.1 — Tenant Isolation Tests

Create two tenants. Assert that no endpoint or webhook handler leaks data across schemas.

**Branch:** `task/backend-mvp-Task13.1-tenant-isolation-tests` — created from `feature/backend-mvp-Phase13-security`

```bash
git checkout feature/backend-mvp-Phase13-security
git pull origin feature/backend-mvp-Phase13-security
git checkout -b task/backend-mvp-Task13.1-tenant-isolation-tests
```

**Tests:**

```python
# tests/security/test_tenant_isolation.py

def test_staff_cannot_read_other_tenant_bookings(tenant_a_client, tenant_b, tenant_a):
    """Staff of tenant A must get 0 results when querying against tenant B's domain."""
    response = tenant_a_client.get("/api/v1/bookings/", HTTP_HOST=tenant_b.domain)
    # Either forbidden or empty — never returns tenant A's bookings
    assert response.status_code in (403, 200)
    if response.status_code == 200:
        assert response.data["results"] == []

def test_webhook_cannot_affect_wrong_tenant(client, tenant_a, tenant_b,
                                            tenant_b_payment, stripe_event_for_tenant_b):
    """Webhook event for tenant B must not affect tenant A's Payment records."""
    from apps.payments.models import Payment
    client.post("/stripe/webhook/", data=stripe_event_for_tenant_b,
                HTTP_STRIPE_SIGNATURE=compute_sig(stripe_event_for_tenant_b),
                content_type="application/json")
    # No Payment in tenant A should have changed
    with schema_context(tenant_a.schema_name):
        assert not Payment.objects.exists()

def test_token_from_tenant_a_invalid_on_tenant_b(client, tenant_a, tenant_b,
                                                   booking_a, raw_token_a):
    """Booking access token from tenant A must not work on tenant B's domain."""
    response = client.get(f"/api/v1/public/bookings/{raw_token_a}/",
                          HTTP_HOST=tenant_b.domain)
    assert response.status_code in (404, 410)
```

**Commit:**
```bash
git add tests/security/test_tenant_isolation.py
git commit -m "[TEST] 13.1 add tenant isolation security tests"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/security/test_tenant_isolation.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task13.1-tenant-isolation-tests
git checkout feature/backend-mvp-Phase13-security
git merge task/backend-mvp-Task13.1-tenant-isolation-tests
git push origin feature/backend-mvp-Phase13-security
```

---

### ❌ Task 13.2 — Stripe Webhook Signature Regression Test

**Branch:** `task/backend-mvp-Task13.2-webhook-regression` — created from `feature/backend-mvp-Phase13-security`

```bash
git checkout feature/backend-mvp-Phase13-security
git pull origin feature/backend-mvp-Phase13-security
git checkout -b task/backend-mvp-Task13.2-webhook-regression
```

**Tests:**

```python
# tests/security/test_webhook_signature.py

def test_unsigned_payload_returns_400(client):
    response = client.post("/stripe/webhook/", data=b'{"type":"test"}',
                           content_type="application/json")
    assert response.status_code == 400

def test_wrong_signature_returns_400(client):
    response = client.post("/stripe/webhook/", data=b'{"type":"test"}',
                           HTTP_STRIPE_SIGNATURE="t=123,v1=bad",
                           content_type="application/json")
    assert response.status_code == 400

def test_valid_signature_passes_verification(client, valid_stripe_event, valid_sig):
    response = client.post("/stripe/webhook/", data=valid_stripe_event,
                           HTTP_STRIPE_SIGNATURE=valid_sig,
                           content_type="application/json")
    assert response.status_code != 400
```

**Commit:**
```bash
git add tests/security/test_webhook_signature.py
git commit -m "[TEST] 13.2 add Stripe signature verification regression tests"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/security/test_webhook_signature.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task13.2-webhook-regression
git checkout feature/backend-mvp-Phase13-security
git merge task/backend-mvp-Task13.2-webhook-regression
git push origin feature/backend-mvp-Phase13-security
```

---

### ❌ Task 13.3 — Credential Hardening (Twilio + SMTP)

Credentials loaded from env only. Never echoed in API responses. Redacted from logs via a log filter.

**Branch:** `task/backend-mvp-Task13.3-credential-hardening` — created from `feature/backend-mvp-Phase13-security`

```bash
git checkout feature/backend-mvp-Phase13-security
git pull origin feature/backend-mvp-Phase13-security
git checkout -b task/backend-mvp-Task13.3-credential-hardening
```

**`apps/common/log_filters.py`:**

```python
import logging

REDACTED = "[REDACTED]"
SENSITIVE_KEYS = {"password", "token", "secret", "auth", "sid", "key"}

class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.msg, str):
            for key in SENSITIVE_KEYS:
                record.msg = record.msg.replace(key, REDACTED)
        return True
```

Register in `LOGGING` config under all handler filters.

**Tests:**

```python
# tests/security/test_credentials.py

def test_twilio_credentials_not_in_api_response(staff_client, tenant):
    import os
    response = staff_client.get("/api/v1/admin/dashboard/", HTTP_HOST=tenant.domain)
    body = str(response.data)
    assert os.environ.get("TWILIO_AUTH_TOKEN", "DUMMY") not in body

def test_log_filter_redacts_sensitive_keys():
    from apps.common.log_filters import SensitiveDataFilter
    import logging
    record = logging.LogRecord("test", logging.INFO, "", 0,
                               "auth_token=abc123 message", (), None)
    SensitiveDataFilter().filter(record)
    assert "abc123" not in record.msg
```

**Commit:**
```bash
git add apps/common/log_filters.py config/settings/base.py
git commit -m "[TASK] 13.3 add credential redaction log filter"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/security/test_credentials.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task13.3-credential-hardening
git checkout feature/backend-mvp-Phase13-security
git merge task/backend-mvp-Task13.3-credential-hardening
git push origin feature/backend-mvp-Phase13-security
```

---

### ❌ Task 13.4 — Token Endpoint Hardening

Constant-time hash comparison. Raw token never logged. Rate limited.

**Branch:** `task/backend-mvp-Task13.4-token-hardening` — created from `feature/backend-mvp-Phase13-security`

```bash
git checkout feature/backend-mvp-Phase13-security
git pull origin feature/backend-mvp-Phase13-security
git checkout -b task/backend-mvp-Task13.4-token-hardening
```

**`apps/customers/models.py` — constant-time verify:**

```python
import hmac

def verify_token(raw: str, stored_hash: str) -> bool:
    return hmac.compare_digest(hash_token(raw), stored_hash)
```

Replace direct `token_hash=h` DB lookup with `verify_token` after fetching by hash (already constant-time since SHA-256 comparison is fixed-length). Ensure raw token is never written to any log.

**Tests:**

```python
# tests/security/test_token_hardening.py

def test_verify_token_correct(tenant_db, booking):
    from apps.customers.models import BookingAccessToken, verify_token
    tok, raw = BookingAccessToken.issue(booking)
    assert verify_token(raw, tok.token_hash) is True

def test_verify_token_wrong(tenant_db, booking):
    from apps.customers.models import BookingAccessToken, verify_token
    tok, _ = BookingAccessToken.issue(booking)
    assert verify_token("wrongtoken", tok.token_hash) is False

def test_raw_token_not_in_audit_log(tenant_db, booking, raw_token, staff_client, tenant):
    from apps.audit.models import AuditLog
    # Trigger a booking action; raw token must not appear in any audit log payload
    staff_client.post(f"/api/v1/bookings/{booking.id}/approve/", HTTP_HOST=tenant.domain)
    for log in AuditLog.objects.all():
        assert raw_token not in str(log.payload)
```

**Commit:**
```bash
git add apps/customers/models.py
git commit -m "[TASK] 13.4 add constant-time token verification and hardening"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/security/test_token_hardening.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task13.4-token-hardening
git checkout feature/backend-mvp-Phase13-security
git merge task/backend-mvp-Task13.4-token-hardening
git push origin feature/backend-mvp-Phase13-security
```

---

### ❌ Task 13.5 — Rate Limiting (Public Endpoints)

`AnonRateThrottle` on public booking-request and token endpoints. Uses local-memory cache (no Redis, per technical doc §8).

**Branch:** `task/backend-mvp-Task13.5-rate-limiting` — created from `feature/backend-mvp-Phase13-security`

```bash
git checkout feature/backend-mvp-Phase13-security
git pull origin feature/backend-mvp-Phase13-security
git checkout -b task/backend-mvp-Task13.5-rate-limiting
```

**`config/settings/base.py` additions:**

```python
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "30/min"},
    "EXCEPTION_HANDLER": "apps.common.exception_handler.custom_exception_handler",
}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache"
    }
}
```

**Tests:**

```python
# tests/security/test_rate_limiting.py

def test_public_booking_endpoint_throttled(client, tenant):
    for _ in range(31):
        response = client.post("/api/v1/public/bookings/",
                               content_type="application/json",
                               HTTP_HOST=tenant.domain)
    assert response.status_code == 429
```

**Commit:**
```bash
git add config/settings/base.py
git commit -m "[TASK] 13.5 add rate limiting on public endpoints"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/security/test_rate_limiting.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task13.5-rate-limiting
git checkout feature/backend-mvp-Phase13-security
git merge task/backend-mvp-Task13.5-rate-limiting
git push origin feature/backend-mvp-Phase13-security
```

---

### ❌ Phase 13 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase13-security
git push origin feature/backend-mvp
```

---

## ❌ Phase 14 — Testing Strategy

Consolidates the full layered test suite: unit, API, webhook, tenant isolation, token flow, and localization coverage. Targets ≥85% coverage on core apps.

**⚠️ Create this branch only after Phase 13 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase14-tests` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase14-tests
git push -u origin feature/backend-mvp-Phase14-tests
```

---

### ❌ Task 14.1 — Layered Test Suite

Adds missing coverage tests not already written per-task:
- API happy paths + code-form error response verification
- Stripe webhook event fixtures (all handler events)
- Full token flow: issue → use → expire → reject
- Cross-locale template rendering

**Branch:** `task/backend-mvp-Task14.1-layered-tests` — created from `feature/backend-mvp-Phase14-tests`

```bash
git checkout feature/backend-mvp-Phase14-tests
git pull origin feature/backend-mvp-Phase14-tests
git checkout -b task/backend-mvp-Task14.1-layered-tests
```

**Coverage targets:**

| App | Minimum Coverage |
|---|---|
| `apps/bookings` | 85% |
| `apps/payments` | 85% |
| `apps/notifications` | 85% |
| `apps/customers` | 85% |

Run coverage report:
```bash
pytest --cov=apps/bookings --cov=apps/payments --cov=apps/notifications --cov=apps/customers --cov-report=term-missing
```

**Commit:**
```bash
git add tests/
git commit -m "[TEST] 14.1 add full layered test suite"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task14.1-layered-tests
git checkout feature/backend-mvp-Phase14-tests
git merge task/backend-mvp-Task14.1-layered-tests
git push origin feature/backend-mvp-Phase14-tests
```

---

### ❌ Task 14.2 — Test Tooling & Fixtures

Shared `conftest.py` fixtures: `tenant_db`, `staff_client`, `manager_client`, `booking`, `customer`, `payment`, etc. Ensures no test duplicates fixture setup.

**Branch:** `task/backend-mvp-Task14.2-test-tooling` — created from `feature/backend-mvp-Phase14-tests`

```bash
git checkout feature/backend-mvp-Phase14-tests
git pull origin feature/backend-mvp-Phase14-tests
git checkout -b task/backend-mvp-Task14.2-test-tooling
```

**`tests/conftest.py` (key fixtures):**

```python
import pytest
from django_tenants.test.client import TenantClient

@pytest.fixture
def tenant(db):
    from apps.tenants.models import Restaurant, Domain
    r = Restaurant.objects.create(schema_name="test", name="Test Restaurant")
    Domain.objects.create(domain="test.localhost", tenant=r, is_primary=True)
    return r

@pytest.fixture
def staff_client(tenant, staff_user):
    client = TenantClient(tenant)
    client.force_login(staff_user)
    return client

@pytest.fixture
def manager_client(tenant, manager_user):
    client = TenantClient(tenant)
    client.force_login(manager_user)
    return client
```

`factory_boy` factories for `User`, `StaffMembership`, `Customer`, `Booking`, `Payment`.

**Commit:**
```bash
git add tests/conftest.py tests/factories.py
git commit -m "[TEST] 14.2 add shared conftest fixtures and factories"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task14.2-test-tooling
git checkout feature/backend-mvp-Phase14-tests
git merge task/backend-mvp-Task14.2-test-tooling
git push origin feature/backend-mvp-Phase14-tests
```

---

### ❌ Phase 14 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase14-tests
git push origin feature/backend-mvp
```

---

## ❌ Phase 15 — Observability

Structured JSON logging per logger, `/healthz` endpoint. No APM dependency in MVP.

**⚠️ Create this branch only after Phase 14 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase15-observability` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase15-observability
git push -u origin feature/backend-mvp-Phase15-observability
```

---

### ❌ Task 15.1 — Structured Logging & Health Endpoint

**Branch:** `task/backend-mvp-Task15.1-logging-healthz` — created from `feature/backend-mvp-Phase15-observability`

```bash
git checkout feature/backend-mvp-Phase15-observability
git pull origin feature/backend-mvp-Phase15-observability
git checkout -b task/backend-mvp-Task15.1-logging-healthz
```

**`config/settings/base.py` logging config:**

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
        "bookings":           {"handlers": ["stdout"], "level": "INFO", "propagate": False},
        "payments.webhook":   {"handlers": ["stdout"], "level": "INFO", "propagate": False},
        "notifications":      {"handlers": ["stdout"], "level": "INFO", "propagate": False},
        "audit":              {"handlers": ["stdout"], "level": "INFO", "propagate": False},
    },
}
```

Add `python-json-logger` to `pyproject.toml` dependencies.

**`config/urls_public.py` — healthz:**

```python
from django.http import HttpResponse

def healthz(request):
    return HttpResponse("ok")
```

**Tests:**

```python
# tests/test_observability.py

def test_healthz_returns_200(client):
    response = client.get("/healthz/")
    assert response.status_code == 200
    assert response.content == b"ok"
```

**Commit:**
```bash
git add config/settings/base.py config/urls_public.py
git commit -m "[TASK] 15.1 add structured JSON logging and healthz endpoint"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/test_observability.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task15.1-logging-healthz
git checkout feature/backend-mvp-Phase15-observability
git merge task/backend-mvp-Task15.1-logging-healthz
git push origin feature/backend-mvp-Phase15-observability
```

---

### ❌ Phase 15 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase15-observability
git push origin feature/backend-mvp
```

---

## ❌ Phase 16 — Deployment Prep (Hugging Face + managed Postgres)

**⚠️ Create this branch only after Phase 15 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase16-deploy` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase16-deploy
git push -u origin feature/backend-mvp-Phase16-deploy
```

---

### ❌ Task 16.1 — Dockerfile

Single container, no Redis, no worker. Migrations run on startup before gunicorn.

**Branch:** `task/backend-mvp-Task16.1-dockerfile` — created from `feature/backend-mvp-Phase16-deploy`

```bash
git checkout feature/backend-mvp-Phase16-deploy
git pull origin feature/backend-mvp-Phase16-deploy
git checkout -b task/backend-mvp-Task16.1-dockerfile
```

**`Dockerfile`:**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install --no-cache-dir .
COPY . .
CMD ["sh", "-lc", "python manage.py migrate_schemas --shared && python manage.py migrate_schemas && gunicorn config.wsgi --bind 0.0.0.0:$PORT"]
```

**Tests:** None — infrastructure only. Validate via `docker build` locally.

**Commit:**
```bash
git add Dockerfile .dockerignore
git commit -m "[TASK] 16.1 add Dockerfile for HuggingFace deployment"
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task16.1-dockerfile
git checkout feature/backend-mvp-Phase16-deploy
git merge task/backend-mvp-Task16.1-dockerfile
git push origin feature/backend-mvp-Phase16-deploy
```

---

### ❌ Task 16.2 — Environment Variables

Document and validate all required env vars. No secrets in source.

**Branch:** `task/backend-mvp-Task16.2-env-vars` — created from `feature/backend-mvp-Phase16-deploy`

```bash
git checkout feature/backend-mvp-Phase16-deploy
git pull origin feature/backend-mvp-Phase16-deploy
git checkout -b task/backend-mvp-Task16.2-env-vars
```

**Required env vars (`.env.example`):**

```bash
DJANGO_SECRET_KEY=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432
STRIPE_API_KEY=
STRIPE_WEBHOOK_SECRET=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM=
EMAIL_HOST=
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=
ALLOWED_HOSTS=
PUBLIC_DOMAIN=
PUBLIC_BOOKING_RETURN_URL=
PUBLIC_BOOKING_CANCEL_URL=
PUBLIC_BOOKING_BASE_URL=
```

**Tests:**

```python
# tests/test_env.py

def test_required_env_vars_present():
    import os
    required = [
        "DJANGO_SECRET_KEY", "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST",
        "STRIPE_API_KEY", "STRIPE_WEBHOOK_SECRET",
        "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_FROM",
        "EMAIL_HOST", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD",
        "DEFAULT_FROM_EMAIL", "ALLOWED_HOSTS",
    ]
    missing = [v for v in required if not os.environ.get(v)]
    assert not missing, f"Missing env vars: {missing}"
```

**Commit:**
```bash
git add .env.example
git commit -m "[TASK] 16.2 document required environment variables"
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task16.2-env-vars
git checkout feature/backend-mvp-Phase16-deploy
git merge task/backend-mvp-Task16.2-env-vars
git push origin feature/backend-mvp-Phase16-deploy
```

---

### ❌ Task 16.3 — Domain & Subdomains

Configure `ALLOWED_HOSTS` and tenant domain mapping. Verify wildcard subdomain support on Hugging Face. If unsupported, flag to switch host before deploying.

**Branch:** `task/backend-mvp-Task16.3-domain-subdomains` — created from `feature/backend-mvp-Phase16-deploy`

```bash
git checkout feature/backend-mvp-Phase16-deploy
git pull origin feature/backend-mvp-Phase16-deploy
git checkout -b task/backend-mvp-Task16.3-domain-subdomains
```

**Domain plan (technical doc §13):**
- Web app: `tablesched.domenicocaruso.com`
- API: `api.tablesched.domenicocaruso.com`
- Tenant APIs: `api.<tenant>.tablesched.domenicocaruso.com` → mapped to `Domain` rows

**`config/settings/prod.py`:**

```python
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
# e.g. ALLOWED_HOSTS=".tablesched.domenicocaruso.com,api.tablesched.domenicocaruso.com"
```

**⚠️ Note:** If Hugging Face does not support wildcard subdomains, switch backend host before proceeding. Do not work around this.

**Tests:** None — infrastructure validation. Verify via DNS and `curl`.

**Commit:**
```bash
git add config/settings/prod.py
git commit -m "[TASK] 16.3 configure domain and subdomain routing for production"
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task16.3-domain-subdomains
git checkout feature/backend-mvp-Phase16-deploy
git merge task/backend-mvp-Task16.3-domain-subdomains
git push origin feature/backend-mvp-Phase16-deploy
```

---

### ❌ Phase 16 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase16-deploy
git push origin feature/backend-mvp
```

---

### ❌ Feature complete — merge into develop

```bash
# Requires explicit confirmation before merging.
git checkout develop
git merge feature/backend-mvp
git push origin develop
```
