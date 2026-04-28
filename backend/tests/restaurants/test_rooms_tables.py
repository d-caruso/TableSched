"""Tests for room and table models."""

from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from django.db import IntegrityError
from django.db import connection

from apps.restaurants.models import Room, Table


@contextmanager
def room_table_models() -> Iterator[None]:
    existing_tables = set(connection.introspection.table_names())
    models_in_order = (Room, Table)
    for model in models_in_order:
        if model._meta.db_table not in existing_tables:
            with connection.schema_editor() as editor:
                editor.create_model(model)
            existing_tables.add(model._meta.db_table)
    yield


@pytest.mark.django_db
def test_table_label_unique_per_room():
    with room_table_models():
        room = Room.objects.create(name="Main Room")
        Table.objects.create(room=room, label="T1", seats=4)
        with pytest.raises(IntegrityError):
            Table.objects.create(room=room, label="T1", seats=2)


@pytest.mark.django_db
def test_same_label_allowed_in_different_rooms():
    with room_table_models():
        room_1 = Room.objects.create(name="Room A")
        room_2 = Room.objects.create(name="Room B")
        Table.objects.create(room=room_1, label="T1", seats=4)
        table_2 = Table.objects.create(room=room_2, label="T1", seats=4)
        assert table_2.pk is not None
