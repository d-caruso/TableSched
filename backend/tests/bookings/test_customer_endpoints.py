"""Tests for token-authenticated customer booking endpoints."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.bookings.models import Booking
from apps.bookings.views_customer import CustomerBookingView
from apps.customers.models import BookingAccessToken, Customer
from apps.restaurants.models import RestaurantSettings
from tests.tenant_helpers import tenant_schema


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


@pytest.mark.django_db(transaction=True)
def test_get_booking_with_valid_token():
    with tenant_schema("customer_endpoints"):
        booking = _create_booking(timezone.now() + timedelta(days=2))
        _, raw_token = BookingAccessToken.issue(booking)
        request = APIRequestFactory().get(f"/api/v1/public/bookings/{raw_token}/")
        response = CustomerBookingView.as_view()(request, raw_token=raw_token)

    assert response.status_code == 200
    payload = response.data
    assert payload["id"] == str(booking.id)
    assert payload["status"] == "pending_review"
    assert "staff_message" not in payload
    assert "decided_by" not in payload


@pytest.mark.django_db(transaction=True)
def test_invalid_token_returns_404():
    with tenant_schema("customer_endpoints"):
        request = APIRequestFactory().get("/api/v1/public/bookings/badtoken/")
        response = CustomerBookingView.as_view()(request, raw_token="badtoken")

    assert response.status_code == 404
    payload = response.data
    assert payload["error_code"] == "token_invalid"


@pytest.mark.django_db(transaction=True)
def test_expired_token_returns_410():
    with tenant_schema("customer_endpoints"):
        booking = _create_booking(timezone.now() - timedelta(days=8))
        _, raw_token = BookingAccessToken.issue(booking)
        request = APIRequestFactory().get(f"/api/v1/public/bookings/{raw_token}/")
        response = CustomerBookingView.as_view()(request, raw_token=raw_token)

    assert response.status_code == 410
    payload = response.data
    assert payload["error_code"] == "token_expired"


@pytest.mark.django_db(transaction=True)
def test_cancel_booking_via_token():
    with tenant_schema("customer_endpoints"):
        RestaurantSettings.objects.create()
        booking = _create_booking(timezone.now() + timedelta(days=2))
        _, raw_token = BookingAccessToken.issue(booking)
        request = APIRequestFactory().post(
            f"/api/v1/public/bookings/{raw_token}/",
            {"action": "cancel"},
            format="json",
        )
        response = CustomerBookingView.as_view()(request, raw_token=raw_token)
        booking.refresh_from_db()

    assert response.status_code == 200
    assert booking.status == "cancelled_by_customer"


@pytest.mark.django_db(transaction=True)
def test_response_contains_code_strings():
    with tenant_schema("customer_endpoints"):
        _booking = _create_booking(timezone.now() + timedelta(days=2))
        _, raw_token = BookingAccessToken.issue(_booking)
        request = APIRequestFactory().get(f"/api/v1/public/bookings/{raw_token}/")
        response = CustomerBookingView.as_view()(request, raw_token=raw_token)

    assert response.status_code == 200
    payload = response.data
    assert " " not in payload["status"]
