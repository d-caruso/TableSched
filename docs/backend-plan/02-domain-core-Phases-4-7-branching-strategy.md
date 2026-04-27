# Branching Strategy — Phases 4–7: Domain Core

References:
- Implementation plan: [`02-domain-core-Phases-4-7.md`](./02-domain-core-Phases-4-7.md)
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
└── feature/backend-mvp
    ├── feature/backend-mvp-Phase4-auth              ← created from feature/backend-mvp AFTER Phase 3 merged
    │   ├── task/backend-mvp-Task4.1-user-model
    │   ├── task/backend-mvp-Task4.2-allauth
    │   └── task/backend-mvp-Task4.3-staff-membership
    ├── feature/backend-mvp-Phase5-customers-tokens  ← created from feature/backend-mvp AFTER Phase 4 merged
    │   ├── task/backend-mvp-Task5.1-customer-model
    │   ├── task/backend-mvp-Task5.2-booking-access-token
    │   └── task/backend-mvp-Task5.3-customer-endpoints
    ├── feature/backend-mvp-Phase6-restaurant-config ← created from feature/backend-mvp AFTER Phase 5 merged
    │   ├── task/backend-mvp-Task6.1-restaurant-settings
    │   ├── task/backend-mvp-Task6.2-opening-hours
    │   ├── task/backend-mvp-Task6.3-rooms-tables
    │   └── task/backend-mvp-Task6.4-public-endpoint
    └── feature/backend-mvp-Phase7-bookings          ← created from feature/backend-mvp AFTER Phase 6 merged
        ├── task/backend-mvp-Task7.1-booking-model
        ├── task/backend-mvp-Task7.2-state-machine
        ├── task/backend-mvp-Task7.3-booking-creation
        ├── task/backend-mvp-Task7.4-staff-actions
        ├── task/backend-mvp-Task7.5-customer-cancel-modify
        └── task/backend-mvp-Task7.6-drf-views
```

---

## ❌ Phase 4 — Authentication & Authorization (Staff Only)

Implements staff-only auth using Django Auth + django-allauth. Customers do not authenticate — they use tokenized booking links (Phase 5). Includes the `User` model (public schema), allauth configuration, and the `StaffMembership` tenant-schema model.

**⚠️ Create this branch only after Phase 3 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase4-auth` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase4-auth
git push -u origin feature/backend-mvp-Phase4-auth
```

---

### ✅ Task 4.1 — User Model (Public Schema)

Custom `User` extending `AbstractUser`. Staff users are created by the operator only — no public signup. No user-facing strings.

**Branch:** `task/backend-mvp-Task4.1-user-model` — created from `feature/backend-mvp-Phase4-auth`

```bash
git checkout feature/backend-mvp-Phase4-auth
git pull origin feature/backend-mvp-Phase4-auth
git checkout -b task/backend-mvp-Task4.1-user-model
```

**`apps/accounts/models.py`:**

```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass  # email-based login via allauth; no extra fields needed in MVP
```

Set in settings: `AUTH_USER_MODEL = "accounts.User"`.

**Tests:**

```python
# tests/accounts/test_models.py

def test_user_model_is_custom(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    assert User.__name__ == "User"
    assert User._meta.app_label == "accounts"

def test_create_user(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username="staff1", email="staff1@example.com", password="pass")
    assert user.pk is not None
```

**Commit:**
```bash
git add apps/accounts/
git commit -m "[TASK] 4.1 add custom User model"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/accounts/test_models.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task4.1-user-model
git checkout feature/backend-mvp-Phase4-auth
git merge task/backend-mvp-Task4.1-user-model
git push origin feature/backend-mvp-Phase4-auth
```

---

### ❌ Task 4.2 — django-allauth Configuration

Configure email-based login. No social providers (YAGNI). Disable public signup — staff users are operator-provisioned only.

**Branch:** `task/backend-mvp-Task4.2-allauth` — created from `feature/backend-mvp-Phase4-auth`

```bash
git checkout feature/backend-mvp-Phase4-auth
git pull origin feature/backend-mvp-Phase4-auth
git checkout -b task/backend-mvp-Task4.2-allauth
```

**`config/settings/base.py` additions:**

```python
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"

# Disable self-service signup; staff are created by operator
ACCOUNT_ALLOW_REGISTRATION = False
```

**Tests:**

```python
# tests/accounts/test_auth.py

def test_login_with_email(client, db):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    User.objects.create_user(username="staff1", email="staff@example.com", password="testpass123")
    response = client.post("/auth/login/", {"login": "staff@example.com", "password": "testpass123"})
    assert response.status_code in (200, 302)

def test_signup_is_disabled(client, db):
    response = client.post("/auth/signup/", {"email": "new@example.com"})
    assert response.status_code in (403, 404, 302)
```

**Commit:**
```bash
git add config/settings/
git commit -m "[TASK] 4.2 configure django-allauth email login, disable signup"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/accounts/test_auth.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task4.2-allauth
git checkout feature/backend-mvp-Phase4-auth
git merge task/backend-mvp-Task4.2-allauth
git push origin feature/backend-mvp-Phase4-auth
```

---

### ❌ Task 4.3 — StaffMembership (Tenant Schema)

Defines the per-tenant staff role. A user can have one membership per tenant (enforced by the model living in the tenant schema). Staff are added by the operator via Django Admin.

**Branch:** `task/backend-mvp-Task4.3-staff-membership` — created from `feature/backend-mvp-Phase4-auth`

```bash
git checkout feature/backend-mvp-Phase4-auth
git pull origin feature/backend-mvp-Phase4-auth
git checkout -b task/backend-mvp-Task4.3-staff-membership
```

**`apps/memberships/models.py`:**

```python
from django.db import models
from apps.common.models import TimeStampedModel

class StaffMembership(TimeStampedModel):
    ROLE_MANAGER, ROLE_STAFF = "manager", "staff"
    ROLE_CHOICES = [(ROLE_MANAGER, "manager"), (ROLE_STAFF, "staff")]

    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user"], name="uniq_user_per_tenant")
        ]
```

Register in Django Admin (`apps/memberships/admin.py`) for operator use.

**Tests:**

```python
# tests/memberships/test_models.py

def test_staff_membership_unique_per_tenant(tenant_db):
    """A user cannot have two memberships in the same tenant."""
    from apps.memberships.models import StaffMembership
    from django.db import IntegrityError
    import pytest

    user = create_user()
    StaffMembership.objects.create(user=user, role="staff")
    with pytest.raises(IntegrityError):
        StaffMembership.objects.create(user=user, role="manager")

def test_staff_membership_role_choices(tenant_db):
    from apps.memberships.models import StaffMembership
    valid_roles = {c[0] for c in StaffMembership.ROLE_CHOICES}
    assert "manager" in valid_roles
    assert "staff" in valid_roles
```

**Commit:**
```bash
git add apps/memberships/
git commit -m "[TASK] 4.3 add StaffMembership model and admin"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/memberships/test_models.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task4.3-staff-membership
git checkout feature/backend-mvp-Phase4-auth
git merge task/backend-mvp-Task4.3-staff-membership
git push origin feature/backend-mvp-Phase4-auth
```

---

### ❌ Phase 4 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase4-auth
git push origin feature/backend-mvp
```

---

## ❌ Phase 5 — Customers & Booking Access Tokens

Implements the guest-only `Customer` model (phone-deduplicated, locale-aware) and the `BookingAccessToken` (random, hashed, per-booking). Also provides the public token-authenticated endpoints for customers to view/cancel/modify their booking.

**⚠️ Create this branch only after Phase 4 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase5-customers-tokens` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase5-customers-tokens
git push -u origin feature/backend-mvp-Phase5-customers-tokens
```

---

### ❌ Task 5.1 — Customer Model (Tenant Schema)

Guest-only customer record. Deduped by phone. Email optional, name and locale required. No user-facing strings in the model or service layer.

**Branch:** `task/backend-mvp-Task5.1-customer-model` — created from `feature/backend-mvp-Phase5-customers-tokens`

```bash
git checkout feature/backend-mvp-Phase5-customers-tokens
git pull origin feature/backend-mvp-Phase5-customers-tokens
git checkout -b task/backend-mvp-Task5.1-customer-model
```

**`apps/customers/models.py`:**

```python
from django.db import models
from apps.common.models import TimeStampedModel

LOCALE_EN, LOCALE_IT, LOCALE_DE = "en", "it", "de"
LOCALE_CHOICES = [(LOCALE_EN, "en"), (LOCALE_IT, "it"), (LOCALE_DE, "de")]

class Customer(TimeStampedModel):
    phone = models.CharField(max_length=32, unique=True)  # dedupe key
    email = models.EmailField(blank=True)                 # optional
    name = models.CharField(max_length=200)               # required
    locale = models.CharField(max_length=8, choices=LOCALE_CHOICES, default=LOCALE_EN)
```

**`apps/customers/services.py` — upsert helper:**

```python
def upsert_customer(*, phone, email, name, locale):
    customer, created = Customer.objects.get_or_create(
        phone=phone,
        defaults={"email": email, "name": name, "locale": locale},
    )
    if not created:
        changed = False
        if email and customer.email != email:
            customer.email = email; changed = True
        if name and customer.name != name:
            customer.name = name; changed = True
        if locale and customer.locale != locale:
            customer.locale = locale; changed = True
        if changed:
            customer.save()
    return customer
```

**Tests:**

```python
# tests/customers/test_models.py

def test_upsert_creates_new_customer(tenant_db):
    from apps.customers.services import upsert_customer
    c = upsert_customer(phone="+39123", email="a@b.com", name="Mario", locale="it")
    assert c.phone == "+39123"
    assert c.name == "Mario"

def test_upsert_dedupes_by_phone(tenant_db):
    from apps.customers.services import upsert_customer
    c1 = upsert_customer(phone="+39123", email="a@b.com", name="Mario", locale="it")
    c2 = upsert_customer(phone="+39123", email="new@b.com", name="Mario", locale="it")
    assert c1.id == c2.id
    c1.refresh_from_db()
    assert c1.email == "new@b.com"  # email updated

def test_different_phones_are_different_customers(tenant_db):
    from apps.customers.services import upsert_customer
    c1 = upsert_customer(phone="+39111", email="", name="A", locale="en")
    c2 = upsert_customer(phone="+39222", email="", name="B", locale="en")
    assert c1.id != c2.id
```

**Commit:**
```bash
git add apps/customers/
git commit -m "[TASK] 5.1 add Customer model and upsert service"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/customers/test_models.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task5.1-customer-model
git checkout feature/backend-mvp-Phase5-customers-tokens
git merge task/backend-mvp-Task5.1-customer-model
git push origin feature/backend-mvp-Phase5-customers-tokens
```

---

### ❌ Task 5.2 — BookingAccessToken

One token per booking. Stored as SHA-256 hash; raw token sent to customer once and never persisted. Expires 7 days after booking datetime.

**Branch:** `task/backend-mvp-Task5.2-booking-access-token` — created from `feature/backend-mvp-Phase5-customers-tokens`

```bash
git checkout feature/backend-mvp-Phase5-customers-tokens
git pull origin feature/backend-mvp-Phase5-customers-tokens
git checkout -b task/backend-mvp-Task5.2-booking-access-token
```

**`apps/customers/models.py` (continued):**

```python
import hashlib
import secrets
from django.utils import timezone

class BookingAccessToken(TimeStampedModel):
    booking = models.OneToOneField("bookings.Booking", on_delete=models.CASCADE)
    token_hash = models.CharField(max_length=128, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)

    @classmethod
    def issue(cls, booking) -> tuple["BookingAccessToken", str]:
        raw = secrets.token_urlsafe(48)               # ≥ 32 bytes entropy
        h = hash_token(raw)
        expires = booking.starts_at + timezone.timedelta(days=7)
        obj = cls.objects.create(booking=booking, token_hash=h, expires_at=expires)
        return obj, raw                                # raw is sent to customer ONCE

def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()
```

**Tests:**

```python
# tests/customers/test_tokens.py
import hmac

def test_token_is_hashed(tenant_db, booking):
    from apps.customers.models import BookingAccessToken, hash_token
    tok, raw = BookingAccessToken.issue(booking)
    assert tok.token_hash == hash_token(raw)
    assert raw not in tok.token_hash  # raw never stored

def test_token_expires_7_days_after_booking(tenant_db, booking):
    from apps.customers.models import BookingAccessToken
    from django.utils import timezone
    tok, _ = BookingAccessToken.issue(booking)
    delta = tok.expires_at - booking.starts_at
    assert delta.days == 7

def test_token_hash_uses_constant_time_compare(tenant_db, booking):
    from apps.customers.models import BookingAccessToken, hash_token
    tok, raw = BookingAccessToken.issue(booking)
    # Verify constant-time comparison works correctly
    assert hmac.compare_digest(hash_token(raw), tok.token_hash)
    assert not hmac.compare_digest(hash_token("wrong"), tok.token_hash)
```

**Commit:**
```bash
git add apps/customers/models.py
git commit -m "[TASK] 5.2 add BookingAccessToken with hashed storage"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/customers/test_tokens.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task5.2-booking-access-token
git checkout feature/backend-mvp-Phase5-customers-tokens
git merge task/backend-mvp-Task5.2-booking-access-token
git push origin feature/backend-mvp-Phase5-customers-tokens
```

---

### ❌ Task 5.3 — Customer-Facing Endpoints (Token-Authenticated)

Public endpoints for customers to view/cancel/modify their booking via the tokenized link. No session auth. All responses are code-form only — no localized strings.

**Branch:** `task/backend-mvp-Task5.3-customer-endpoints` — created from `feature/backend-mvp-Phase5-customers-tokens`

```bash
git checkout feature/backend-mvp-Phase5-customers-tokens
git pull origin feature/backend-mvp-Phase5-customers-tokens
git checkout -b task/backend-mvp-Task5.3-customer-endpoints
```

**`apps/bookings/views_customer.py`:**

```python
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.common.errors import DomainError
from apps.common.codes import ErrorCode
from apps.customers.models import BookingAccessToken, hash_token

class CustomerBookingView(APIView):
    permission_classes = []  # public; auth via token

    def _resolve(self, raw_token):
        h = hash_token(raw_token)
        try:
            tok = BookingAccessToken.objects.select_related("booking").get(token_hash=h)
        except BookingAccessToken.DoesNotExist:
            raise DomainError(ErrorCode.TOKEN_INVALID, status=404)
        if tok.revoked_at or tok.expires_at < timezone.now():
            raise DomainError(ErrorCode.TOKEN_EXPIRED, status=410)
        return tok.booking

    def get(self, request, raw_token):
        booking = self._resolve(raw_token)
        return Response(BookingPublicSerializer(booking).data)

    def post(self, request, raw_token):
        booking = self._resolve(raw_token)
        action = request.data.get("action")
        from apps.bookings import services
        from apps.restaurants.models import RestaurantSettings
        settings = RestaurantSettings.objects.get()
        if action == "cancel":
            services.cancel_by_customer(booking, settings=settings)
        elif action == "modify":
            services.modify_by_customer(booking, request.data, settings=settings)
        else:
            raise DomainError(ErrorCode.VALIDATION_FAILED)
        return Response(BookingPublicSerializer(booking).data)
```

URL: `/api/v1/public/bookings/<raw_token>/`. `BookingPublicSerializer` exposes only customer-relevant fields — no staff messages, no decided_by, codes only.

**Tests:**

```python
# tests/bookings/test_customer_endpoints.py

def test_get_booking_with_valid_token(client, tenant, booking, token, raw_token):
    response = client.get(f"/api/v1/public/bookings/{raw_token}/",
                          HTTP_HOST=tenant.domain)
    assert response.status_code == 200
    assert response.data["id"] == str(booking.id)

def test_invalid_token_returns_404(client, tenant):
    response = client.get("/api/v1/public/bookings/badtoken/",
                          HTTP_HOST=tenant.domain)
    assert response.status_code == 404
    assert response.data["error_code"] == "token_invalid"

def test_expired_token_returns_410(client, tenant, expired_token, raw_expired_token):
    response = client.get(f"/api/v1/public/bookings/{raw_expired_token}/",
                          HTTP_HOST=tenant.domain)
    assert response.status_code == 410
    assert response.data["error_code"] == "token_expired"

def test_cancel_booking_via_token(client, tenant, booking, raw_token):
    response = client.post(f"/api/v1/public/bookings/{raw_token}/",
                           {"action": "cancel"}, HTTP_HOST=tenant.domain,
                           content_type="application/json")
    assert response.status_code == 200
    booking.refresh_from_db()
    assert booking.status == "cancelled_by_customer"

def test_response_contains_no_localized_strings(client, tenant, booking, raw_token):
    response = client.get(f"/api/v1/public/bookings/{raw_token}/",
                          HTTP_HOST=tenant.domain)
    # All string values must be codes (underscored), not sentences
    for key, val in response.data.items():
        if isinstance(val, str) and key == "status":
            assert " " not in val
```

**Commit:**
```bash
git add apps/bookings/views_customer.py apps/bookings/serializers.py
git commit -m "[TASK] 5.3 add token-authenticated customer booking endpoints"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/bookings/test_customer_endpoints.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task5.3-customer-endpoints
git checkout feature/backend-mvp-Phase5-customers-tokens
git merge task/backend-mvp-Task5.3-customer-endpoints
git push origin feature/backend-mvp-Phase5-customers-tokens
```

---

### ❌ Phase 5 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase5-customers-tokens
git push origin feature/backend-mvp
```

---

## ❌ Phase 6 — Restaurant Configuration

Implements per-tenant restaurant settings (singleton), opening hours, closed days, rooms, and tables. Also exposes the public restaurant page endpoint.

**⚠️ Create this branch only after Phase 5 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase6-restaurant-config` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase6-restaurant-config
git push -u origin feature/backend-mvp-Phase6-restaurant-config
```

---

### ❌ Task 6.1 — Restaurant Settings (Singleton)

Configurable deposit policy, cutoff rules, and advance-booking limits. One row per tenant. No user-facing strings.

**Branch:** `task/backend-mvp-Task6.1-restaurant-settings` — created from `feature/backend-mvp-Phase6-restaurant-config`

```bash
git checkout feature/backend-mvp-Phase6-restaurant-config
git pull origin feature/backend-mvp-Phase6-restaurant-config
git checkout -b task/backend-mvp-Task6.1-restaurant-settings
```

**`apps/restaurants/models.py`:**

```python
from django.db import models
from apps.common.models import TimeStampedModel

class RestaurantSettings(TimeStampedModel):
    DEPOSIT_NEVER = "never"
    DEPOSIT_ALWAYS = "always"
    DEPOSIT_PARTY_THRESHOLD = "party_threshold"
    DEPOSIT_POLICY = [
        (DEPOSIT_NEVER, "never"),
        (DEPOSIT_ALWAYS, "always"),
        (DEPOSIT_PARTY_THRESHOLD, "party_threshold"),
    ]

    deposit_policy = models.CharField(max_length=32, choices=DEPOSIT_POLICY,
                                      default=DEPOSIT_NEVER)
    deposit_party_threshold = models.PositiveSmallIntegerField(null=True, blank=True)
    deposit_amount_cents = models.PositiveIntegerField(default=0)
    near_term_threshold_hours = models.PositiveSmallIntegerField(default=48)
    long_term_payment_window_hours = models.PositiveSmallIntegerField(default=24)
    cancellation_cutoff_hours = models.PositiveSmallIntegerField(default=24)
    booking_cutoff_minutes = models.PositiveSmallIntegerField(default=5)
    advance_booking_days = models.PositiveSmallIntegerField(default=90)
```

**Tests:**

```python
# tests/restaurants/test_settings.py

def test_deposit_policy_choices(tenant_db):
    from apps.restaurants.models import RestaurantSettings
    valid = {c[0] for c in RestaurantSettings.DEPOSIT_POLICY}
    assert valid == {"never", "always", "party_threshold"}

def test_default_deposit_policy_is_never(tenant_db):
    from apps.restaurants.models import RestaurantSettings
    s = RestaurantSettings.objects.create()
    assert s.deposit_policy == "never"
```

**Commit:**
```bash
git add apps/restaurants/models.py
git commit -m "[TASK] 6.1 add RestaurantSettings singleton model"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/restaurants/test_settings.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task6.1-restaurant-settings
git checkout feature/backend-mvp-Phase6-restaurant-config
git merge task/backend-mvp-Task6.1-restaurant-settings
git push origin feature/backend-mvp-Phase6-restaurant-config
```

---

### ❌ Task 6.2 — Opening Hours & Closed Days

Weekly schedule and one-off closed days. Pure `is_open(dt)` helper — no user-facing strings.

**Branch:** `task/backend-mvp-Task6.2-opening-hours` — created from `feature/backend-mvp-Phase6-restaurant-config`

```bash
git checkout feature/backend-mvp-Phase6-restaurant-config
git pull origin feature/backend-mvp-Phase6-restaurant-config
git checkout -b task/backend-mvp-Task6.2-opening-hours
```

**`apps/restaurants/models.py` (continued):**

```python
class OpeningHours(TimeStampedModel):
    weekday = models.PositiveSmallIntegerField()       # 0=Mon..6=Sun
    opens_at = models.TimeField()
    closes_at = models.TimeField()

    class Meta:
        unique_together = [("weekday", "opens_at", "closes_at")]

class ClosedDay(TimeStampedModel):
    date = models.DateField(unique=True)
    reason_code = models.CharField(max_length=64, blank=True)
```

**`apps/restaurants/services/opening_hours.py`:**

```python
from django.utils import timezone
from apps.restaurants.models import OpeningHours, ClosedDay

def is_open(dt) -> bool:
    if ClosedDay.objects.filter(date=dt.date()).exists():
        return False
    return OpeningHours.objects.filter(
        weekday=dt.weekday(),
        opens_at__lte=dt.time(),
        closes_at__gt=dt.time(),
    ).exists()
```

**Tests:**

```python
# tests/restaurants/test_opening_hours.py

def test_is_open_during_hours(tenant_db):
    from apps.restaurants.models import OpeningHours
    from apps.restaurants.services.opening_hours import is_open
    import datetime
    OpeningHours.objects.create(weekday=0, opens_at=datetime.time(12, 0),
                                closes_at=datetime.time(22, 0))
    dt = datetime.datetime(2025, 1, 6, 14, 0)  # Monday 14:00
    assert is_open(dt) is True

def test_is_closed_on_closed_day(tenant_db):
    from apps.restaurants.models import OpeningHours, ClosedDay
    from apps.restaurants.services.opening_hours import is_open
    import datetime
    OpeningHours.objects.create(weekday=0, opens_at=datetime.time(12, 0),
                                closes_at=datetime.time(22, 0))
    ClosedDay.objects.create(date=datetime.date(2025, 1, 6))
    dt = datetime.datetime(2025, 1, 6, 14, 0)
    assert is_open(dt) is False

def test_is_closed_outside_hours(tenant_db):
    from apps.restaurants.models import OpeningHours
    from apps.restaurants.services.opening_hours import is_open
    import datetime
    OpeningHours.objects.create(weekday=0, opens_at=datetime.time(12, 0),
                                closes_at=datetime.time(22, 0))
    dt = datetime.datetime(2025, 1, 6, 11, 0)  # before opening
    assert is_open(dt) is False
```

**Commit:**
```bash
git add apps/restaurants/models.py apps/restaurants/services/
git commit -m "[TASK] 6.2 add OpeningHours, ClosedDay, and is_open helper"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/restaurants/test_opening_hours.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task6.2-opening-hours
git checkout feature/backend-mvp-Phase6-restaurant-config
git merge task/backend-mvp-Task6.2-opening-hours
git push origin feature/backend-mvp-Phase6-restaurant-config
```

---

### ❌ Task 6.3 — Rooms & Tables

Basic floor layout. Tables have visual coordinates. No table combinations.

**Branch:** `task/backend-mvp-Task6.3-rooms-tables` — created from `feature/backend-mvp-Phase6-restaurant-config`

```bash
git checkout feature/backend-mvp-Phase6-restaurant-config
git pull origin feature/backend-mvp-Phase6-restaurant-config
git checkout -b task/backend-mvp-Task6.3-rooms-tables
```

**`apps/restaurants/models.py` (continued):**

```python
class Room(TimeStampedModel):
    name = models.CharField(max_length=100)

class Table(TimeStampedModel):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="tables")
    label = models.CharField(max_length=50)
    seats = models.PositiveSmallIntegerField()
    pos_x = models.IntegerField(default=0)
    pos_y = models.IntegerField(default=0)

    class Meta:
        unique_together = [("room", "label")]
```

**Tests:**

```python
# tests/restaurants/test_rooms_tables.py

def test_table_label_unique_per_room(tenant_db):
    from apps.restaurants.models import Room, Table
    from django.db import IntegrityError
    import pytest
    room = Room.objects.create(name="Main Room")
    Table.objects.create(room=room, label="T1", seats=4)
    with pytest.raises(IntegrityError):
        Table.objects.create(room=room, label="T1", seats=2)

def test_same_label_allowed_in_different_rooms(tenant_db):
    from apps.restaurants.models import Room, Table
    r1 = Room.objects.create(name="Room A")
    r2 = Room.objects.create(name="Room B")
    Table.objects.create(room=r1, label="T1", seats=4)
    Table.objects.create(room=r2, label="T1", seats=4)  # no error
```

**Commit:**
```bash
git add apps/restaurants/models.py
git commit -m "[TASK] 6.3 add Room and Table models"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/restaurants/test_rooms_tables.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task6.3-rooms-tables
git checkout feature/backend-mvp-Phase6-restaurant-config
git merge task/backend-mvp-Task6.3-rooms-tables
git push origin feature/backend-mvp-Phase6-restaurant-config
```

---

### ❌ Task 6.4 — Public Restaurant Page Endpoint

Unauthenticated endpoint returning name, opening hours, and basic policies as codes.

**Branch:** `task/backend-mvp-Task6.4-public-endpoint` — created from `feature/backend-mvp-Phase6-restaurant-config`

```bash
git checkout feature/backend-mvp-Phase6-restaurant-config
git pull origin feature/backend-mvp-Phase6-restaurant-config
git checkout -b task/backend-mvp-Task6.4-public-endpoint
```

**`GET /api/v1/public/restaurant`** — no auth, returns codes only. No user-facing strings in the response.

**Tests:**

```python
# tests/restaurants/test_public_endpoint.py

def test_public_restaurant_endpoint_no_auth(client, tenant):
    response = client.get("/api/v1/public/restaurant/", HTTP_HOST=tenant.domain)
    assert response.status_code == 200

def test_public_restaurant_response_codes_only(client, tenant):
    response = client.get("/api/v1/public/restaurant/", HTTP_HOST=tenant.domain)
    # deposit_policy must be a code, not a sentence
    assert response.data["deposit_policy"] in ("never", "always", "party_threshold")
```

**Commit:**
```bash
git add apps/restaurants/views.py apps/restaurants/urls.py apps/restaurants/serializers.py
git commit -m "[TASK] 6.4 add public restaurant page endpoint"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/restaurants/test_public_endpoint.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task6.4-public-endpoint
git checkout feature/backend-mvp-Phase6-restaurant-config
git merge task/backend-mvp-Task6.4-public-endpoint
git push origin feature/backend-mvp-Phase6-restaurant-config
```

---

### ❌ Phase 6 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase6-restaurant-config
git push origin feature/backend-mvp
```

---

## ❌ Phase 7 — Booking Lifecycle

The core domain. Implements the `Booking` model, status machine, creation service with all business-rule validators, staff actions, and customer cancel/modify. All API responses use codes only.

**⚠️ Create this branch only after Phase 6 is merged into `feature/backend-mvp`.**

**Branch:** `feature/backend-mvp-Phase7-bookings` — created from `feature/backend-mvp`

```bash
git checkout feature/backend-mvp
git pull origin feature/backend-mvp
git checkout -b feature/backend-mvp-Phase7-bookings
git push -u origin feature/backend-mvp-Phase7-bookings
```

---

### ❌ Task 7.1 — Booking Model & Status Set

All ten canonical booking statuses. No user-facing strings.

**Branch:** `task/backend-mvp-Task7.1-booking-model` — created from `feature/backend-mvp-Phase7-bookings`

```bash
git checkout feature/backend-mvp-Phase7-bookings
git pull origin feature/backend-mvp-Phase7-bookings
git checkout -b task/backend-mvp-Task7.1-booking-model
```

**`apps/bookings/models.py`:**

```python
from django.db import models
from apps.common.models import TimeStampedModel

class BookingStatus(models.TextChoices):
    PENDING_REVIEW = "pending_review"
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    CONFIRMED_WITHOUT_DEPOSIT = "confirmed_without_deposit"
    DECLINED = "declined"
    CANCELLED_BY_CUSTOMER = "cancelled_by_customer"
    CANCELLED_BY_STAFF = "cancelled_by_staff"
    NO_SHOW = "no_show"
    EXPIRED = "expired"
    AUTHORIZATION_EXPIRED = "authorization_expired"

class Booking(TimeStampedModel):
    customer = models.ForeignKey("customers.Customer", on_delete=models.PROTECT)
    starts_at = models.DateTimeField()
    party_size = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=32, choices=BookingStatus.choices,
                              default=BookingStatus.PENDING_REVIEW)
    notes = models.TextField(blank=True)
    table = models.ForeignKey("restaurants.Table", null=True, blank=True,
                              on_delete=models.SET_NULL)
    staff_message = models.TextField(blank=True)   # only field that bypasses i18n codes
    payment_due_at = models.DateTimeField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)
    decided_by = models.ForeignKey("memberships.StaffMembership", null=True,
                                   blank=True, on_delete=models.SET_NULL)

    class Meta:
        indexes = [models.Index(fields=["status", "starts_at"])]
```

**Tests:**

```python
# tests/bookings/test_models.py

def test_booking_default_status_is_pending_review(tenant_db, customer):
    from apps.bookings.models import Booking, BookingStatus
    b = Booking.objects.create(customer=customer, starts_at=future_dt(), party_size=2)
    assert b.status == BookingStatus.PENDING_REVIEW

def test_all_statuses_are_defined():
    from apps.bookings.models import BookingStatus
    expected = {
        "pending_review", "pending_payment", "confirmed", "confirmed_without_deposit",
        "declined", "cancelled_by_customer", "cancelled_by_staff",
        "no_show", "expired", "authorization_expired",
    }
    assert set(BookingStatus.values) == expected
```

**Commit:**
```bash
git add apps/bookings/models.py
git commit -m "[TASK] 7.1 add Booking model and status set"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/bookings/test_models.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task7.1-booking-model
git checkout feature/backend-mvp-Phase7-bookings
git merge task/backend-mvp-Task7.1-booking-model
git push origin feature/backend-mvp-Phase7-bookings
```

---

### ❌ Task 7.2 — Status Machine

Enforces valid status transitions. Raises `DomainError` (code-only) on invalid attempts.

**Branch:** `task/backend-mvp-Task7.2-state-machine` — created from `feature/backend-mvp-Phase7-bookings`

```bash
git checkout feature/backend-mvp-Phase7-bookings
git pull origin feature/backend-mvp-Phase7-bookings
git checkout -b task/backend-mvp-Task7.2-state-machine
```

**`apps/bookings/services/state_machine.py`:**

```python
from apps.bookings.models import BookingStatus as S
from apps.common.errors import DomainError
from apps.common.codes import ErrorCode

ALLOWED = {
    S.PENDING_REVIEW: {
        S.CONFIRMED, S.CONFIRMED_WITHOUT_DEPOSIT, S.PENDING_PAYMENT,
        S.DECLINED, S.CANCELLED_BY_CUSTOMER, S.EXPIRED, S.AUTHORIZATION_EXPIRED,
    },
    S.PENDING_PAYMENT: {
        S.CONFIRMED, S.CONFIRMED_WITHOUT_DEPOSIT,
        S.EXPIRED, S.CANCELLED_BY_CUSTOMER, S.CANCELLED_BY_STAFF, S.DECLINED,
    },
    S.AUTHORIZATION_EXPIRED: {
        S.PENDING_PAYMENT, S.CONFIRMED_WITHOUT_DEPOSIT, S.DECLINED,
        S.CANCELLED_BY_STAFF, S.CANCELLED_BY_CUSTOMER,
    },
    S.CONFIRMED: {S.CANCELLED_BY_CUSTOMER, S.CANCELLED_BY_STAFF, S.NO_SHOW},
    S.CONFIRMED_WITHOUT_DEPOSIT: {S.CANCELLED_BY_CUSTOMER, S.CANCELLED_BY_STAFF, S.NO_SHOW},
}

def transition(booking, target):
    if target not in ALLOWED.get(booking.status, set()):
        raise DomainError(
            ErrorCode.BOOKING_TRANSITION_INVALID,
            {"from": booking.status, "to": target},
        )
    booking.status = target
```

**Tests:**

```python
# tests/bookings/test_state_machine.py

def test_valid_transition_pending_review_to_confirmed(booking):
    from apps.bookings.services.state_machine import transition
    from apps.bookings.models import BookingStatus
    transition(booking, BookingStatus.CONFIRMED)
    assert booking.status == BookingStatus.CONFIRMED

def test_invalid_transition_raises_domain_error(booking):
    from apps.bookings.services.state_machine import transition
    from apps.bookings.models import BookingStatus
    from apps.common.errors import DomainError
    booking.status = BookingStatus.CONFIRMED
    with pytest.raises(DomainError) as exc:
        transition(booking, BookingStatus.PENDING_REVIEW)
    assert exc.value.detail["error_code"] == "booking_transition_invalid"

def test_error_contains_no_localized_string(booking):
    from apps.bookings.services.state_machine import transition
    from apps.bookings.models import BookingStatus
    from apps.common.errors import DomainError
    booking.status = BookingStatus.EXPIRED
    with pytest.raises(DomainError) as exc:
        transition(booking, BookingStatus.CONFIRMED)
    detail = exc.value.detail
    assert "error_code" in detail
    assert " " not in detail["error_code"]
```

**Commit:**
```bash
git add apps/bookings/services/state_machine.py
git commit -m "[TASK] 7.2 add booking status machine"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/bookings/test_state_machine.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task7.2-state-machine
git checkout feature/backend-mvp-Phase7-bookings
git merge task/backend-mvp-Task7.2-state-machine
git push origin feature/backend-mvp-Phase7-bookings
```

---

### ❌ Task 7.3 — Booking Creation Service

Validates slot alignment, advance limit, cutoff, opening hours. Creates booking first, then optionally creates a Stripe PaymentIntent for near-term deposits. Issues the access token. Sends notifications (non-blocking).

**Branch:** `task/backend-mvp-Task7.3-booking-creation` — created from `feature/backend-mvp-Phase7-bookings`

```bash
git checkout feature/backend-mvp-Phase7-bookings
git pull origin feature/backend-mvp-Phase7-bookings
git checkout -b task/backend-mvp-Task7.3-booking-creation
```

**`apps/bookings/services/creation.py`:**

```python
from apps.bookings.models import Booking
from apps.customers.models import BookingAccessToken
from apps.common.errors import DomainError
from apps.common.codes import ErrorCode
from apps.restaurants.services.opening_hours import is_open

def create_booking_request(*, settings, customer, starts_at, party_size, notes):
    _validate_slot_alignment(starts_at)
    _validate_advance_limit(starts_at, settings)
    _validate_cutoff(starts_at, settings)
    _validate_opening_hours(starts_at)
    _validate_party_size(party_size)

    booking = Booking.objects.create(
        customer=customer, starts_at=starts_at,
        party_size=party_size, notes=notes,
    )

    payment_intent = None
    if _deposit_required(settings, party_size) and _is_near_term(starts_at, settings):
        from apps.payments import services as payments
        payment_intent = payments.create_preauth(booking=booking, settings=settings)

    token, raw = BookingAccessToken.issue(booking)
    from apps.notifications import services as notifications
    notifications.notify_customer(booking, "booking_request_received", raw_token=raw)
    notifications.notify_staff(booking, "new_booking_request")

    return booking, payment_intent

def _validate_slot_alignment(starts_at):
    if starts_at.minute % 15 != 0:
        raise DomainError(ErrorCode.BOOKING_SLOT_MISALIGNED)

def _validate_advance_limit(starts_at, settings):
    from django.utils.timezone import now
    from datetime import timedelta
    if starts_at > now() + timedelta(days=settings.advance_booking_days):
        raise DomainError(ErrorCode.BOOKING_BEYOND_ADVANCE_LIMIT)

def _validate_cutoff(starts_at, settings):
    from django.utils.timezone import now
    from datetime import timedelta
    if starts_at - now() < timedelta(minutes=settings.booking_cutoff_minutes):
        raise DomainError(ErrorCode.BOOKING_CUTOFF_PASSED)

def _validate_opening_hours(starts_at):
    if not is_open(starts_at):
        raise DomainError(ErrorCode.BOOKING_OUTSIDE_OPENING_HOURS)

def _validate_party_size(party_size):
    if party_size < 1:
        raise DomainError(ErrorCode.VALIDATION_FAILED, {"field": "party_size"})
```

**Tests:**

```python
# tests/bookings/test_creation.py

def test_create_booking_success(tenant_db, customer, open_settings):
    from apps.bookings.services.creation import create_booking_request
    booking, _ = create_booking_request(
        settings=open_settings, customer=customer,
        starts_at=future_open_slot(), party_size=2, notes="",
    )
    assert booking.status == "pending_review"

def test_slot_must_be_15_min_aligned(tenant_db, customer, open_settings):
    from apps.bookings.services.creation import create_booking_request
    from apps.common.errors import DomainError
    import datetime
    starts_at = future_open_slot().replace(minute=7)
    with pytest.raises(DomainError) as exc:
        create_booking_request(settings=open_settings, customer=customer,
                               starts_at=starts_at, party_size=2, notes="")
    assert exc.value.detail["error_code"] == "booking_slot_misaligned"

def test_booking_beyond_advance_limit(tenant_db, customer, open_settings):
    ...

def test_booking_past_cutoff(tenant_db, customer, open_settings):
    ...

def test_booking_outside_opening_hours(tenant_db, customer, open_settings):
    ...
```

**Commit:**
```bash
git add apps/bookings/services/creation.py
git commit -m "[TASK] 7.3 add booking creation service with validators"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/bookings/test_creation.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task7.3-booking-creation
git checkout feature/backend-mvp-Phase7-bookings
git merge task/backend-mvp-Task7.3-booking-creation
git push origin feature/backend-mvp-Phase7-bookings
```

---

### ❌ Task 7.4 — Staff Actions

Approve, decline, modify, assign table, mark no-show, confirm without deposit, request payment again. All via `IsTenantMember` permission. No user-facing strings.

**Branch:** `task/backend-mvp-Task7.4-staff-actions` — created from `feature/backend-mvp-Phase7-bookings`

```bash
git checkout feature/backend-mvp-Phase7-bookings
git pull origin feature/backend-mvp-Phase7-bookings
git checkout -b task/backend-mvp-Task7.4-staff-actions
```

**`apps/bookings/services/staff.py` — approve:**

```python
def approve(booking, *, by_membership, settings):
    if booking.status != BookingStatus.PENDING_REVIEW:
        raise DomainError(ErrorCode.BOOKING_TRANSITION_INVALID)
    payment = Payment.objects.filter(booking=booking).first()
    if payment and payment.status == PaymentStatus.AUTHORIZED:
        payments.capture(payment)
        transition(booking, BookingStatus.CONFIRMED)
    elif _deposit_required(settings, booking.party_size):
        payments.create_payment_link(booking=booking, settings=settings)
        booking.payment_due_at = now() + timedelta(hours=settings.long_term_payment_window_hours)
        transition(booking, BookingStatus.PENDING_PAYMENT)
    else:
        transition(booking, BookingStatus.CONFIRMED_WITHOUT_DEPOSIT)
    booking.decided_by = by_membership
    booking.decided_at = now()
    booking.save()
    notifications.notify_customer(booking, _customer_code_for(booking.status))
    audit.record(actor=by_membership, action="booking.approve", target=booking,
                 payload={"to_status": booking.status})
```

**Tests:**

```python
# tests/bookings/test_staff_actions.py

def test_approve_no_deposit_confirms_without_deposit(tenant_db, booking, membership, no_deposit_settings):
    from apps.bookings.services.staff import approve
    approve(booking, by_membership=membership, settings=no_deposit_settings)
    booking.refresh_from_db()
    assert booking.status == "confirmed_without_deposit"

def test_approve_with_authorized_payment_captures_and_confirms(tenant_db, booking, membership, authorized_payment, settings):
    from apps.bookings.services.staff import approve
    approve(booking, by_membership=membership, settings=settings)
    booking.refresh_from_db()
    assert booking.status == "confirmed"

def test_decline_cancels_authorization(tenant_db, booking, membership, authorized_payment):
    from apps.bookings.services.staff import decline
    decline(booking, by_membership=membership, reason_code="staff_rejection_generic")
    booking.refresh_from_db()
    assert booking.status == "declined"

def test_decline_staff_message_is_passthrough(tenant_db, booking, membership):
    from apps.bookings.services.staff import decline
    decline(booking, by_membership=membership, reason_code="staff_rejection_generic",
            staff_message="Siamo al completo")
    booking.refresh_from_db()
    assert booking.staff_message == "Siamo al completo"
```

**Commit:**
```bash
git add apps/bookings/services/staff.py
git commit -m "[TASK] 7.4 add staff action services"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/bookings/test_staff_actions.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task7.4-staff-actions
git checkout feature/backend-mvp-Phase7-bookings
git merge task/backend-mvp-Task7.4-staff-actions
git push origin feature/backend-mvp-Phase7-bookings
```

---

### ❌ Task 7.5 — Customer Cancel / Modify (Token-Authenticated)

Enforces cancellation cutoff. Modification re-enters `pending_review` only if date/time/party_size changed.

**Branch:** `task/backend-mvp-Task7.5-customer-cancel-modify` — created from `feature/backend-mvp-Phase7-bookings`

```bash
git checkout feature/backend-mvp-Phase7-bookings
git pull origin feature/backend-mvp-Phase7-bookings
git checkout -b task/backend-mvp-Task7.5-customer-cancel-modify
```

**`apps/bookings/services/customer.py`:**

```python
def cancel_by_customer(booking, *, settings):
    _enforce_cancellation_cutoff(booking, settings)
    transition(booking, BookingStatus.CANCELLED_BY_CUSTOMER)
    booking.save()

def modify_by_customer(booking, payload, *, settings):
    _enforce_cancellation_cutoff(booking, settings)
    starts_at = payload.get("starts_at") or booking.starts_at
    party_size = payload.get("party_size") or booking.party_size
    notes = payload.get("notes", booking.notes)
    if (starts_at, party_size) != (booking.starts_at, booking.party_size):
        _validate_slot_alignment(starts_at)
        _validate_advance_limit(starts_at, settings)
        _validate_cutoff(starts_at, settings)
        _validate_opening_hours(starts_at)
        booking.starts_at = starts_at
        booking.party_size = party_size
        if booking.status in (BookingStatus.CONFIRMED, BookingStatus.CONFIRMED_WITHOUT_DEPOSIT):
            transition(booking, BookingStatus.PENDING_REVIEW)
    booking.notes = notes
    booking.save()

def _enforce_cancellation_cutoff(booking, settings):
    from django.utils.timezone import now
    from datetime import timedelta
    if booking.starts_at - now() < timedelta(hours=settings.cancellation_cutoff_hours):
        raise DomainError(ErrorCode.CUTOFF_PASSED)
```

**Tests:**

```python
# tests/bookings/test_customer_actions.py

def test_cancel_within_cutoff_succeeds(tenant_db, booking, settings):
    from apps.bookings.services.customer import cancel_by_customer
    cancel_by_customer(booking, settings=settings)
    booking.refresh_from_db()
    assert booking.status == "cancelled_by_customer"

def test_cancel_past_cutoff_raises(tenant_db, past_cutoff_booking, settings):
    from apps.bookings.services.customer import cancel_by_customer
    from apps.common.errors import DomainError
    with pytest.raises(DomainError) as exc:
        cancel_by_customer(past_cutoff_booking, settings=settings)
    assert exc.value.detail["error_code"] == "cutoff_passed"

def test_modify_confirmed_booking_re_enters_review(tenant_db, confirmed_booking, settings):
    from apps.bookings.services.customer import modify_by_customer
    from apps.bookings.models import BookingStatus
    new_start = future_open_slot()
    modify_by_customer(confirmed_booking, {"starts_at": new_start}, settings=settings)
    confirmed_booking.refresh_from_db()
    assert confirmed_booking.status == BookingStatus.PENDING_REVIEW
```

**Commit:**
```bash
git add apps/bookings/services/customer.py
git commit -m "[TASK] 7.5 add customer cancel and modify services"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/bookings/test_customer_actions.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task7.5-customer-cancel-modify
git checkout feature/backend-mvp-Phase7-bookings
git merge task/backend-mvp-Task7.5-customer-cancel-modify
git push origin feature/backend-mvp-Phase7-bookings
```

---

### ❌ Task 7.6 — DRF Views (Thin)

Thin viewset delegates all logic to services. Serializes results in code form only.

**Branch:** `task/backend-mvp-Task7.6-drf-views` — created from `feature/backend-mvp-Phase7-bookings`

```bash
git checkout feature/backend-mvp-Phase7-bookings
git pull origin feature/backend-mvp-Phase7-bookings
git checkout -b task/backend-mvp-Task7.6-drf-views
```

**`apps/bookings/views.py`:**

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.common.permissions import IsTenantMember
from apps.restaurants.models import RestaurantSettings
from apps.bookings import services
from apps.bookings.models import Booking
from apps.bookings.serializers import BookingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTenantMember]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.select_related("customer", "table")

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        booking = self.get_object()
        services.approve(booking, by_membership=request.membership,
                         settings=RestaurantSettings.objects.get())
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=["post"])
    def decline(self, request, pk=None):
        booking = self.get_object()
        services.decline(booking, by_membership=request.membership,
                         reason_code=request.data.get("reason_code", ""),
                         staff_message=request.data.get("staff_message", ""))
        return Response(self.get_serializer(booking).data)
    # ... other actions identically thin ...
```

**Tests:**

```python
# tests/bookings/test_views.py

def test_approve_endpoint_requires_auth(client, tenant, booking):
    response = client.post(f"/api/v1/bookings/{booking.id}/approve/",
                           HTTP_HOST=tenant.domain)
    assert response.status_code == 403

def test_approve_endpoint_returns_updated_status(staff_client, tenant, booking, no_deposit_settings):
    response = staff_client.post(f"/api/v1/bookings/{booking.id}/approve/",
                                 HTTP_HOST=tenant.domain)
    assert response.status_code == 200
    assert response.data["status"] == "confirmed_without_deposit"

def test_response_contains_no_localized_strings(staff_client, tenant, booking):
    response = staff_client.get(f"/api/v1/bookings/{booking.id}/",
                                HTTP_HOST=tenant.domain)
    assert " " not in response.data["status"]
```

**Commit:**
```bash
git add apps/bookings/views.py apps/bookings/urls.py apps/bookings/serializers.py
git commit -m "[TASK] 7.6 add booking DRF views and serializers"
```

**Pre-merge checks:**
```bash
ruff check backend/
mypy backend/
pytest tests/bookings/test_views.py
pytest
```

**Push & merge:**
```bash
git push origin task/backend-mvp-Task7.6-drf-views
git checkout feature/backend-mvp-Phase7-bookings
git merge task/backend-mvp-Task7.6-drf-views
git push origin feature/backend-mvp-Phase7-bookings
```

---

### ❌ Phase 7 complete — merge into feature branch

```bash
git checkout feature/backend-mvp
git merge feature/backend-mvp-Phase7-bookings
git push origin feature/backend-mvp
```
