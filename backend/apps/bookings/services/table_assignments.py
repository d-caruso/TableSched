"""Manual table assignment services."""

from collections.abc import Iterable

from apps.bookings.models import (
    Booking,
    BookingTableAssignment,
    Walkin,
    WalkinTableAssignment,
)
from apps.memberships.models import StaffMembership
from apps.restaurants.models import Table


def replace_booking_tables(
    booking: Booking,
    *,
    tables: Iterable[Table],
    by_membership: StaffMembership | None,
) -> Booking:
    table_ids = {table.id for table in tables}
    BookingTableAssignment.objects.filter(booking=booking).exclude(table_id__in=table_ids).delete()
    for table in tables:
        BookingTableAssignment.objects.update_or_create(
            booking=booking,
            table=table,
            defaults={"assigned_by": by_membership},
        )
    return booking


def remove_booking_table(booking: Booking, *, table: Table) -> Booking:
    BookingTableAssignment.objects.filter(booking=booking, table=table).delete()
    return booking


def replace_walkin_tables(
    walkin: Walkin,
    *,
    tables: Iterable[Table],
    by_membership: StaffMembership | None,
) -> Walkin:
    table_ids = {table.id for table in tables}
    WalkinTableAssignment.objects.filter(walkin=walkin).exclude(table_id__in=table_ids).delete()
    for table in tables:
        WalkinTableAssignment.objects.update_or_create(
            walkin=walkin,
            table=table,
            defaults={"assigned_by": by_membership},
        )
    return walkin


def remove_walkin_table(walkin: Walkin, *, table: Table) -> Walkin:
    WalkinTableAssignment.objects.filter(walkin=walkin, table=table).delete()
    return walkin
