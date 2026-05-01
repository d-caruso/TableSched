"""Tests for table assignment services and serializer output."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.bookings.models import (
    Booking,
    BookingTableAssignment,
    Walkin,
    WalkinTableAssignment,
)
from apps.bookings.serializers import BookingSerializer
from apps.bookings.serializers_walkins import WalkinSerializer
from apps.bookings.services.table_assignments import (
    remove_booking_table,
    remove_walkin_table,
    replace_booking_tables,
    replace_walkin_tables,
)
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.restaurants.models import Room, Table
from tests.tenant_helpers import tenant_schema


def _booking() -> Booking:
    customer = Customer.objects.create(
        phone="+3900173000",
        email="table-services@example.com",
        name="Table Services",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
    )


def _walkin() -> Walkin:
    return Walkin.objects.create(starts_at=timezone.now(), party_size=2)


def _membership() -> StaffMembership:
    user = User.objects.create_user(username="staff17_3", email="staff173@example.com")
    return StaffMembership.objects.create(user=user, role=StaffMembership.ROLE_MANAGER)


def _table(label: str) -> Table:
    room, _ = Room.objects.get_or_create(name="Main")
    return Table.objects.create(room=room, label=label, seats=2)


@pytest.mark.django_db
def test_replace_booking_tables_sets_exact_assignments_idempotently():
    with tenant_schema("booking_table_services"):
        booking = _booking()
        membership = _membership()
        table_1 = _table("T1")
        table_2 = _table("T2")
        table_3 = _table("T3")

        replace_booking_tables(booking, tables=[table_1, table_2], by_membership=membership)
        replace_booking_tables(booking, tables=[table_2, table_3], by_membership=membership)
        replace_booking_tables(booking, tables=[table_2, table_3], by_membership=membership)

        assigned_tables = set(
            BookingTableAssignment.objects.filter(booking=booking).values_list(
                "table_id", flat=True
            )
        )
        assert assigned_tables == {table_2.id, table_3.id}
        assert BookingTableAssignment.objects.filter(booking=booking).count() == 2


@pytest.mark.django_db
def test_remove_booking_table_preserves_other_assignments():
    with tenant_schema("booking_table_services"):
        booking = _booking()
        table_1 = _table("T1")
        table_2 = _table("T2")
        replace_booking_tables(booking, tables=[table_1, table_2], by_membership=None)

        remove_booking_table(booking, table=table_1)

        assert list(
            BookingTableAssignment.objects.filter(booking=booking).values_list(
                "table_id", flat=True
            )
        ) == [table_2.id]


@pytest.mark.django_db
def test_replace_walkin_tables_sets_exact_assignments_idempotently():
    with tenant_schema("walkin_table_services"):
        walkin = _walkin()
        membership = _membership()
        table_1 = _table("T1")
        table_2 = _table("T2")
        table_3 = _table("T3")

        replace_walkin_tables(walkin, tables=[table_1, table_2], by_membership=membership)
        replace_walkin_tables(walkin, tables=[table_2, table_3], by_membership=membership)
        replace_walkin_tables(walkin, tables=[table_2, table_3], by_membership=membership)

        assigned_tables = set(
            WalkinTableAssignment.objects.filter(walkin=walkin).values_list(
                "table_id", flat=True
            )
        )
        assert assigned_tables == {table_2.id, table_3.id}
        assert WalkinTableAssignment.objects.filter(walkin=walkin).count() == 2


@pytest.mark.django_db
def test_remove_walkin_table_preserves_other_assignments():
    with tenant_schema("walkin_table_services"):
        walkin = _walkin()
        table_1 = _table("T1")
        table_2 = _table("T2")
        replace_walkin_tables(walkin, tables=[table_1, table_2], by_membership=None)

        remove_walkin_table(walkin, table=table_1)

        assert list(
            WalkinTableAssignment.objects.filter(walkin=walkin).values_list(
                "table_id", flat=True
            )
        ) == [table_2.id]


@pytest.mark.django_db
def test_serializers_expose_tables_and_not_table():
    with tenant_schema("table_serializer_services"):
        booking = _booking()
        walkin = _walkin()
        table = _table("T1")
        replace_booking_tables(booking, tables=[table], by_membership=None)
        replace_walkin_tables(walkin, tables=[table], by_membership=None)

        booking_payload = BookingSerializer(booking).data
        walkin_payload = WalkinSerializer(walkin).data

        assert booking_payload["tables"] == [table.id]
        assert "table" not in booking_payload
        assert walkin_payload["tables"] == [table.id]
        assert "table" not in walkin_payload
