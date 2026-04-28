"""Tests for opening-hours service."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date, datetime, time

import pytest
from django.db import connection

from apps.restaurants.models import ClosedDay, OpeningHours
from apps.restaurants.services.opening_hours import is_open


@contextmanager
def opening_hours_tables() -> Iterator[None]:
    existing_tables = set(connection.introspection.table_names())
    models_in_order = (OpeningHours, ClosedDay)
    for model in models_in_order:
        if model._meta.db_table not in existing_tables:
            with connection.schema_editor() as editor:
                editor.create_model(model)
            existing_tables.add(model._meta.db_table)
    yield


@pytest.mark.django_db
def test_is_open_during_hours():
    with opening_hours_tables():
        OpeningHours.objects.create(
            weekday=0,
            opens_at=time(12, 0),
            closes_at=time(22, 0),
        )
        dt = datetime(2025, 1, 6, 14, 0)
        assert is_open(dt) is True


@pytest.mark.django_db
def test_is_closed_on_closed_day():
    with opening_hours_tables():
        OpeningHours.objects.create(
            weekday=0,
            opens_at=time(12, 0),
            closes_at=time(22, 0),
        )
        ClosedDay.objects.create(date=date(2025, 1, 6))
        dt = datetime(2025, 1, 6, 14, 0)
        assert is_open(dt) is False


@pytest.mark.django_db
def test_is_closed_outside_hours():
    with opening_hours_tables():
        OpeningHours.objects.create(
            weekday=0,
            opens_at=time(12, 0),
            closes_at=time(22, 0),
        )
        dt = datetime(2025, 1, 6, 11, 0)
        assert is_open(dt) is False
