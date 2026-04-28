"""Tests for booking status machine transitions."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone

from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services.state_machine import transition
from apps.common.errors import DomainError
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.restaurants.models import Room, Table


@contextmanager
def booking_state_tables() -> Iterator[None]:
    existing_tables = set(connection.introspection.table_names())
    models_in_order = (Customer, StaffMembership, Room, Table, Booking)

    for model in models_in_order:
        if model._meta.db_table not in existing_tables:
            with connection.schema_editor() as editor:
                editor.create_model(model)
            existing_tables.add(model._meta.db_table)
    yield


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
    with booking_state_tables():
        booking = _build_booking()
        transition(booking, BookingStatus.CONFIRMED)
        assert booking.status == BookingStatus.CONFIRMED


@pytest.mark.django_db
def test_invalid_transition_raises_domain_error():
    with booking_state_tables():
        booking = _build_booking(status=BookingStatus.CONFIRMED)
        with pytest.raises(DomainError) as exc:
            transition(booking, BookingStatus.PENDING_REVIEW)
        assert exc.value.detail["error_code"] == "booking_transition_invalid"


@pytest.mark.django_db
def test_error_contains_no_localized_string():
    with booking_state_tables():
        booking = _build_booking(status=BookingStatus.EXPIRED)
        with pytest.raises(DomainError) as exc:
            transition(booking, BookingStatus.CONFIRMED)
        detail = exc.value.detail
        assert "error_code" in detail
        assert " " not in detail["error_code"]
