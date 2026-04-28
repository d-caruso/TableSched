"""Tests for payment models."""

from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.bookings.models import Booking
from apps.customers.models import Customer
from apps.payments.models import Payment, PaymentStatus
from tests.payments.helpers import payment_tenant


def _booking() -> Booking:
    customer = Customer.objects.create(
        phone="+3900081000",
        email="payments@example.com",
        name="Payments Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
    )


@pytest.mark.django_db
def test_all_payment_statuses_defined():
    expected = {
        "pending",
        "authorized",
        "captured",
        "failed",
        "refund_pending",
        "refunded",
        "refund_failed",
    }
    assert set(PaymentStatus.values) == expected


@pytest.mark.django_db
def test_payment_is_one_to_one_with_booking():
    with payment_tenant():
        booking = _booking()
        Payment.objects.create(
            booking=booking,
            kind=Payment.KIND_PREAUTH,
            amount_cents=1000,
            status=PaymentStatus.PENDING,
        )

        with pytest.raises(IntegrityError):
            Payment.objects.create(
                booking=booking,
                kind=Payment.KIND_LINK,
                amount_cents=1000,
                status=PaymentStatus.PENDING,
            )
