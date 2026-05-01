"""Tests for booking decision resource endpoints."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.bookings.models import Booking
from apps.bookings.views import BookingViewSet
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.restaurants.models import RestaurantSettings
from tests.tenant_helpers import tenant_schema


def _booking() -> Booking:
    customer = Customer.objects.create(
        phone="+3900182000",
        email="decisions@example.com",
        name="Decision Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
    )


def _membership() -> StaffMembership:
    user = User.objects.create_user(username="staff18_2", email="staff182@example.com")
    return StaffMembership.objects.create(user=user, role=StaffMembership.ROLE_MANAGER)


def _request(method: str, booking: Booking, membership: StaffMembership, data=None):
    factory = APIRequestFactory()
    request = getattr(factory, method)(
        f"/api/v1/bookings/{booking.id}/decisions/",
        data or {},
        format="json",
    )
    request.membership = membership
    request.user = membership.user
    return request


@pytest.mark.django_db(transaction=True)
def test_post_approved_decision_uses_approve_service():
    with tenant_schema("booking_decisions"):
        RestaurantSettings.objects.create(deposit_policy=RestaurantSettings.DEPOSIT_NEVER)
        booking = _booking()
        membership = _membership()
        request = _request("post", booking, membership, {"outcome": "approved"})

        response = BookingViewSet.as_view({"post": "decisions"})(request, pk=str(booking.id))

        booking.refresh_from_db()
        assert response.status_code == 201
        assert response.data["status"] == "confirmed_without_deposit"
        assert booking.decided_by_id == membership.id


@pytest.mark.django_db(transaction=True)
def test_post_declined_decision_accepts_reason_and_staff_message():
    with tenant_schema("booking_decisions"):
        RestaurantSettings.objects.create()
        booking = _booking()
        membership = _membership()
        request = _request(
            "post",
            booking,
            membership,
            {
                "outcome": "declined",
                "reason_code": "staff_rejection_generic",
                "staff_message": "Fully booked",
            },
        )

        response = BookingViewSet.as_view({"post": "decisions"})(request, pk=str(booking.id))

        booking.refresh_from_db()
        assert response.status_code == 201
        assert response.data["status"] == "declined"
        assert response.data["staff_message"] == "Fully booked"
        assert booking.staff_message == "Fully booked"


@pytest.mark.django_db(transaction=True)
def test_post_decision_rejects_invalid_outcome():
    with tenant_schema("booking_decisions"):
        RestaurantSettings.objects.create()
        booking = _booking()
        membership = _membership()
        request = _request("post", booking, membership, {"outcome": "confirmed"})

        response = BookingViewSet.as_view({"post": "decisions"})(request, pk=str(booking.id))

        assert response.status_code == 400


@pytest.mark.django_db(transaction=True)
def test_get_decisions_returns_current_decision_state():
    with tenant_schema("booking_decisions"):
        RestaurantSettings.objects.create(deposit_policy=RestaurantSettings.DEPOSIT_NEVER)
        booking = _booking()
        membership = _membership()
        post_request = _request("post", booking, membership, {"outcome": "approved"})
        BookingViewSet.as_view({"post": "decisions"})(post_request, pk=str(booking.id))

        get_request = _request("get", booking, membership)
        response = BookingViewSet.as_view({"get": "decisions"})(
            get_request,
            pk=str(booking.id),
        )

        assert response.status_code == 200
        assert response.data["booking"] == str(booking.id)
        assert response.data["status"] == "confirmed_without_deposit"
        assert response.data["decided_by"] == str(membership.id)
