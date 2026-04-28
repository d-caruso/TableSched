"""Tests for token-authenticated customer booking endpoints."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone

from apps.bookings.models import Booking
from apps.customers.models import BookingAccessToken, Customer
from apps.memberships.models import StaffMembership


@contextmanager
def endpoint_tables() -> Iterator[None]:
    existing_tables = set(connection.introspection.table_names())
    models_in_order = (Customer, StaffMembership, Booking, BookingAccessToken)

    for model in models_in_order:
        if model._meta.db_table not in existing_tables:
            with connection.schema_editor() as editor:
                editor.create_model(model)
            existing_tables.add(model._meta.db_table)
    yield


def _create_booking(starts_at):
    customer = Customer.objects.create(
        phone="+3900001234",
        email="guest@example.com",
        name="Guest",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=starts_at,
        party_size=2,
        notes="window table",
    )


@pytest.mark.django_db
def test_get_booking_with_valid_token(client):
    with endpoint_tables():
        booking = _create_booking(timezone.now() + timedelta(days=2))
        _, raw_token = BookingAccessToken.issue(booking)
        response = client.get(f"/api/v1/public/bookings/{raw_token}/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(booking.id)
    assert payload["status"] == "pending_review"
    assert "staff_message" not in payload
    assert "decided_by" not in payload


@pytest.mark.django_db
def test_invalid_token_returns_404(client):
    with endpoint_tables():
        response = client.get("/api/v1/public/bookings/badtoken/")

    assert response.status_code == 404
    payload = response.json()
    assert payload["error_code"] == "token_invalid"


@pytest.mark.django_db
def test_expired_token_returns_410(client):
    with endpoint_tables():
        booking = _create_booking(timezone.now() - timedelta(days=8))
        _, raw_token = BookingAccessToken.issue(booking)
        response = client.get(f"/api/v1/public/bookings/{raw_token}/")

    assert response.status_code == 410
    payload = response.json()
    assert payload["error_code"] == "token_expired"


@pytest.mark.django_db
def test_cancel_booking_via_token(client):
    with endpoint_tables():
        booking = _create_booking(timezone.now() + timedelta(days=2))
        _, raw_token = BookingAccessToken.issue(booking)
        response = client.post(
            f"/api/v1/public/bookings/{raw_token}/",
            {"action": "cancel"},
            content_type="application/json",
        )
        booking.refresh_from_db()

    assert response.status_code == 200
    assert booking.status == "cancelled_by_customer"


@pytest.mark.django_db
def test_response_contains_code_strings(client):
    with endpoint_tables():
        _booking = _create_booking(timezone.now() + timedelta(days=2))
        _, raw_token = BookingAccessToken.issue(_booking)
        response = client.get(f"/api/v1/public/bookings/{raw_token}/")

    assert response.status_code == 200
    payload = response.json()
    assert " " not in payload["status"]
