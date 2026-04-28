"""Tests for restaurant settings model."""

import pytest

from apps.restaurants.models import RestaurantSettings
from tests.tenant_helpers import tenant_schema


@pytest.mark.django_db
def test_deposit_policy_choices():
    valid = {choice[0] for choice in RestaurantSettings.DEPOSIT_POLICY}
    assert valid == {"never", "always", "party_threshold"}


@pytest.mark.django_db
def test_default_deposit_policy_is_never():
    with tenant_schema("restaurant_settings"):
        settings = RestaurantSettings.objects.create()
        assert settings.deposit_policy == "never"
