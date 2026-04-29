"""Tests for booking table assignments."""

from datetime import timedelta

import pytest
from django.db import connection
from django.db import IntegrityError
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone
from django_tenants.utils import schema_context  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.bookings.models import Booking, BookingTableAssignment
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.restaurants.models import Room, Table
from tests.tenant_helpers import tenant_schema


def _booking() -> Booking:
    customer = Customer.objects.create(
        phone="+3900171000",
        email="assignment@example.com",
        name="Assignment Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
    )


def _membership() -> StaffMembership:
    user = User.objects.create_user(username="staff17_1", email="staff171@example.com")
    return StaffMembership.objects.create(user=user, role=StaffMembership.ROLE_MANAGER)


def _table(label: str) -> Table:
    room, _ = Room.objects.get_or_create(name="Main")
    return Table.objects.create(room=room, label=label, seats=2)


@pytest.mark.django_db
def test_booking_model_can_have_multiple_table_assignments():
    with tenant_schema("booking_table_assignments"):
        booking = _booking()
        table_1 = _table("T1")
        table_2 = _table("T2")

        BookingTableAssignment.objects.create(booking=booking, table=table_1)
        BookingTableAssignment.objects.create(booking=booking, table=table_2)

        assigned_tables = set(
            BookingTableAssignment.objects.filter(booking=booking).values_list(
                "table_id", flat=True
            )
        )
        assert assigned_tables == {table_1.id, table_2.id}


@pytest.mark.django_db
def test_duplicate_booking_table_assignment_is_rejected():
    with tenant_schema("booking_table_assignments"):
        booking = _booking()
        table = _table("T1")
        BookingTableAssignment.objects.create(booking=booking, table=table)

        with pytest.raises(IntegrityError):
            BookingTableAssignment.objects.create(booking=booking, table=table)


@pytest.mark.django_db
def test_booking_creation_without_tables_still_succeeds():
    with tenant_schema("booking_table_assignments"):
        booking = _booking()

        assert booking.pk is not None
        assert not BookingTableAssignment.objects.filter(booking=booking).exists()


@pytest.mark.django_db(transaction=True)
def test_existing_booking_table_fk_migrates_to_assignment():
    with tenant_schema("booking_table_migration") as (_tenant, schema_name, _domain):
        with schema_context(schema_name):
            executor = MigrationExecutor(connection)
            executor.migrate([("bookings", "0003_walkin")])

            old_apps = executor.loader.project_state([("bookings", "0003_walkin")]).apps
            CustomerModel = old_apps.get_model("customers", "Customer")
            BookingModel = old_apps.get_model("bookings", "Booking")
            RoomModel = old_apps.get_model("restaurants", "Room")
            TableModel = old_apps.get_model("restaurants", "Table")

            customer = CustomerModel.objects.create(
                phone="+3900171001",
                email="migration@example.com",
                name="Migration Customer",
                locale="en",
            )
            room = RoomModel.objects.create(name="Migration Room")
            table = TableModel.objects.create(room=room, label="M1", seats=2)
            booking = BookingModel.objects.create(
                customer=customer,
                starts_at=timezone.now() + timedelta(days=2),
                party_size=2,
                table=table,
            )

            executor = MigrationExecutor(connection)
            executor.migrate([("bookings", "0004_booking_table_assignment")])

            new_apps = executor.loader.project_state(
                [("bookings", "0004_booking_table_assignment")]
            ).apps
            AssignmentModel = new_apps.get_model("bookings", "BookingTableAssignment")

            assert AssignmentModel.objects.filter(
                booking_id=booking.id,
                table_id=table.id,
                assigned_by_id__isnull=True,
            ).exists()
