"""Tests for tenant closed-day endpoints."""

from datetime import date
from uuid import uuid4

import pytest
from django.urls import resolve
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.memberships.models import StaffMembership
from apps.restaurants.models import ClosedDay
from apps.restaurants.views import ClosedDayDetailView, ClosedDayListCreateView
from tests.tenant_helpers import tenant_schema


def _membership(role: str) -> StaffMembership:
    suffix = uuid4().hex[:8]
    user = User.objects.create_user(
        username=f"{role}_closed_{suffix}",
        email=f"{role}-closed-{suffix}@example.com",
    )
    return StaffMembership.objects.create(user=user, role=role, is_active=True)


def _request(method: str, path: str, membership: StaffMembership, data=None):
    factory = APIRequestFactory()
    request = getattr(factory, method)(path, data or {}, format="json")
    request.membership = membership
    request.user = membership.user
    return request


@pytest.mark.django_db(transaction=True)
def test_staff_can_list_closed_days():
    with tenant_schema("closed_days_endpoint"):
        closed_day = ClosedDay.objects.create(
            date=date(2026, 1, 1),
            reason_code="holiday",
        )
        membership = _membership(StaffMembership.ROLE_STAFF)
        request = _request("get", "/api/v1/restaurant/closed-days/", membership)

        response = ClosedDayListCreateView.as_view()(request)

        assert response.status_code == 200
        assert response.data[0]["id"] == str(closed_day.id)
        assert response.data[0]["date"] == "2026-01-01"


@pytest.mark.django_db(transaction=True)
def test_manager_can_create_closed_day():
    with tenant_schema("closed_days_endpoint"):
        membership = _membership(StaffMembership.ROLE_MANAGER)
        request = _request(
            "post",
            "/api/v1/restaurant/closed-days/",
            membership,
            {"date": "2026-01-01", "reason_code": "holiday"},
        )

        response = ClosedDayListCreateView.as_view()(request)

        assert response.status_code == 201
        assert ClosedDay.objects.filter(date=date(2026, 1, 1)).exists()


@pytest.mark.django_db(transaction=True)
def test_manager_can_update_and_delete_closed_day():
    with tenant_schema("closed_days_endpoint"):
        closed_day = ClosedDay.objects.create(date=date(2026, 1, 1), reason_code="holiday")
        membership = _membership(StaffMembership.ROLE_MANAGER)
        patch_request = _request(
            "patch",
            f"/api/v1/restaurant/closed-days/{closed_day.id}/",
            membership,
            {"reason_code": "private_event"},
        )
        delete_request = _request(
            "delete",
            f"/api/v1/restaurant/closed-days/{closed_day.id}/",
            membership,
        )

        patch_response = ClosedDayDetailView.as_view()(patch_request, pk=str(closed_day.id))
        closed_day.refresh_from_db()
        delete_response = ClosedDayDetailView.as_view()(delete_request, pk=str(closed_day.id))

        assert patch_response.status_code == 200
        assert closed_day.reason_code == "private_event"
        assert delete_response.status_code == 204
        assert not ClosedDay.objects.filter(pk=closed_day.pk).exists()


@pytest.mark.django_db(transaction=True)
def test_closed_day_rejects_duplicate_date():
    with tenant_schema("closed_days_endpoint"):
        ClosedDay.objects.create(date=date(2026, 1, 1), reason_code="holiday")
        membership = _membership(StaffMembership.ROLE_MANAGER)
        request = _request(
            "post",
            "/api/v1/restaurant/closed-days/",
            membership,
            {"date": "2026-01-01", "reason_code": "holiday"},
        )

        response = ClosedDayListCreateView.as_view()(request)

        assert response.status_code == 400
        assert response.data["error_code"] == "validation_failed"


def test_closed_day_routes_resolve():
    collection = resolve("/api/v1/restaurant/closed-days/")
    detail = resolve("/api/v1/restaurant/closed-days/00000000-0000-0000-0000-000000000000/")

    assert collection.url_name == "closed-days"
    assert detail.url_name == "closed-day-detail"
