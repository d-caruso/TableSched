"""Tests for booking model status behavior."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone

from apps.bookings.models import Booking, BookingStatus
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.restaurants.models import Room, Table


@contextmanager
def booking_model_tables() -> Iterator[None]:
    existing_tables = set(connection.introspection.table_names())
    models_in_order = (Customer, StaffMembership, Room, Table, Booking)

    for model in models_in_order:
        if model._meta.db_table not in existing_tables:
            with connection.schema_editor() as editor:
                editor.create_model(model)
            existing_tables.add(model._meta.db_table)
    yield


@pytest.mark.django_db
def test_booking_default_status_is_pending_review():
    with booking_model_tables():
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
