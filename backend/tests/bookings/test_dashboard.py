"""Tests for the admin dashboard endpoint."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.bookings.models import Booking, BookingStatus
from apps.bookings.views import AdminDashboardView
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from tests.tenant_helpers import tenant_schema


def _customer(phone_suffix: str) -> Customer:
    return Customer.objects.create(
        phone=f"+3900100{phone_suffix}",
        email="dashboard@example.com",
        name="Dashboard Customer",
        locale="en",
    )


def _booking(*, status: str, created_at_offset_days: int = 0) -> Booking:
    booking = Booking.objects.create(
        customer=_customer(str(created_at_offset_days).zfill(2)),
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
        status=status,
    )
    if created_at_offset_days:
        Booking.objects.filter(pk=booking.pk).update(
            created_at=timezone.now() - timedelta(days=created_at_offset_days)
        )
        booking.refresh_from_db()
    return booking


def _membership() -> StaffMembership:
    user = User.objects.create_user(
        username="dashboard_staff",
        email="dashboard-staff@example.com",
        password="testpass123",
    )
    return StaffMembership.objects.create(
        user=user,
        role=StaffMembership.ROLE_MANAGER,
        is_active=True,
    )


@pytest.mark.django_db(transaction=True)
def test_dashboard_requires_auth():
    with tenant_schema("dashboard"):
        request = APIRequestFactory().get("/api/v1/admin/dashboard/")
        response = AdminDashboardView.as_view()(request)

        assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_dashboard_returns_counts_and_recent(monkeypatch):
    with tenant_schema("dashboard"):
        monkeypatch.setattr(
            "apps.bookings.services.opportunistic_maintenance.run_opportunistic_maintenance",
            lambda: None,
        )
        membership = _membership()
        _booking(status=BookingStatus.PENDING_REVIEW, created_at_offset_days=1)
        _booking(status=BookingStatus.CONFIRMED, created_at_offset_days=2)
        recent_booking = _booking(status=BookingStatus.DECLINED, created_at_offset_days=0)

        request = APIRequestFactory().get("/api/v1/admin/dashboard/")
        request.user = membership.user
        response = AdminDashboardView.as_view()(request)

        assert response.status_code == 200
        assert response.data["counts_by_status"][BookingStatus.PENDING_REVIEW] == 1
        assert response.data["counts_by_status"][BookingStatus.CONFIRMED] == 1
        assert response.data["counts_by_status"][BookingStatus.DECLINED] == 1
        assert response.data["recent"][0]["id"] == recent_booking.id


@pytest.mark.django_db(transaction=True)
def test_dashboard_triggers_opportunistic_maintenance(monkeypatch):
    with tenant_schema("dashboard"):
        called = {"value": False}

        def _run():
            called["value"] = True

        monkeypatch.setattr(
            "apps.bookings.services.opportunistic_maintenance.run_opportunistic_maintenance",
            _run,
        )
        membership = _membership()
        request = APIRequestFactory().get("/api/v1/admin/dashboard/")
        request.user = membership.user

        response = AdminDashboardView.as_view()(request)

        assert response.status_code == 200
        assert called["value"] is True
