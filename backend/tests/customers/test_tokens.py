"""Tests for customer booking access tokens."""

import hmac
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone

from apps.bookings.models import Booking
from apps.customers.models import BookingAccessToken, Customer, hash_token
from apps.memberships.models import StaffMembership


@contextmanager
def token_related_tables() -> Iterator[None]:
    existing_tables = set(connection.introspection.table_names())
    models_in_order = (Customer, StaffMembership, Booking, BookingAccessToken)

    for model in models_in_order:
        if model._meta.db_table not in existing_tables:
            with connection.schema_editor() as editor:
                editor.create_model(model)
            existing_tables.add(model._meta.db_table)
    yield


def _build_booking() -> Booking:
    customer = Customer.objects.create(
        phone="+3900000001",
        email="guest@example.com",
        name="Guest",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=3),
        party_size=2,
    )


@pytest.mark.django_db
def test_token_is_hashed():
    with token_related_tables():
        booking = _build_booking()
        token, raw = BookingAccessToken.issue(booking)

        assert token.token_hash == hash_token(raw)
        assert raw not in token.token_hash


@pytest.mark.django_db
def test_token_expires_7_days_after_booking():
    with token_related_tables():
        booking = _build_booking()
        token, _ = BookingAccessToken.issue(booking)

        assert token.expires_at - booking.starts_at == timedelta(days=7)


@pytest.mark.django_db
def test_token_hash_uses_constant_time_compare():
    with token_related_tables():
        booking = _build_booking()
        token, raw = BookingAccessToken.issue(booking)

        assert hmac.compare_digest(hash_token(raw), token.token_hash)
        assert not hmac.compare_digest(hash_token("wrong"), token.token_hash)
