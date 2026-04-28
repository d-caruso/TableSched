"""Tests for opening-hours service."""

from datetime import date, datetime, time

import pytest

from apps.restaurants.models import ClosedDay, OpeningHours
from apps.restaurants.services.opening_hours import is_open
from tests.tenant_helpers import tenant_schema


@pytest.mark.django_db
def test_is_open_during_hours():
    with tenant_schema("opening_hours"):
        OpeningHours.objects.create(
            weekday=0,
            opens_at=time(12, 0),
            closes_at=time(22, 0),
        )
        dt = datetime(2025, 1, 6, 14, 0)
        assert is_open(dt) is True


@pytest.mark.django_db
def test_is_closed_on_closed_day():
    with tenant_schema("opening_hours"):
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
    with tenant_schema("opening_hours"):
        OpeningHours.objects.create(
            weekday=0,
            opens_at=time(12, 0),
            closes_at=time(22, 0),
        )
        dt = datetime(2025, 1, 6, 11, 0)
        assert is_open(dt) is False
