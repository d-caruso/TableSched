"""Tests for tenant opening-window endpoints."""

from datetime import time
from uuid import uuid4

import pytest
from django.urls import resolve
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.memberships.models import StaffMembership
from apps.restaurants.models import OpeningHours
from apps.restaurants.views import OpeningWindowDetailView, OpeningWindowListCreateView
from tests.tenant_helpers import tenant_schema


def _membership(role: str) -> StaffMembership:
    suffix = uuid4().hex[:8]
    user = User.objects.create_user(
        username=f"{role}_opening_{suffix}",
        email=f"{role}-opening-{suffix}@example.com",
    )
    return StaffMembership.objects.create(user=user, role=role, is_active=True)


def _request(method: str, path: str, membership: StaffMembership, data=None):
    factory = APIRequestFactory()
    request = getattr(factory, method)(path, data or {}, format="json")
    request.user = membership.user
    return request


@pytest.mark.django_db(transaction=True)
def test_staff_can_list_opening_windows():
    with tenant_schema("opening_windows_endpoint"):
        window = OpeningHours.objects.create(
            weekday=1,
            opens_at=time(12, 0),
            closes_at=time(22, 0),
        )
        membership = _membership(StaffMembership.ROLE_STAFF)
        request = _request("get", "/api/v1/restaurant/opening-windows/", membership)

        response = OpeningWindowListCreateView.as_view()(request)

        assert response.status_code == 200
        assert response.data[0]["id"] == str(window.id)
        assert response.data[0]["weekday"] == 1


@pytest.mark.django_db(transaction=True)
def test_manager_can_create_opening_window():
    with tenant_schema("opening_windows_endpoint"):
        membership = _membership(StaffMembership.ROLE_MANAGER)
        request = _request(
            "post",
            "/api/v1/restaurant/opening-windows/",
            membership,
            {"weekday": 2, "opens_at": "10:00:00", "closes_at": "18:00:00"},
        )

        response = OpeningWindowListCreateView.as_view()(request)

        assert response.status_code == 201
        assert OpeningHours.objects.filter(weekday=2).exists()


@pytest.mark.django_db(transaction=True)
def test_manager_can_update_and_delete_opening_window():
    with tenant_schema("opening_windows_endpoint"):
        window = OpeningHours.objects.create(
            weekday=3,
            opens_at=time(12, 0),
            closes_at=time(22, 0),
        )
        membership = _membership(StaffMembership.ROLE_MANAGER)
        patch_request = _request(
            "patch",
            f"/api/v1/restaurant/opening-windows/{window.id}/",
            membership,
            {"opens_at": "13:00:00"},
        )
        delete_request = _request(
            "delete",
            f"/api/v1/restaurant/opening-windows/{window.id}/",
            membership,
        )

        patch_response = OpeningWindowDetailView.as_view()(patch_request, pk=str(window.id))
        window.refresh_from_db()
        delete_response = OpeningWindowDetailView.as_view()(delete_request, pk=str(window.id))

        assert patch_response.status_code == 200
        assert window.opens_at == time(13, 0)
        assert delete_response.status_code == 204
        assert not OpeningHours.objects.filter(pk=window.pk).exists()


@pytest.mark.django_db(transaction=True)
def test_opening_window_rejects_invalid_weekday_and_time_range():
    with tenant_schema("opening_windows_endpoint"):
        membership = _membership(StaffMembership.ROLE_MANAGER)
        invalid_weekday = _request(
            "post",
            "/api/v1/restaurant/opening-windows/",
            membership,
            {"weekday": 7, "opens_at": "10:00:00", "closes_at": "18:00:00"},
        )
        invalid_range = _request(
            "post",
            "/api/v1/restaurant/opening-windows/",
            membership,
            {"weekday": 1, "opens_at": "18:00:00", "closes_at": "10:00:00"},
        )

        weekday_response = OpeningWindowListCreateView.as_view()(invalid_weekday)
        range_response = OpeningWindowListCreateView.as_view()(invalid_range)

        assert weekday_response.status_code == 400
        assert weekday_response.data["error_code"] == "validation_failed"
        assert range_response.status_code == 400
        assert range_response.data["error_code"] == "validation_failed"


def test_opening_window_routes_resolve():
    collection = resolve("/api/v1/restaurant/opening-windows/")
    detail = resolve("/api/v1/restaurant/opening-windows/00000000-0000-0000-0000-000000000000/")

    assert collection.url_name == "opening-windows"
    assert detail.url_name == "opening-window-detail"
