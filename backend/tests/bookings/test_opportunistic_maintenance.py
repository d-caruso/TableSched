"""Tests for opportunistic maintenance."""

from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services import opportunistic_maintenance
from apps.customers.models import Customer
from apps.payments.models import Payment, PaymentStatus
from tests.tenant_helpers import tenant_schema


def _customer() -> Customer:
    suffix = uuid4().hex[:8]
    return Customer.objects.create(
        phone=f"+390001{suffix}",
        email="maintenance@example.com",
        name="Maintenance Customer",
        locale="en",
    )


def _booking(*, status: str, payment_due_at=None) -> Booking:
    return Booking.objects.create(
        customer=_customer(),
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
        status=status,
        payment_due_at=payment_due_at,
    )


def _authorized_payment(*, created_at) -> Payment:
    booking = _booking(status=BookingStatus.PENDING_REVIEW)
    payment = Payment.objects.create(
        booking=booking,
        kind=Payment.KIND_PREAUTH,
        amount_cents=1000,
        status=PaymentStatus.AUTHORIZED,
    )
    Payment.objects.filter(pk=payment.pk).update(created_at=created_at)
    payment.refresh_from_db()
    return payment


def _clear_notification_calls(monkeypatch):
    calls = {"customer": [], "staff": []}

    monkeypatch.setattr(
        opportunistic_maintenance.notifications,
        "notify_customer",
        lambda *args, **kwargs: calls["customer"].append((args, kwargs)),
    )
    monkeypatch.setattr(
        opportunistic_maintenance.notifications,
        "notify_staff",
        lambda *args, **kwargs: calls["staff"].append((args, kwargs)),
    )
    return calls


@pytest.mark.django_db
def test_expire_pending_payment_past_due(monkeypatch):
    with tenant_schema("opportunistic_maintenance"):
        calls = _clear_notification_calls(monkeypatch)
        booking = _booking(
            status=BookingStatus.PENDING_PAYMENT,
            payment_due_at=timezone.now() - timedelta(minutes=5),
        )

        opportunistic_maintenance._expire_pending_payments()

        booking.refresh_from_db()
        assert booking.status == BookingStatus.EXPIRED
        assert len(calls["customer"]) == 1


@pytest.mark.django_db
def test_expire_pending_payment_not_yet_due(monkeypatch):
    with tenant_schema("opportunistic_maintenance"):
        calls = _clear_notification_calls(monkeypatch)
        booking = _booking(
            status=BookingStatus.PENDING_PAYMENT,
            payment_due_at=timezone.now() + timedelta(minutes=5),
        )

        opportunistic_maintenance._expire_pending_payments()

        booking.refresh_from_db()
        assert booking.status == BookingStatus.PENDING_PAYMENT
        assert calls["customer"] == []


@pytest.mark.django_db
def test_expire_authorized_deposit_old(monkeypatch):
    with tenant_schema("opportunistic_maintenance"):
        calls = _clear_notification_calls(monkeypatch)
        payment = _authorized_payment(created_at=timezone.now() - timedelta(days=7))

        opportunistic_maintenance._expire_authorized_deposits()

        payment.refresh_from_db()
        payment.booking.refresh_from_db()
        assert payment.status == PaymentStatus.FAILED
        assert payment.booking.status == BookingStatus.AUTHORIZATION_EXPIRED
        assert len(calls["staff"]) == 1


@pytest.mark.django_db
def test_opportunistic_maintenance_is_idempotent(monkeypatch):
    with tenant_schema("opportunistic_maintenance"):
        _clear_notification_calls(monkeypatch)
        booking = _booking(
            status=BookingStatus.PENDING_PAYMENT,
            payment_due_at=timezone.now() - timedelta(minutes=5),
        )

        opportunistic_maintenance._expire_pending_payments()
        opportunistic_maintenance._expire_pending_payments()

        booking.refresh_from_db()
        assert booking.status == BookingStatus.EXPIRED


@pytest.mark.django_db
def test_opportunistic_maintenance_bounded_at_200(monkeypatch):
    with tenant_schema("opportunistic_maintenance"):
        _clear_notification_calls(monkeypatch)
        for _ in range(201):
            _booking(
                status=BookingStatus.PENDING_PAYMENT,
                payment_due_at=timezone.now() - timedelta(minutes=5),
            )

        opportunistic_maintenance._expire_pending_payments()

        assert Booking.objects.filter(status=BookingStatus.EXPIRED).count() == 200
