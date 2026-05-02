"""Tests for public restaurant endpoint."""

import pytest
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.restaurants.models import OpeningHours, RestaurantSettings
from apps.restaurants.views import PublicRestaurantView
from tests.tenant_helpers import tenant_schema


@pytest.mark.django_db(transaction=True)
def test_public_restaurant_endpoint_no_auth():
    with tenant_schema("restaurant_public"):
        RestaurantSettings.objects.create()
        request = APIRequestFactory().get("/api/v1/public/")
        response = PublicRestaurantView.as_view()(request)
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_public_restaurant_response_codes_only():
    with tenant_schema("restaurant_public"):
        RestaurantSettings.objects.create(deposit_policy=RestaurantSettings.DEPOSIT_ALWAYS)
        OpeningHours.objects.create(weekday=0, opens_at="12:00:00", closes_at="22:00:00")
        request = APIRequestFactory().get("/api/v1/public/")
        response = PublicRestaurantView.as_view()(request)
    assert response.status_code == 200
    payload = response.data
    assert payload["deposit_policy"] in ("never", "always", "party_threshold")
