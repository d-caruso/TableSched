"""Tests for booking creation service and validators."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone

from apps.bookings.models import Booking
from apps.bookings.services.creation import create_booking_request
from apps.common.errors import DomainError
from apps.customers.models import BookingAccessToken, Customer
from apps.memberships.models import StaffMembership
from apps.restaurants.models import ClosedDay, OpeningHours, RestaurantSettings, Room, Table


@contextmanager
def creation_tables() -> Iterator[None]:
    existing_tables = set(connection.introspection.table_names())
    models_in_order = (
        Customer,
        StaffMembership,
        Room,
        Table,
        RestaurantSettings,
        OpeningHours,
        ClosedDay,
        Booking,
        BookingAccessToken,
    )
    for model in models_in_order:
        if model._meta.db_table not in existing_tables:
            with connection.schema_editor() as editor:
                editor.create_model(model)
            existing_tables.add(model._meta.db_table)
    yield


def _aligned_future_slot(*, days: int = 1, minutes: int = 0):
    now = timezone.now()
    base = now + timedelta(days=days, minutes=minutes)
    rounded_minutes = (base.minute // 15) * 15
    return base.replace(minute=rounded_minutes, second=0, microsecond=0)


def _seed_opening_for(starts_at) -> None:
    open_time = (starts_at - timedelta(hours=1)).time().replace(microsecond=0)
    close_time = (starts_at + timedelta(hours=2)).time().replace(microsecond=0)
    OpeningHours.objects.create(
        weekday=starts_at.weekday(),
        opens_at=open_time,
        closes_at=close_time,
    )


def _base_settings(**overrides):
    defaults = {
        "deposit_policy": RestaurantSettings.DEPOSIT_NEVER,
        "deposit_party_threshold": None,
        "deposit_amount_cents": 0,
        "near_term_threshold_hours": 48,
        "long_term_payment_window_hours": 24,
        "cancellation_cutoff_hours": 24,
        "booking_cutoff_minutes": 5,
        "advance_booking_days": 90,
    }
    defaults.update(overrides)
    return RestaurantSettings.objects.create(**defaults)


def _customer():
    return Customer.objects.create(
        phone="+3900012345",
        email="creation@example.com",
        name="Creation Customer",
        locale="en",
    )


@pytest.mark.django_db
def test_create_booking_success():
    with creation_tables():
        starts_at = _aligned_future_slot(days=2)
        _seed_opening_for(starts_at)
        settings = _base_settings()
        customer = _customer()

        booking, payment_intent = create_booking_request(
            settings=settings,
            customer=customer,
            starts_at=starts_at,
            party_size=2,
            notes="",
        )

        assert booking.status == "pending_review"
        assert payment_intent is None
        assert BookingAccessToken.objects.filter(booking=booking).exists()


@pytest.mark.django_db
def test_slot_must_be_15_min_aligned():
    with creation_tables():
        starts_at = _aligned_future_slot(days=2).replace(minute=7)
        _seed_opening_for(starts_at)
        settings = _base_settings()
        customer = _customer()

        with pytest.raises(DomainError) as exc:
            create_booking_request(
                settings=settings,
                customer=customer,
                starts_at=starts_at,
                party_size=2,
                notes="",
            )
        assert exc.value.detail["error_code"] == "booking_slot_misaligned"


@pytest.mark.django_db
def test_booking_beyond_advance_limit():
    with creation_tables():
        starts_at = _aligned_future_slot(days=4)
        _seed_opening_for(starts_at)
        settings = _base_settings(advance_booking_days=1)
        customer = _customer()

        with pytest.raises(DomainError) as exc:
            create_booking_request(
                settings=settings,
                customer=customer,
                starts_at=starts_at,
                party_size=2,
                notes="",
            )
        assert exc.value.detail["error_code"] == "booking_beyond_advance_limit"


@pytest.mark.django_db
def test_booking_past_cutoff():
    with creation_tables():
        starts_at = _aligned_future_slot(days=0, minutes=15)
        _seed_opening_for(starts_at)
        settings = _base_settings(booking_cutoff_minutes=120)
        customer = _customer()

        with pytest.raises(DomainError) as exc:
            create_booking_request(
                settings=settings,
                customer=customer,
                starts_at=starts_at,
                party_size=2,
                notes="",
            )
        assert exc.value.detail["error_code"] == "booking_cutoff_passed"


@pytest.mark.django_db
def test_booking_outside_opening_hours():
    with creation_tables():
        starts_at = _aligned_future_slot(days=2)
        settings = _base_settings()
        customer = _customer()

        with pytest.raises(DomainError) as exc:
            create_booking_request(
                settings=settings,
                customer=customer,
                starts_at=starts_at,
                party_size=2,
                notes="",
            )
        assert exc.value.detail["error_code"] == "booking_outside_opening_hours"
