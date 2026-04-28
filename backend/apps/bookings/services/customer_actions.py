"""Customer-initiated booking actions."""

from collections.abc import Mapping
from typing import Any

from apps.bookings.models import Booking, BookingStatus


def cancel_by_customer(booking: Booking) -> Booking:
    """Cancel a booking through customer token flow."""

    booking.status = BookingStatus.CANCELLED_BY_CUSTOMER
    booking.save(update_fields=["status", "updated_at"])
    return booking


def modify_by_customer(booking: Booking, payload: Mapping[str, Any]) -> Booking:
    """Apply customer-requested updates and return booking to pending review."""

    changed_fields: list[str] = []
    if "starts_at" in payload:
        booking.starts_at = payload["starts_at"]
        changed_fields.append("starts_at")
    if "party_size" in payload:
        booking.party_size = payload["party_size"]
        changed_fields.append("party_size")
    if "notes" in payload:
        booking.notes = payload["notes"]
        changed_fields.append("notes")

    booking.status = BookingStatus.PENDING_REVIEW
    changed_fields.append("status")

    if changed_fields:
        booking.save(update_fields=[*changed_fields, "updated_at"])
    return booking
