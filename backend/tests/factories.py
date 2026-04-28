"""Factory Boy factories for shared test fixtures."""

from __future__ import annotations

from datetime import timedelta

import factory
from django.utils import timezone

from apps.accounts.models import User
from apps.bookings.models import Booking, BookingStatus, Walkin
from apps.customers.models import BookingAccessToken, Customer
from apps.memberships.models import StaffMembership
from apps.payments.models import Payment, PaymentStatus
from apps.restaurants.models import RestaurantSettings, Room, Table
from apps.tenants.models import Domain, Restaurant


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.Sequence(lambda n: f"user_{n}@example.com")
    password = factory.django.Password("testpass123")


class RestaurantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Restaurant

    schema_name = factory.Sequence(lambda n: f"test_{n}")
    name = factory.Sequence(lambda n: f"Test Restaurant {n}")


class DomainFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Domain

    domain = factory.Sequence(lambda n: f"test-{n}.localhost")
    tenant = factory.SubFactory(RestaurantFactory)
    is_primary = True


class StaffMembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StaffMembership

    user = factory.SubFactory(UserFactory)
    role = StaffMembership.ROLE_STAFF
    is_active = True

    class Params:
        manager = factory.Trait(role=StaffMembership.ROLE_MANAGER)


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Customer

    phone = factory.Sequence(lambda n: f"+3900001{n:04d}")
    email = factory.Sequence(lambda n: f"customer_{n}@example.com")
    name = factory.Sequence(lambda n: f"Customer {n}")
    locale = "en"


class RestaurantSettingsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RestaurantSettings

    deposit_policy = RestaurantSettings.DEPOSIT_NEVER
    deposit_party_threshold = None
    deposit_amount_cents = 0
    near_term_threshold_hours = 48
    long_term_payment_window_hours = 24
    cancellation_cutoff_hours = 24
    booking_cutoff_minutes = 5
    advance_booking_days = 90


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    name = factory.Sequence(lambda n: f"Room {n}")


class TableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Table

    room = factory.SubFactory(RoomFactory)
    label = factory.Sequence(lambda n: f"T{n}")
    seats = 4
    pos_x = 0
    pos_y = 0


class BookingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Booking

    customer = factory.SubFactory(CustomerFactory)
    starts_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=2))
    party_size = 2
    status = BookingStatus.PENDING_REVIEW
    notes = ""
    table = None
    staff_message = ""
    payment_due_at = None
    decided_at = None
    decided_by = None


class WalkinFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Walkin

    starts_at = factory.LazyFunction(lambda: timezone.now())
    party_size = 2
    table = None
    notes = ""


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    booking = factory.SubFactory(BookingFactory)
    kind = Payment.KIND_PREAUTH
    stripe_payment_intent_id = factory.Sequence(lambda n: f"pi_{n}")
    stripe_checkout_session_id = factory.Sequence(lambda n: f"cs_{n}")
    amount_cents = 2500
    currency = "eur"
    status = PaymentStatus.PENDING
    expires_at = None


class BookingAccessTokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BookingAccessToken

    booking = factory.SubFactory(BookingFactory)
    token_hash = factory.Sequence(lambda n: f"hash_{n}")
    expires_at = factory.LazyFunction(lambda: timezone.now() + timedelta(days=7))
    revoked_at = None
