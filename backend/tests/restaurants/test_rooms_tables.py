"""Tests for room and table models."""

import pytest
from django.db import IntegrityError

from apps.restaurants.models import Room, Table
from tests.tenant_helpers import tenant_schema


@pytest.mark.django_db
def test_table_label_unique_per_room():
    with tenant_schema("room_tables"):
        room = Room.objects.create(name="Main Room")
        Table.objects.create(room=room, label="T1", seats=4)
        with pytest.raises(IntegrityError):
            Table.objects.create(room=room, label="T1", seats=2)


@pytest.mark.django_db
def test_same_label_allowed_in_different_rooms():
    with tenant_schema("room_tables"):
        room_1 = Room.objects.create(name="Room A")
        room_2 = Room.objects.create(name="Room B")
        Table.objects.create(room=room_1, label="T1", seats=4)
        table_2 = Table.objects.create(room=room_2, label="T1", seats=4)
        assert table_2.pk is not None
