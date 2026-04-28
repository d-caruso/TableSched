"""Tests for Stripe pre-authorization flow."""

from datetime import timedelta
from unittest.mock import Mock
from django.db import connection

import pytest
from django.utils import timezone
import stripe as stripe_sdk

from apps.bookings.models import Booking, BookingStatus
from apps.customers.models import Customer
from apps.payments.models import Payment, PaymentStatus
from apps.restaurants.models import RestaurantSettings
from tests.payments.helpers import payment_tenant


def _booking() -> Booking:
    customer = Customer.objects.create(
        phone="+3900082000",
        email="preauth@example.com",
        name="Preauth Customer",
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


@pytest.mark.django_db
def test_create_preauth_creates_payment_record(monkeypatch):
    with payment_tenant():
        booking = _booking()
        settings = _settings()
        intent = Mock(id="pi_123", client_secret="secret_123")

        from apps.payments.gateways import stripe

        create_mock = Mock(return_value=intent)
        monkeypatch.setattr(stripe_sdk.PaymentIntent, "create", create_mock)

        result = stripe.create_preauth(booking=booking, settings=settings)

        payment = Payment.objects.get(booking=booking)
        assert result is intent
        assert payment.kind == Payment.KIND_PREAUTH
        assert payment.status == PaymentStatus.PENDING
        assert payment.stripe_payment_intent_id == "pi_123"
        assert create_mock.call_args.kwargs["capture_method"] == "manual"
        assert create_mock.call_args.kwargs["metadata"]["tenant_schema"] == connection.schema_name
        assert create_mock.call_args.kwargs["metadata"]["booking_id"] == str(booking.id)


@pytest.mark.django_db
def test_preauth_metadata_contains_tenant_schema(monkeypatch):
    with payment_tenant():
        booking = _booking()
        settings = _settings()
        intent = Mock(id="pi_456", client_secret="secret_456")

        from apps.payments.gateways import stripe

        create_mock = Mock(return_value=intent)
        monkeypatch.setattr(stripe_sdk.PaymentIntent, "create", create_mock)

        stripe.create_preauth(booking=booking, settings=settings)

        call_kwargs = create_mock.call_args.kwargs
        assert call_kwargs["capture_method"] == "manual"
        assert call_kwargs["metadata"]["tenant_schema"] == connection.schema_name
        assert call_kwargs["metadata"]["booking_id"] == str(booking.id)


@pytest.mark.django_db
def test_booking_stays_pending_review_after_preauth(monkeypatch):
    with payment_tenant():
        booking = _booking()
        settings = _settings()
        intent = Mock(id="pi_789", client_secret="secret_789")

        from apps.payments.gateways import stripe

        create_mock = Mock(return_value=intent)
        monkeypatch.setattr(stripe_sdk.PaymentIntent, "create", create_mock)

        stripe.create_preauth(booking=booking, settings=settings)
        booking.refresh_from_db()

        assert booking.status == BookingStatus.PENDING_REVIEW
