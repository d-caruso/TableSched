"""Tests for staff booking actions service."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone

from apps.accounts.models import User
from apps.bookings.models import Booking
from apps.bookings.services.staff import approve, decline
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.restaurants.models import RestaurantSettings, Room, Table


@contextmanager
def staff_action_tables() -> Iterator[None]:
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


def _membership() -> StaffMembership:
    user = User.objects.create_user(username="staff7_4", email="staff74@example.com", password="x")
    return StaffMembership.objects.create(user=user, role=StaffMembership.ROLE_MANAGER, is_active=True)


def _booking() -> Booking:
    customer = Customer.objects.create(
        phone="+3900074000",
        email="staff-actions@example.com",
        name="Staff Actions",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
    )


def _settings(**overrides) -> RestaurantSettings:
    defaults = {
        "deposit_policy": RestaurantSettings.DEPOSIT_NEVER,
        "deposit_party_threshold": None,
        "deposit_amount_cents": 500,
        "near_term_threshold_hours": 48,
        "long_term_payment_window_hours": 24,
        "cancellation_cutoff_hours": 24,
        "booking_cutoff_minutes": 5,
        "advance_booking_days": 90,
    }
    defaults.update(overrides)
    return RestaurantSettings.objects.create(**defaults)


@pytest.mark.django_db
def test_approve_no_deposit_confirms_without_deposit():
    with staff_action_tables():
        booking = _booking()
        membership = _membership()
        settings = _settings(deposit_policy=RestaurantSettings.DEPOSIT_NEVER)

        approve(booking, by_membership=membership, settings=settings)
        booking.refresh_from_db()

        assert booking.status == "confirmed_without_deposit"


@pytest.mark.django_db
def test_approve_with_authorized_payment_captures_and_confirms(monkeypatch):
    with staff_action_tables():
        booking = _booking()
        membership = _membership()
        settings = _settings(deposit_policy=RestaurantSettings.DEPOSIT_ALWAYS)

        from apps.payments import services as payments

        payment = {"id": "auth_1"}
        captured = {"called": False}

        def _get_authorized_payment(*, booking):
            _ = booking
            return payment

        def _capture(value):
            assert value is payment
            captured["called"] = True

        monkeypatch.setattr(payments, "get_authorized_payment", _get_authorized_payment)
        monkeypatch.setattr(payments, "capture", _capture)

        approve(booking, by_membership=membership, settings=settings)
        booking.refresh_from_db()

        assert captured["called"] is True
        assert booking.status == "confirmed"


@pytest.mark.django_db
def test_decline_cancels_authorization(monkeypatch):
    with staff_action_tables():
        booking = _booking()
        membership = _membership()

        from apps.payments import services as payments

        payment = {"id": "auth_2"}
        cancelled = {"called": False}

        def _get_authorized_payment(*, booking):
            _ = booking
            return payment

        def _cancel_authorization(value):
            assert value is payment
            cancelled["called"] = True

        monkeypatch.setattr(payments, "get_authorized_payment", _get_authorized_payment)
        monkeypatch.setattr(payments, "cancel_authorization", _cancel_authorization)

        decline(booking, by_membership=membership, reason_code="staff_rejection_generic")
        booking.refresh_from_db()

        assert cancelled["called"] is True
        assert booking.status == "declined"


@pytest.mark.django_db
def test_decline_staff_message_is_passthrough():
    with staff_action_tables():
        booking = _booking()
        membership = _membership()

        decline(
            booking,
            by_membership=membership,
            reason_code="staff_rejection_generic",
            staff_message="Siamo al completo",
        )
        booking.refresh_from_db()

        assert booking.staff_message == "Siamo al completo"
