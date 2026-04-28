"""Tests for restaurant settings model."""

from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from django.db import connection

from apps.restaurants.models import RestaurantSettings


@contextmanager
def restaurant_settings_table() -> Iterator[None]:
    table_name = RestaurantSettings._meta.db_table
    table_exists = table_name in connection.introspection.table_names()
    if not table_exists:
        with connection.schema_editor() as editor:
            editor.create_model(RestaurantSettings)
    yield


@pytest.mark.django_db
def test_deposit_policy_choices():
    valid = {choice[0] for choice in RestaurantSettings.DEPOSIT_POLICY}
    assert valid == {"never", "always", "party_threshold"}


@pytest.mark.django_db
def test_default_deposit_policy_is_never():
    with restaurant_settings_table():
        settings = RestaurantSettings.objects.create()
        assert settings.deposit_policy == "never"
