"""Tests for staff booking DRF views."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.bookings.models import Booking, BookingStatus
from apps.bookings.views import BookingViewSet
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.restaurants.models import RestaurantSettings
from tests.tenant_helpers import tenant_schema


def _seed_booking():
    customer = Customer.objects.create(
        phone="+3900076000",
        email="views@example.com",
        name="Views Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
    )


def _seed_staff():
    user = User.objects.create_user(
        username="staff_7_6",
        email="staff76@example.com",
        password="testpass123",
    )
    StaffMembership.objects.create(
        user=user,
        role=StaffMembership.ROLE_MANAGER,
        is_active=True,
    )
    return user


@pytest.mark.django_db(transaction=True)
def test_approve_endpoint_requires_auth():
    with tenant_schema("booking_views") as (_tenant, _schema_name, _domain_name):
        RestaurantSettings.objects.create()
        booking = _seed_booking()
        request = APIRequestFactory().post(f"/api/v1/bookings/{booking.id}/approve/")
        response = BookingViewSet.as_view({"post": "approve"})(request, pk=str(booking.id))
    assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_approve_endpoint_returns_updated_status():
    with tenant_schema("booking_views") as (_tenant, _schema_name, _domain_name):
        RestaurantSettings.objects.create(deposit_policy=RestaurantSettings.DEPOSIT_NEVER)
        booking = _seed_booking()
        user = _seed_staff()
        request = APIRequestFactory().post(f"/api/v1/bookings/{booking.id}/approve/")
        request.membership = StaffMembership.objects.get(user=user, is_active=True)
        request.user = user
        response = BookingViewSet.as_view({"post": "approve"})(request, pk=str(booking.id))
    assert response.status_code == 200
    assert response.data["status"] == "confirmed_without_deposit"


@pytest.mark.django_db(transaction=True)
def test_response_contains_no_localized_strings():
    with tenant_schema("booking_views") as (_tenant, _schema_name, _domain_name):
        RestaurantSettings.objects.create()
        booking = _seed_booking()
        user = _seed_staff()
        request = APIRequestFactory().get(f"/api/v1/bookings/{booking.id}/")
        request.membership = StaffMembership.objects.get(user=user, is_active=True)
        request.user = user
        response = BookingViewSet.as_view({"get": "retrieve"})(request, pk=str(booking.id))
    assert response.status_code == 200
    assert " " not in response.data["status"]


@pytest.mark.django_db(transaction=True)
def test_assign_table_without_table_returns_code_form():
    with tenant_schema("booking_views") as (_tenant, _schema_name, _domain_name):
        RestaurantSettings.objects.create()
        booking = _seed_booking()
        user = _seed_staff()
        request = APIRequestFactory().post(f"/api/v1/bookings/{booking.id}/assign-table/", {})
        request.membership = StaffMembership.objects.get(user=user, is_active=True)
        request.user = user
        response = BookingViewSet.as_view({"post": "assign_table"})(request, pk=str(booking.id))

    assert response.status_code == 400
    assert response.data["error_code"] == "validation_failed"
    assert response.data["params"]["field"] == "table"


@pytest.mark.django_db(transaction=True)
def test_patch_booking_fields_uses_staff_modify_service():
    with tenant_schema("booking_views") as (_tenant, _schema_name, _domain_name):
        RestaurantSettings.objects.create()
        booking = _seed_booking()
        user = _seed_staff()
        request = APIRequestFactory().patch(
            f"/api/v1/bookings/{booking.id}/",
            {"party_size": 4, "notes": "near window"},
            format="json",
        )
        request.membership = StaffMembership.objects.get(user=user, is_active=True)
        request.user = user
        response = BookingViewSet.as_view({"patch": "partial_update"})(
            request,
            pk=str(booking.id),
        )

        booking.refresh_from_db()
        assert response.status_code == 200
        assert booking.party_size == 4
        assert booking.notes == "near window"


@pytest.mark.django_db(transaction=True)
def test_patch_booking_status_no_show_uses_state_machine():
    with tenant_schema("booking_views") as (_tenant, _schema_name, _domain_name):
        RestaurantSettings.objects.create()
        booking = _seed_booking()
        booking.status = BookingStatus.CONFIRMED
        booking.save(update_fields=["status", "updated_at"])
        user = _seed_staff()
        request = APIRequestFactory().patch(
            f"/api/v1/bookings/{booking.id}/",
            {"status": BookingStatus.NO_SHOW},
            format="json",
        )
        request.membership = StaffMembership.objects.get(user=user, is_active=True)
        request.user = user
        response = BookingViewSet.as_view({"patch": "partial_update"})(
            request,
            pk=str(booking.id),
        )

        booking.refresh_from_db()
        assert response.status_code == 200
        assert booking.status == BookingStatus.NO_SHOW


@pytest.mark.django_db(transaction=True)
def test_patch_booking_rejects_other_direct_status_changes():
    with tenant_schema("booking_views") as (_tenant, _schema_name, _domain_name):
        RestaurantSettings.objects.create()
        booking = _seed_booking()
        user = _seed_staff()
        request = APIRequestFactory().patch(
            f"/api/v1/bookings/{booking.id}/",
            {"status": BookingStatus.CONFIRMED},
            format="json",
        )
        request.membership = StaffMembership.objects.get(user=user, is_active=True)
        request.user = user
        response = BookingViewSet.as_view({"patch": "partial_update"})(
            request,
            pk=str(booking.id),
        )

        booking.refresh_from_db()
        assert response.status_code == 400
        assert response.data["error_code"] == "validation_failed"
        assert response.data["params"]["field"] == "status"
        assert booking.status == BookingStatus.PENDING_REVIEW
