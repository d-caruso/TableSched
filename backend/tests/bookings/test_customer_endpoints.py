"""Tests for token-authenticated customer booking endpoints."""

from datetime import time, timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.bookings.models import Booking
from apps.bookings.views_customer import CustomerBookingView
from apps.customers.models import BookingAccessToken, Customer
from apps.restaurants.models import OpeningHours, RestaurantSettings
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


def _future_slot(days: int = 2):
    return (timezone.now() + timedelta(days=days)).replace(
        hour=19,
        minute=0,
        second=0,
        microsecond=0,
    )


def _open_for(slot) -> None:
    OpeningHours.objects.create(
        weekday=slot.weekday(),
        opens_at=time(0, 0),
        closes_at=time(23, 59),
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
def test_patch_booking_via_token_modifies_customer_editable_fields():
    with tenant_schema("customer_endpoints"):
        RestaurantSettings.objects.create()
        starts_at = _future_slot()
        new_starts_at = _future_slot(days=3)
        _open_for(new_starts_at)
        booking = _create_booking(starts_at)
        _, raw_token = BookingAccessToken.issue(booking)
        request = APIRequestFactory().patch(
            f"/api/v1/public/bookings/{raw_token}/",
            {
                "starts_at": new_starts_at.isoformat(),
                "party_size": 4,
                "notes": "near bar",
            },
            format="json",
        )

        response = CustomerBookingView.as_view()(request, raw_token=raw_token)
        booking.refresh_from_db()

    assert response.status_code == 200
    assert booking.starts_at == new_starts_at
    assert booking.party_size == 4
    assert booking.notes == "near bar"
    assert response.data["party_size"] == 4


@pytest.mark.django_db(transaction=True)
def test_delete_booking_via_token_cancels_customer_booking():
    with tenant_schema("customer_endpoints"):
        RestaurantSettings.objects.create()
        booking = _create_booking(_future_slot())
        _, raw_token = BookingAccessToken.issue(booking)
        request = APIRequestFactory().delete(f"/api/v1/public/bookings/{raw_token}/")

        response = CustomerBookingView.as_view()(request, raw_token=raw_token)
        booking.refresh_from_db()

    assert response.status_code == 200
    assert booking.status == "cancelled_by_customer"
    assert response.data["status"] == "cancelled_by_customer"


@pytest.mark.django_db(transaction=True)
def test_patch_booking_via_token_rejects_unsupported_fields():
    with tenant_schema("customer_endpoints"):
        RestaurantSettings.objects.create()
        booking = _create_booking(_future_slot())
        _, raw_token = BookingAccessToken.issue(booking)
        request = APIRequestFactory().patch(
            f"/api/v1/public/bookings/{raw_token}/",
            {"status": "cancelled_by_customer"},
            format="json",
        )

        response = CustomerBookingView.as_view()(request, raw_token=raw_token)

    assert response.status_code == 400
    assert response.data["error_code"] == "validation_failed"
    assert response.data["params"]["field"] == "status"


@pytest.mark.django_db(transaction=True)
def test_patch_booking_via_invalid_token_returns_404():
    with tenant_schema("customer_endpoints"):
        request = APIRequestFactory().patch(
            "/api/v1/public/bookings/badtoken/",
            {"notes": "updated"},
            format="json",
        )
        response = CustomerBookingView.as_view()(request, raw_token="badtoken")

    assert response.status_code == 404
    assert response.data["error_code"] == "token_invalid"


@pytest.mark.django_db(transaction=True)
def test_delete_booking_via_expired_token_returns_410():
    with tenant_schema("customer_endpoints"):
        RestaurantSettings.objects.create()
        booking = _create_booking(timezone.now() - timedelta(days=8))
        _, raw_token = BookingAccessToken.issue(booking)
        request = APIRequestFactory().delete(f"/api/v1/public/bookings/{raw_token}/")

        response = CustomerBookingView.as_view()(request, raw_token=raw_token)

    assert response.status_code == 410
    assert response.data["error_code"] == "token_expired"


@pytest.mark.django_db(transaction=True)
def test_patch_booking_via_token_is_throttled():
    with tenant_schema("customer_endpoints"):
        RestaurantSettings.objects.create()
        booking = _create_booking(_future_slot())
        _, raw_token = BookingAccessToken.issue(booking)
        factory = APIRequestFactory()
        response = None

        for _ in range(31):
            request = factory.patch(
                f"/api/v1/public/bookings/{raw_token}/",
                {"notes": "updated"},
                format="json",
            )
            request.META["REMOTE_ADDR"] = "127.0.18.5"
            response = CustomerBookingView.as_view()(request, raw_token=raw_token)
            if response.status_code == 429:
                break

    assert response is not None
    assert response.status_code == 429


@pytest.mark.django_db(transaction=True)
def test_token_flow_issue_use_expire_reject():
    with tenant_schema("customer_endpoints"):
        booking = _create_booking(timezone.now() + timedelta(days=2))
        token, raw_token = BookingAccessToken.issue(booking)

        request = APIRequestFactory().get(f"/api/v1/public/bookings/{raw_token}/")
        response = CustomerBookingView.as_view()(request, raw_token=raw_token)
        assert response.status_code == 200

        BookingAccessToken.objects.filter(pk=token.pk).update(
            expires_at=timezone.now() - timedelta(seconds=1)
        )

        expired_request = APIRequestFactory().get(f"/api/v1/public/bookings/{raw_token}/")
        expired_response = CustomerBookingView.as_view()(expired_request, raw_token=raw_token)

    assert expired_response.status_code == 410
    assert expired_response.data["error_code"] == "token_expired"
    assert response.data["id"] == str(booking.id)


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
