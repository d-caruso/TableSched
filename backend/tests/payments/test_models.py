"""Tests for payment models."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta

import pytest
from django.db import IntegrityError, connection
from django.utils import timezone

from apps.bookings.models import Booking
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.payments.models import Payment, PaymentStatus
from apps.restaurants.models import Room, Table


@contextmanager
def payment_model_tables() -> Iterator[None]:
    existing_tables = set(connection.introspection.table_names())
    models_in_order = (Customer, StaffMembership, Room, Table, Booking, Payment)
    for model in models_in_order:
        if model._meta.db_table not in existing_tables:
            with connection.schema_editor() as editor:
                editor.create_model(model)
            existing_tables.add(model._meta.db_table)
    yield


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
    with payment_model_tables():
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
