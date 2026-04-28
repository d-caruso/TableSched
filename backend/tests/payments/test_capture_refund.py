"""Tests for Stripe capture, payment links, and refunds."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta
from unittest.mock import Mock

import pytest
from django.db import connection
from django.utils import timezone
import stripe as stripe_sdk

from apps.accounts.models import User
from apps.bookings.models import Booking
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.payments.models import Payment, PaymentStatus
from apps.restaurants.models import RestaurantSettings, Room, Table


@contextmanager
def capture_refund_tables() -> Iterator[None]:
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
    customer = Customer.objects.create(
        phone="+3900083000",
        email="capture@example.com",
        name="Capture Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
    )


def _payment(*, booking: Booking, status: str) -> Payment:
    return Payment.objects.create(
        booking=booking,
        kind=Payment.KIND_PREAUTH,
        stripe_payment_intent_id="pi_test",
        amount_cents=2500,
        status=status,
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


@pytest.mark.django_db
def test_capture_sets_status_captured(monkeypatch):
    with capture_refund_tables():
        booking = _booking()
        payment = _payment(booking=booking, status=PaymentStatus.AUTHORIZED)

        from apps.payments.gateways import stripe

        capture_mock = Mock(return_value=Mock())
        monkeypatch.setattr(stripe_sdk.PaymentIntent, "capture", capture_mock)

        result = stripe.capture(payment)
        payment.refresh_from_db()

        assert result.status == PaymentStatus.CAPTURED
        assert payment.status == PaymentStatus.CAPTURED
        assert capture_mock.called


@pytest.mark.django_db
def test_create_payment_link_creates_payment_record(monkeypatch):
    with capture_refund_tables():
        booking = _booking()
        settings = _settings()
        session = Mock(id="cs_123")

        from apps.payments.gateways import stripe

        create_mock = Mock(return_value=session)
        monkeypatch.setattr(stripe_sdk.checkout.Session, "create", create_mock)

        result = stripe.create_payment_link(booking=booking, settings=settings)

        payment = Payment.objects.get(booking=booking)
        assert result == payment
        assert payment.kind == Payment.KIND_LINK
        assert payment.status == PaymentStatus.PENDING
        assert payment.stripe_checkout_session_id == "cs_123"
        assert payment.expires_at is not None
        assert create_mock.call_args.kwargs["mode"] == "payment"
        assert create_mock.call_args.kwargs["metadata"]["booking_id"] == str(booking.id)


@pytest.mark.django_db
def test_refund_sets_status_refunded(monkeypatch):
    with capture_refund_tables():
        booking = _booking()
        payment = _payment(booking=booking, status=PaymentStatus.CAPTURED)

        from apps.payments.gateways import stripe

        refund_mock = Mock(return_value=Mock())
        monkeypatch.setattr(stripe_sdk.Refund, "create", refund_mock)

        result = stripe.refund(payment)
        payment.refresh_from_db()

        assert result.status == PaymentStatus.REFUNDED
        assert payment.status == PaymentStatus.REFUNDED
        assert refund_mock.called


@pytest.mark.django_db
def test_refund_on_stripe_error_sets_refund_failed(monkeypatch):
    with capture_refund_tables():
        booking = _booking()
        payment = _payment(booking=booking, status=PaymentStatus.CAPTURED)

        from apps.payments.gateways import stripe

        monkeypatch.setattr(
            stripe_sdk.Refund,
            "create",
            Mock(side_effect=stripe_sdk.error.StripeError("boom")),
        )

        result = stripe.refund(payment)
        payment.refresh_from_db()

        assert result.status == PaymentStatus.REFUND_FAILED
        assert payment.status == PaymentStatus.REFUND_FAILED
