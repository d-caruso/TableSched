"""Tests for the manual payment refund endpoint."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta
from uuid import uuid4
from unittest.mock import Mock

import pytest
from django.db import connection
from django.utils import timezone
import stripe as stripe_sdk
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.bookings.models import Booking
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.payments.models import Payment, PaymentStatus
from apps.payments.views import PaymentRefundView
from apps.restaurants.models import RestaurantSettings, Room, Table


@contextmanager
def refund_tables() -> Iterator[None]:
    existing_tables = set(connection.introspection.table_names())
    models_in_order = (
        User,
        Customer,
        StaffMembership,
        Room,
        Table,
        RestaurantSettings,
        Booking,
        Payment,
    )
    for model in models_in_order:
        if model._meta.db_table not in existing_tables:
            with connection.schema_editor() as editor:
                editor.create_model(model)
            existing_tables.add(model._meta.db_table)
    yield


def _booking() -> Booking:
    suffix = uuid4().hex[:8]
    customer = Customer.objects.create(
        phone=f"+3900086{suffix}",
        email=f"refund-{suffix}@example.com",
        name="Refund Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
    )


def _settings() -> RestaurantSettings:
    return RestaurantSettings.objects.create(
        deposit_policy=RestaurantSettings.DEPOSIT_ALWAYS,
        deposit_party_threshold=None,
        deposit_amount_cents=2500,
        near_term_threshold_hours=48,
        long_term_payment_window_hours=24,
        cancellation_cutoff_hours=24,
        booking_cutoff_minutes=5,
        advance_booking_days=90,
    )


def _payment(*, booking: Booking) -> Payment:
    return Payment.objects.create(
        booking=booking,
        kind=Payment.KIND_PREAUTH,
        stripe_payment_intent_id="pi_refund",
        amount_cents=2500,
        currency="eur",
        status=PaymentStatus.CAPTURED,
    )


def _manager_membership() -> StaffMembership:
    suffix = uuid4().hex[:8]
    user = User.objects.create_user(
        username=f"manager_8_6_{suffix}",
        email=f"manager86-{suffix}@example.com",
        password="testpass123",
    )
    return StaffMembership.objects.create(
        user=user,
        role=StaffMembership.ROLE_MANAGER,
        is_active=True,
    )


def _staff_membership() -> StaffMembership:
    suffix = uuid4().hex[:8]
    user = User.objects.create_user(
        username=f"staff_8_6_{suffix}",
        email=f"staff86-{suffix}@example.com",
        password="testpass123",
    )
    return StaffMembership.objects.create(
        user=user,
        role=StaffMembership.ROLE_STAFF,
        is_active=True,
    )


@pytest.mark.django_db(transaction=True)
def test_refund_requires_manager_role():
    with refund_tables():
        _settings()
        booking = _booking()
        payment = _payment(booking=booking)
        membership = _staff_membership()
        request = APIRequestFactory().post(f"/api/v1/payments/{payment.id}/refund/")
        request.membership = membership
        request.user = membership.user
        response = PaymentRefundView.as_view()(request, pk=str(payment.id))

    assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_refund_succeeds_for_manager(monkeypatch):
    with refund_tables():
        _settings()
        booking = _booking()
        payment = _payment(booking=booking)
        membership = _manager_membership()
        request = APIRequestFactory().post(f"/api/v1/payments/{payment.id}/refund/")
        request.membership = membership
        request.user = membership.user

        refund_mock = Mock(return_value=Mock())
        monkeypatch.setattr(stripe_sdk.Refund, "create", refund_mock)

        response = PaymentRefundView.as_view()(request, pk=str(payment.id))
        payment.refresh_from_db()

    assert response.status_code == 200
    assert payment.status == PaymentStatus.REFUNDED
    assert refund_mock.called
