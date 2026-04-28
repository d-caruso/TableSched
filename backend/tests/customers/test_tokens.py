"""Tests for customer booking access tokens."""

import hmac
from datetime import timedelta

import pytest
from django.utils import timezone

from apps.bookings.models import Booking
from apps.customers.models import BookingAccessToken, Customer, hash_token
from tests.tenant_helpers import tenant_schema


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
    with tenant_schema("customer_tokens"):
        booking = _build_booking()
        token, raw = BookingAccessToken.issue(booking)

        assert token.token_hash == hash_token(raw)
        assert raw not in token.token_hash


@pytest.mark.django_db
def test_token_expires_7_days_after_booking():
    with tenant_schema("customer_tokens"):
        booking = _build_booking()
        token, _ = BookingAccessToken.issue(booking)

        assert token.expires_at - booking.starts_at == timedelta(days=7)


@pytest.mark.django_db
def test_token_hash_uses_constant_time_compare():
    with tenant_schema("customer_tokens"):
        booking = _build_booking()
        token, raw = BookingAccessToken.issue(booking)

        assert hmac.compare_digest(hash_token(raw), token.token_hash)
        assert not hmac.compare_digest(hash_token("wrong"), token.token_hash)
