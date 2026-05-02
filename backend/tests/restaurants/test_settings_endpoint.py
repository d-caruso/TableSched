"""Tests for tenant restaurant settings endpoint."""

import pytest
from django.urls import resolve
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.memberships.models import StaffMembership
from apps.restaurants.models import RestaurantSettings
from apps.restaurants.views import RestaurantSettingsView
from tests.tenant_helpers import tenant_schema


def _membership(role: str) -> StaffMembership:
    user = User.objects.create_user(username=f"{role}_settings", email=f"{role}@example.com")
    return StaffMembership.objects.create(user=user, role=role, is_active=True)


def _request(method: str, membership: StaffMembership | None = None, data=None):
    factory = APIRequestFactory()
    request = getattr(factory, method)(
        "/api/v1/restaurant/settings/",
        data or {},
        format="json",
    )
    if membership is not None:
        request.user = membership.user
    return request


@pytest.mark.django_db(transaction=True)
def test_staff_can_read_restaurant_settings():
    with tenant_schema("restaurant_settings_endpoint"):
        settings_obj = RestaurantSettings.objects.create()
        membership = _membership(StaffMembership.ROLE_STAFF)
        request = _request("get", membership)

        response = RestaurantSettingsView.as_view()(request)

        assert response.status_code == 200
        assert response.data["deposit_policy"] == settings_obj.deposit_policy


@pytest.mark.django_db(transaction=True)
def test_manager_can_update_restaurant_settings():
    with tenant_schema("restaurant_settings_endpoint"):
        settings_obj = RestaurantSettings.objects.create()
        membership = _membership(StaffMembership.ROLE_MANAGER)
        request = _request(
            "patch",
            membership,
            {
                "deposit_policy": RestaurantSettings.DEPOSIT_ALWAYS,
                "deposit_amount_cents": 3000,
            },
        )

        response = RestaurantSettingsView.as_view()(request)
        settings_obj.refresh_from_db()

        assert response.status_code == 200
        assert settings_obj.deposit_policy == RestaurantSettings.DEPOSIT_ALWAYS
        assert settings_obj.deposit_amount_cents == 3000


@pytest.mark.django_db(transaction=True)
def test_staff_cannot_update_restaurant_settings():
    with tenant_schema("restaurant_settings_endpoint"):
        settings_obj = RestaurantSettings.objects.create()
        membership = _membership(StaffMembership.ROLE_STAFF)
        request = _request("patch", membership, {"deposit_amount_cents": 3000})

        response = RestaurantSettingsView.as_view()(request)
        settings_obj.refresh_from_db()

        assert response.status_code == 403
        assert settings_obj.deposit_amount_cents != 3000


@pytest.mark.django_db(transaction=True)
def test_anonymous_cannot_read_restaurant_settings():
    with tenant_schema("restaurant_settings_endpoint"):
        request = _request("get")

        response = RestaurantSettingsView.as_view()(request)

        assert response.status_code == 403


def test_restaurant_settings_route_resolves():
    match = resolve("/api/v1/restaurant/settings/")

    assert match.url_name == "restaurant-settings"
