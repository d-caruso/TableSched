"""Tests for booking status machine transitions."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services.state_machine import transition
from apps.common.errors import DomainError
from apps.customers.models import Customer
from tests.tenant_helpers import tenant_schema


def _build_booking(*, status: str = BookingStatus.PENDING_REVIEW) -> Booking:
    customer = Customer.objects.create(
        phone="+3900099999",
        email="state@example.com",
        name="State Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
        status=status,
    )


@pytest.mark.django_db
def test_valid_transition_pending_review_to_confirmed():
    with tenant_schema("booking_state"):
        booking = _build_booking()
        transition(booking, BookingStatus.CONFIRMED)
        assert booking.status == BookingStatus.CONFIRMED


@pytest.mark.django_db
def test_invalid_transition_raises_domain_error():
    with tenant_schema("booking_state"):
        booking = _build_booking(status=BookingStatus.CONFIRMED)
        with pytest.raises(DomainError) as exc:
            transition(booking, BookingStatus.EXPIRED)
        assert exc.value.detail["error_code"] == "booking_transition_invalid"


@pytest.mark.django_db
def test_error_contains_no_localized_string():
    with tenant_schema("booking_state"):
        booking = _build_booking(status=BookingStatus.EXPIRED)
        with pytest.raises(DomainError) as exc:
            transition(booking, BookingStatus.CONFIRMED)
        detail = exc.value.detail
        assert "error_code" in detail
        assert " " not in detail["error_code"]
