# Phases 4–7 — Domain Core

Covers staff authentication, the customer model and tokenized booking access, restaurant configuration, and the booking lifecycle (state machine, validation, staff actions, customer self-service).

---

## Phase 4 — Authentication & Authorization (staff only)

Branch: `feature/auth`

Authentication is for **staff only** (managers, staff). Customers do not authenticate (business doc §1, §12).

### Task 4.1 — User model (public schema)

`apps/accounts/models.py`:

```python
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass  # email-based login via allauth; no extra fields needed in MVP
```

`AUTH_USER_MODEL = "accounts.User"`.

### Task 4.2 — django-allauth configuration

Email-based login, no social providers (YAGNI):

```python
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
```

Self-service signup is irrelevant in MVP since staff users are created by the operator. Disable the public signup view if exposed.

### Task 4.3 — StaffMembership (tenant schema)

`apps/memberships/models.py`:

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

A user can have only one membership per tenant (the model lives in the tenant schema, so cross-tenant is naturally separate).

Operator workflow (no API): create staff via Django Admin or an `add_staff` management command.

---

## Phase 5 — Customers & Booking Access Tokens

Branch: `feature/customers-and-tokens`

### Task 5.1 — Customer model (tenant schema)

`apps/customers/models.py`:

```python
from django.db import models
from apps.common.models import TimeStampedModel

LOCALE_EN, LOCALE_IT, LOCALE_DE = "en", "it", "de"
LOCALE_CHOICES = [(LOCALE_EN, "en"), (LOCALE_IT, "it"), (LOCALE_DE, "de")]

class Customer(TimeStampedModel):
    phone = models.CharField(max_length=32, unique=True)  # dedupe key
    email = models.EmailField(blank=True)                 # optional, secondary metadata
    name = models.CharField(max_length=200)               # required
    locale = models.CharField(max_length=8, choices=LOCALE_CHOICES, default=LOCALE_EN)
```

Dedupe rule (business doc §12): `get_or_create(phone=...)`; if found, update email/name/locale when they differ.

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

### Task 5.2 — BookingAccessToken (tenant schema)

`apps/customers/models.py` (continued):

```python
import hashlib
import secrets
from django.db import models
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

Token rules (business doc §1, technical doc §14a):
- 1 token = 1 booking.
- Random, long, unguessable.
- Expires 7 days after `Booking.starts_at`.
- Stored as a SHA-256 hash; the raw token is sent to the customer once, never persisted.
- No OTP in MVP.

### Task 5.3 — Customer-facing endpoints (token-authenticated)

`apps/bookings/views_customer.py`:

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

URL: `/api/v1/public/bookings/<raw_token>/`.

`BookingPublicSerializer` exposes only customer-relevant fields (no internal IDs, no staff messages, no decided_by) — code-form values only.

---

## Phase 6 — Restaurant Configuration

Branch: `feature/restaurant-config`

### Task 6.1 — Restaurant settings (singleton per tenant)

`apps/restaurants/models.py`:

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

### Task 6.2 — Opening hours

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

`apps/restaurants/services/opening_hours.py` exposes a pure `is_open(dt) -> bool` helper.

### Task 6.3 — Rooms & Tables

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

Table combinations explicitly excluded.

### Task 6.4 — Public restaurant page endpoint

`GET /api/v1/public/restaurant` returns name, opening hours, basic policies — code-form. No auth.

---

## Phase 7 — Booking Lifecycle

Branch: `feature/bookings`

### Task 7.1 — Booking model & status set

Canonical Booking statuses (business doc §2):

```python
from django.db import models

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

### Task 7.2 — Status machine

`apps/bookings/services/state_machine.py`:

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

### Task 7.3 — Booking creation service

Per business doc §1, §11. Per technical doc §6: booking is created **first**, then PaymentIntent.

```python
def create_booking_request(*, settings, customer, starts_at, party_size, notes):
    _validate_slot_alignment(starts_at)              # 15-min interval
    _validate_advance_limit(starts_at, settings)     # ≤ advance_booking_days
    _validate_cutoff(starts_at, settings)            # ≥ booking_cutoff_minutes
    _validate_opening_hours(starts_at)               # open + not closed-day
    _validate_party_size(party_size)

    booking = Booking.objects.create(
        customer=customer, starts_at=starts_at,
        party_size=party_size, notes=notes,
    )

    payment_intent = None
    if _deposit_required(settings, party_size) and _is_near_term(starts_at, settings):
        payment_intent = payments.create_preauth(booking=booking, settings=settings)

    token, raw = BookingAccessToken.issue(booking)
    notifications.notify_customer(booking, "booking_request_received", raw_token=raw)
    notifications.notify_staff(booking, "new_booking_request")

    return booking, payment_intent
    # frontend uses payment_intent.client_secret in the Payment Element
```

Each `_validate_*` is a one-liner that raises `DomainError(ErrorCode.X)`. No localized strings.

### Task 7.4 — Staff actions

Endpoints (manager + staff):

- `POST /api/v1/bookings/{id}/approve`
- `POST /api/v1/bookings/{id}/decline`              `{ "reason_code": "...", "staff_message": "..." }`
- `POST /api/v1/bookings/{id}/modify`               body: date/time/party_size/notes/table
- `POST /api/v1/bookings/{id}/assign-table`
- `POST /api/v1/bookings/{id}/mark-no-show`
- `POST /api/v1/bookings/{id}/confirm-without-deposit`   used after `authorization_expired` or deposit-failure
- `POST /api/v1/bookings/{id}/request-payment`           used after `authorization_expired`

Approval logic — distinguishes the three cases per business doc §4:

```python
def approve(booking, *, by_membership, settings):
    if booking.status != BookingStatus.PENDING_REVIEW:
        raise DomainError(ErrorCode.BOOKING_TRANSITION_INVALID)

    payment = Payment.objects.filter(booking=booking).first()

    if payment and payment.status == PaymentStatus.AUTHORIZED:
        # Near-term flow with valid pre-authorization → capture immediately
        payments.capture(payment)
        transition(booking, BookingStatus.CONFIRMED)

    elif _deposit_required(settings, booking.party_size):
        # Long-term flow OR no pre-auth captured → payment link
        payments.create_payment_link(booking=booking, settings=settings)
        booking.payment_due_at = now() + timedelta(
            hours=settings.long_term_payment_window_hours
        )
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

Decline:

```python
def decline(booking, *, by_membership, reason_code, staff_message=""):
    transition(booking, BookingStatus.DECLINED)
    booking.staff_message = staff_message
    booking.decided_by = by_membership
    booking.decided_at = now()
    booking.save()

    payment = Payment.objects.filter(booking=booking).first()
    if payment and payment.status == PaymentStatus.AUTHORIZED:
        payments.cancel_authorization(payment)

    notifications.notify_customer(booking, "booking_declined")
    audit.record(actor=by_membership, action="booking.decline", target=booking,
                 payload={"reason_code": reason_code})
```

`request-payment` and `confirm-without-deposit` (used after `authorization_expired`):

```python
def request_payment_again(booking, *, by_membership, settings):
    payments.create_payment_link(booking=booking, settings=settings)
    booking.payment_due_at = now() + timedelta(
        hours=settings.long_term_payment_window_hours
    )
    transition(booking, BookingStatus.PENDING_PAYMENT)
    booking.save()
    notifications.notify_customer(booking, "payment_required")

def confirm_without_deposit(booking, *, by_membership):
    transition(booking, BookingStatus.CONFIRMED_WITHOUT_DEPOSIT)
    booking.decided_by = by_membership
    booking.decided_at = now()
    booking.save()
    notifications.notify_customer(booking, "booking_approved")
```

### Task 7.5 — Customer cancel/modify (token-authenticated)

```python
def cancel_by_customer(booking, *, settings):
    _enforce_cancellation_cutoff(booking, settings)
    transition(booking, BookingStatus.CANCELLED_BY_CUSTOMER)
    booking.save()
    # Refunds are NOT automatic in MVP. Staff decides manually (see Phase 8).

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
        if booking.status in (BookingStatus.CONFIRMED,
                              BookingStatus.CONFIRMED_WITHOUT_DEPOSIT):
            transition(booking, BookingStatus.PENDING_REVIEW)
    booking.notes = notes
    booking.save()
```

`_enforce_cancellation_cutoff` raises `DomainError(ErrorCode.CUTOFF_PASSED)` if past the cutoff (business doc §5).

### Task 7.6 — DRF views (thin)

```python
class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsTenantMember]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.select_related("customer", "table")

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        booking = self.get_object()
        services.approve(
            booking,
            by_membership=request.membership,
            settings=RestaurantSettings.objects.get(),
        )
        return Response(self.get_serializer(booking).data)
    # other actions identically thin
```
