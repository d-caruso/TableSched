"""Tests for deprecated booking and payment compatibility endpoints."""

from datetime import timedelta

import pytest
from django.urls import resolve
from django.utils import timezone
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.bookings.models import Booking, BookingStatus, BookingTableAssignment
from apps.customers.models import BookingAccessToken, Customer
from apps.memberships.models import StaffMembership
from apps.notifications import services as notification_services
from apps.payments import services as payment_services
from apps.restaurants.models import RestaurantSettings, Room, Table
from tests.tenant_helpers import tenant_schema


def _booking() -> Booking:
    customer = Customer.objects.create(
        phone="+3900199000",
        email="deprecated@example.com",
        name="Deprecated Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
        notes="original notes",
    )


def _membership() -> StaffMembership:
    user = User.objects.create_user(
        username="manager_20_1",
        email="manager201@example.com",
        password="testpass123",
    )
    return StaffMembership.objects.create(
        user=user,
        role=StaffMembership.ROLE_MANAGER,
        is_active=True,
    )


def _dispatch(method: str, path: str, *, membership=None, data=None):
    factory = APIRequestFactory()
    request = getattr(factory, method)(path, data or {}, format="json")
    if membership is not None:
        request.membership = membership
        request.user = membership.user
    match = resolve(path)
    return match.func(request, **match.kwargs)


@pytest.mark.django_db(transaction=True)
def test_legacy_booking_approve_route_still_confirms_without_deposit(monkeypatch):
    with tenant_schema("deprecated_booking_endpoints"):
        RestaurantSettings.objects.create(deposit_policy=RestaurantSettings.DEPOSIT_NEVER)
        monkeypatch.setattr(notification_services, "notify_customer", lambda *args, **kwargs: None)
        booking = _booking()
        membership = _membership()

        response = _dispatch(
            "post",
            f"/api/v1/bookings/{booking.id}/approve/",
            membership=membership,
        )
        booking.refresh_from_db()

    assert response.status_code == 200
    assert booking.status == BookingStatus.CONFIRMED_WITHOUT_DEPOSIT


@pytest.mark.django_db(transaction=True)
def test_legacy_booking_decline_route_still_records_rejection(monkeypatch):
    with tenant_schema("deprecated_booking_endpoints"):
        RestaurantSettings.objects.create()
        monkeypatch.setattr(notification_services, "notify_customer", lambda *args, **kwargs: None)
        booking = _booking()
        membership = _membership()

        response = _dispatch(
            "post",
            f"/api/v1/bookings/{booking.id}/decline/",
            membership=membership,
            data={
                "reason_code": "staff_rejection_generic",
                "staff_message": "Fully booked",
            },
        )
        booking.refresh_from_db()

    assert response.status_code == 200
    assert booking.status == BookingStatus.DECLINED
    assert booking.staff_message == "Fully booked"


@pytest.mark.django_db(transaction=True)
def test_legacy_booking_modify_route_still_updates_staff_fields(monkeypatch):
    with tenant_schema("deprecated_booking_endpoints"):
        RestaurantSettings.objects.create()
        monkeypatch.setattr(notification_services, "notify_customer", lambda *args, **kwargs: None)
        booking = _booking()
        membership = _membership()

        response = _dispatch(
            "post",
            f"/api/v1/bookings/{booking.id}/modify/",
            membership=membership,
            data={"party_size": 4, "notes": "near window"},
        )
        booking.refresh_from_db()

    assert response.status_code == 200
    assert booking.party_size == 4
    assert booking.notes == "near window"


@pytest.mark.django_db(transaction=True)
def test_legacy_booking_assign_table_route_still_replaces_assignment(monkeypatch):
    with tenant_schema("deprecated_booking_endpoints"):
        RestaurantSettings.objects.create()
        monkeypatch.setattr(notification_services, "notify_customer", lambda *args, **kwargs: None)
        booking = _booking()
        membership = _membership()
        room = Room.objects.create(name="Main")
        table = Table.objects.create(room=room, label="T1", seats=4)

        response = _dispatch(
            "post",
            f"/api/v1/bookings/{booking.id}/assign-table/",
            membership=membership,
            data={"table": str(table.id)},
        )
        booking_tables = list(BookingTableAssignment.objects.filter(booking=booking))

    assert response.status_code == 200
    assert len(booking_tables) == 1
    assert booking_tables[0].table_id == table.id


@pytest.mark.django_db(transaction=True)
def test_legacy_booking_mark_no_show_route_still_marks_no_show(monkeypatch):
    with tenant_schema("deprecated_booking_endpoints"):
        RestaurantSettings.objects.create()
        monkeypatch.setattr(notification_services, "notify_customer", lambda *args, **kwargs: None)
        booking = _booking()
        booking.status = BookingStatus.CONFIRMED
        booking.save(update_fields=["status", "updated_at"])
        membership = _membership()

        response = _dispatch(
            "post",
            f"/api/v1/bookings/{booking.id}/mark-no-show/",
            membership=membership,
        )
        booking.refresh_from_db()

    assert response.status_code == 200
    assert booking.status == BookingStatus.NO_SHOW


@pytest.mark.django_db(transaction=True)
def test_legacy_booking_confirm_without_deposit_route_still_confirms(monkeypatch):
    with tenant_schema("deprecated_booking_endpoints"):
        RestaurantSettings.objects.create()
        monkeypatch.setattr(notification_services, "notify_customer", lambda *args, **kwargs: None)
        booking = _booking()
        membership = _membership()

        response = _dispatch(
            "post",
            f"/api/v1/bookings/{booking.id}/confirm-without-deposit/",
            membership=membership,
        )
        booking.refresh_from_db()

    assert response.status_code == 200
    assert booking.status == BookingStatus.CONFIRMED_WITHOUT_DEPOSIT


@pytest.mark.django_db(transaction=True)
def test_legacy_booking_request_payment_route_still_requests_payment(monkeypatch):
    with tenant_schema("deprecated_booking_endpoints"):
        RestaurantSettings.objects.create()
        monkeypatch.setattr(notification_services, "notify_customer", lambda *args, **kwargs: None)
        monkeypatch.setattr(payment_services, "create_payment_link", lambda **kwargs: None)
        booking = _booking()
        membership = _membership()

        response = _dispatch(
            "post",
            f"/api/v1/bookings/{booking.id}/request-payment/",
            membership=membership,
        )
        booking.refresh_from_db()

    assert response.status_code == 200
    assert booking.status == BookingStatus.PENDING_PAYMENT
    assert booking.payment_due_at is not None


@pytest.mark.django_db(transaction=True)
def test_legacy_public_booking_post_route_still_supports_modify():
    with tenant_schema("deprecated_booking_endpoints"):
        RestaurantSettings.objects.create()
        booking = _booking()
        _, raw_token = BookingAccessToken.issue(booking)

        response = _dispatch(
            "post",
            f"/api/v1/public/bookings/{raw_token}/",
            data={"action": "modify", "notes": "updated from legacy post"},
        )
        booking.refresh_from_db()

    assert response.status_code == 200
    assert booking.notes == "updated from legacy post"
