"""Tests for customer cancel/modify booking services."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services.customer_actions import cancel_by_customer, modify_by_customer
from apps.common.errors import DomainError
from apps.customers.models import Customer
from apps.restaurants.models import OpeningHours, RestaurantSettings
from tests.tenant_helpers import tenant_schema


def _settings(**overrides) -> RestaurantSettings:
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


def _booking(*, starts_at, status: str = BookingStatus.PENDING_REVIEW) -> Booking:
    customer = Customer.objects.create(
        phone="+3900075000",
        email="customer-actions@example.com",
        name="Customer Actions",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=starts_at,
        party_size=2,
        status=status,
        notes="initial",
    )


def _seed_opening_for(starts_at) -> None:
    OpeningHours.objects.create(
        weekday=starts_at.weekday(),
        opens_at=(starts_at - timedelta(hours=1)).time().replace(microsecond=0),
        closes_at=(starts_at + timedelta(hours=2)).time().replace(microsecond=0),
    )


@pytest.mark.django_db
def test_cancel_within_cutoff_succeeds():
    with tenant_schema("customer_actions"):
        settings = _settings(cancellation_cutoff_hours=24)
        booking = _booking(starts_at=timezone.now() + timedelta(days=3))

        cancel_by_customer(booking, settings=settings)
        booking.refresh_from_db()

        assert booking.status == "cancelled_by_customer"


@pytest.mark.django_db
def test_cancel_past_cutoff_raises():
    with tenant_schema("customer_actions"):
        settings = _settings(cancellation_cutoff_hours=24)
        booking = _booking(starts_at=timezone.now() + timedelta(hours=2))

        with pytest.raises(DomainError) as exc:
            cancel_by_customer(booking, settings=settings)

        assert exc.value.detail["error_code"] == "cutoff_passed"


@pytest.mark.django_db
def test_modify_confirmed_booking_re_enters_review():
    with tenant_schema("customer_actions"):
        settings = _settings(cancellation_cutoff_hours=24)
        current_start = timezone.now() + timedelta(days=4)
        new_start = timezone.now() + timedelta(days=5)
        current_start = current_start.replace(minute=0, second=0, microsecond=0)
        new_start = new_start.replace(minute=15, second=0, microsecond=0)
        _seed_opening_for(new_start)
        booking = _booking(starts_at=current_start, status=BookingStatus.CONFIRMED)

        modify_by_customer(
            booking,
            {"starts_at": new_start, "party_size": 3},
            settings=settings,
        )
        booking.refresh_from_db()

        assert booking.status == BookingStatus.PENDING_REVIEW
