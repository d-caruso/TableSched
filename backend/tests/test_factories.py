"""Sanity checks for shared fixtures and factories."""

from __future__ import annotations

import pytest


@pytest.mark.django_db(transaction=True)
def test_tenant_fixture_exposes_domain(tenant):
    assert tenant.schema_name
    assert tenant.domain.endswith(".localhost")


@pytest.mark.django_db(transaction=True)
def test_staff_and_manager_clients_are_authenticated(staff_client, manager_client):
    assert staff_client.session.get("_auth_user_id")
    assert manager_client.session.get("_auth_user_id")


@pytest.mark.django_db(transaction=True)
def test_core_factories_create_related_objects(customer, booking, payment, restaurant_settings, room, table, walkin, booking_access_token):
    assert booking.customer_id == customer.id
    assert payment.booking_id == booking.id
    assert restaurant_settings.pk is not None
    assert room.pk is not None
    assert table.room_id == room.id
    assert walkin.table_id == table.id
    assert booking_access_token.booking_id == booking.id
