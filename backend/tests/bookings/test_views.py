"""Tests for staff booking DRF views."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone

from apps.accounts.models import User
from apps.bookings.models import Booking
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.restaurants.models import RestaurantSettings, Room, Table


@contextmanager
def booking_view_tables() -> Iterator[None]:
    existing_tables = set(connection.introspection.table_names())
    models_in_order = (
        User,
        Customer,
        StaffMembership,
        Room,
        Table,
        RestaurantSettings,
        Booking,
    )
    for model in models_in_order:
        if model._meta.db_table not in existing_tables:
            with connection.schema_editor() as editor:
                editor.create_model(model)
            existing_tables.add(model._meta.db_table)
    yield


def _seed_booking():
    customer = Customer.objects.create(
        phone="+3900076000",
        email="views@example.com",
        name="Views Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
    )


def _seed_staff():
    user = User.objects.create_user(
        username="staff_7_6",
        email="staff76@example.com",
        password="testpass123",
    )
    StaffMembership.objects.create(
        user=user,
        role=StaffMembership.ROLE_MANAGER,
        is_active=True,
    )
    return user


@pytest.mark.django_db
def test_approve_endpoint_requires_auth(client):
    with booking_view_tables():
        RestaurantSettings.objects.create()
        booking = _seed_booking()
        response = client.post(
            f"/api/v1/bookings/{booking.id}/approve/",
            HTTP_HOST="localhost",
        )
    assert response.status_code == 403


@pytest.mark.django_db
def test_approve_endpoint_returns_updated_status(client):
    with booking_view_tables():
        RestaurantSettings.objects.create(deposit_policy=RestaurantSettings.DEPOSIT_NEVER)
        booking = _seed_booking()
        user = _seed_staff()
        client.force_login(user)
        response = client.post(
            f"/api/v1/bookings/{booking.id}/approve/",
            HTTP_HOST="localhost",
        )
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed_without_deposit"


@pytest.mark.django_db
def test_response_contains_no_localized_strings(client):
    with booking_view_tables():
        RestaurantSettings.objects.create()
        booking = _seed_booking()
        user = _seed_staff()
        client.force_login(user)
        response = client.get(
            f"/api/v1/bookings/{booking.id}/",
            HTTP_HOST="localhost",
        )
    assert response.status_code == 200
    assert " " not in response.json()["status"]
