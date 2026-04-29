"""Tests for walk-in table assignments."""

import pytest
from django.db import connection
from django.db import IntegrityError
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone
from django_tenants.utils import schema_context  # type: ignore[import-untyped]

from apps.bookings.models import Walkin, WalkinTableAssignment
from apps.restaurants.models import Room, Table
from tests.tenant_helpers import tenant_schema


def _walkin() -> Walkin:
    return Walkin.objects.create(starts_at=timezone.now(), party_size=2)


def _table(label: str) -> Table:
    room, _ = Room.objects.get_or_create(name="Main")
    return Table.objects.create(room=room, label=label, seats=2)


@pytest.mark.django_db
def test_walkin_can_have_multiple_table_assignments():
    with tenant_schema("walkin_table_assignments"):
        walkin = _walkin()
        table_1 = _table("T1")
        table_2 = _table("T2")

        WalkinTableAssignment.objects.create(walkin=walkin, table=table_1)
        WalkinTableAssignment.objects.create(walkin=walkin, table=table_2)

        assigned_tables = set(
            WalkinTableAssignment.objects.filter(walkin=walkin).values_list(
                "table_id", flat=True
            )
        )
        assert assigned_tables == {table_1.id, table_2.id}


@pytest.mark.django_db
def test_duplicate_walkin_table_assignment_is_rejected():
    with tenant_schema("walkin_table_assignments"):
        walkin = _walkin()
        table = _table("T1")
        WalkinTableAssignment.objects.create(walkin=walkin, table=table)

        with pytest.raises(IntegrityError):
            WalkinTableAssignment.objects.create(walkin=walkin, table=table)


@pytest.mark.django_db(transaction=True)
def test_existing_walkin_table_fk_migrates_to_assignment():
    with tenant_schema("walkin_table_migration") as (_tenant, schema_name, _domain):
        with schema_context(schema_name):
            executor = MigrationExecutor(connection)
            executor.migrate([("bookings", "0004_booking_table_assignment")])

            old_apps = executor.loader.project_state(
                [("bookings", "0004_booking_table_assignment")]
            ).apps
            WalkinModel = old_apps.get_model("bookings", "Walkin")
            RoomModel = old_apps.get_model("restaurants", "Room")
            TableModel = old_apps.get_model("restaurants", "Table")

            room = RoomModel.objects.create(name="Migration Room")
            table = TableModel.objects.create(room=room, label="M1", seats=2)
            walkin = WalkinModel.objects.create(
                starts_at=timezone.now(),
                party_size=2,
                table=table,
            )

            executor = MigrationExecutor(connection)
            executor.migrate([("bookings", "0005_walkin_table_assignment")])

            new_apps = executor.loader.project_state(
                [("bookings", "0005_walkin_table_assignment")]
            ).apps
            AssignmentModel = new_apps.get_model("bookings", "WalkinTableAssignment")

            assert AssignmentModel.objects.filter(
                walkin_id=walkin.id,
                table_id=table.id,
                assigned_by_id__isnull=True,
            ).exists()
