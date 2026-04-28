"""Tests for booking model status behavior."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.bookings.models import Booking, BookingStatus
from apps.customers.models import Customer
from tests.tenant_helpers import tenant_schema


@pytest.mark.django_db
def test_booking_default_status_is_pending_review():
    with tenant_schema("booking_models"):
        customer = Customer.objects.create(
            phone="+3900011111",
            email="booking@example.com",
            name="Booking Customer",
            locale="en",
        )
        booking = Booking.objects.create(
            customer=customer,
            starts_at=timezone.now() + timedelta(days=1),
            party_size=2,
        )
        assert booking.status == BookingStatus.PENDING_REVIEW


def test_all_statuses_are_defined():
    expected = {
        "pending_review",
        "pending_payment",
        "confirmed",
        "confirmed_without_deposit",
        "declined",
        "cancelled_by_customer",
        "cancelled_by_staff",
        "no_show",
        "expired",
        "authorization_expired",
    }
    assert set(BookingStatus.values) == expected
