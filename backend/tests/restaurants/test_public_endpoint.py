"""Tests for public restaurant endpoint."""

from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from django.db import connection

from apps.restaurants.models import OpeningHours, RestaurantSettings


@contextmanager
def restaurant_public_tables() -> Iterator[None]:
    existing_tables = set(connection.introspection.table_names())
    models_in_order = (RestaurantSettings, OpeningHours)
    for model in models_in_order:
        if model._meta.db_table not in existing_tables:
            with connection.schema_editor() as editor:
                editor.create_model(model)
            existing_tables.add(model._meta.db_table)
    yield


@pytest.mark.django_db
def test_public_restaurant_endpoint_no_auth(client):
    with restaurant_public_tables():
        RestaurantSettings.objects.create()
        response = client.get("/api/v1/public/restaurant/", HTTP_HOST="localhost")
    assert response.status_code == 200


@pytest.mark.django_db
def test_public_restaurant_response_codes_only(client):
    with restaurant_public_tables():
        RestaurantSettings.objects.create(deposit_policy=RestaurantSettings.DEPOSIT_ALWAYS)
        OpeningHours.objects.create(weekday=0, opens_at="12:00:00", closes_at="22:00:00")
        response = client.get("/api/v1/public/restaurant/", HTTP_HOST="localhost")
    assert response.status_code == 200
    payload = response.json()
    assert payload["deposit_policy"] in ("never", "always", "party_threshold")
