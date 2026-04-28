"""Token endpoint hardening regressions."""

from datetime import timedelta
import logging

import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.bookings.models import Booking
from apps.bookings.views_customer import CustomerBookingView
from apps.customers.models import BookingAccessToken, Customer, verify_token
from tests.tenant_helpers import tenant_schema


def _booking(*, starts_at):
    customer = Customer.objects.create(
        phone="+3900012345",
        email="token@example.com",
        name="Token Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=starts_at,
        party_size=2,
    )


@pytest.mark.django_db(transaction=True)
def test_verify_token_correct():
    with tenant_schema("token_hardening"):
        booking = _booking(starts_at=timezone.now() + timedelta(days=2))
        token, raw = BookingAccessToken.issue(booking)

    assert verify_token(raw, token.token_hash) is True


@pytest.mark.django_db(transaction=True)
def test_verify_token_wrong():
    with tenant_schema("token_hardening"):
        booking = _booking(starts_at=timezone.now() + timedelta(days=2))
        token, _raw = BookingAccessToken.issue(booking)

    assert verify_token("wrongtoken", token.token_hash) is False


@pytest.mark.django_db(transaction=True)
def test_public_booking_endpoint_is_rate_limited():
    with tenant_schema("token_hardening") as (_tenant, _schema_name, _domain_name):
        booking = _booking(starts_at=timezone.now() + timedelta(days=2))
        _, raw = BookingAccessToken.issue(booking)
        factory = APIRequestFactory()

        response = None
        for _ in range(31):
            request = factory.get(f"/api/v1/public/bookings/{raw}/")
            request.META["REMOTE_ADDR"] = "127.0.0.1"
            response = CustomerBookingView.as_view()(request, raw_token=raw)
            if response.status_code == 429:
                break

    assert response is not None
    assert response.status_code == 429


@pytest.mark.django_db(transaction=True)
def test_raw_token_is_not_logged(caplog):
    with tenant_schema("token_hardening"):
        booking = _booking(starts_at=timezone.now() + timedelta(days=2))
        _, raw = BookingAccessToken.issue(booking)
        request = APIRequestFactory().get(f"/api/v1/public/bookings/{raw}/")
        request.META["REMOTE_ADDR"] = "127.0.0.2"

        with caplog.at_level(logging.WARNING):
            response = CustomerBookingView.as_view()(request, raw_token=raw)

    assert response.status_code == 200
    assert raw not in caplog.text
