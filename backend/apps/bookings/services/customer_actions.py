"""Customer-initiated booking actions."""

from collections.abc import Mapping
from typing import Any

from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services.creation import (
    _validate_advance_limit,
    _validate_cutoff,
    _validate_opening_hours,
    _validate_slot_alignment,
)
from apps.bookings.services.state_machine import transition
from apps.common.codes import ErrorCode
from apps.common.errors import DomainError
from apps.restaurants.models import RestaurantSettings
from django.utils import timezone
from datetime import timedelta


def cancel_by_customer(booking: Booking, *, settings: RestaurantSettings) -> Booking:
    """Cancel a booking through customer token flow."""

    _enforce_cancellation_cutoff(booking, settings)
    transition(booking, BookingStatus.CANCELLED_BY_CUSTOMER)
    booking.save(update_fields=["status", "updated_at"])
    return booking


def modify_by_customer(
    booking: Booking,
    payload: Mapping[str, Any],
    *,
    settings: RestaurantSettings,
) -> Booking:
    """Apply customer-requested updates and return booking to pending review."""

    _enforce_cancellation_cutoff(booking, settings)
    starts_at = payload.get("starts_at") or booking.starts_at
    party_size = payload.get("party_size") or booking.party_size
    notes = payload.get("notes", booking.notes)

    changed_fields: list[str] = []
    if (starts_at, party_size) != (booking.starts_at, booking.party_size):
        _validate_slot_alignment(starts_at)
        _validate_advance_limit(starts_at, settings)
        _validate_cutoff(starts_at, settings)
        _validate_opening_hours(starts_at)
        booking.starts_at = starts_at
        booking.party_size = party_size
        changed_fields.extend(["starts_at", "party_size"])
        if booking.status in (
            BookingStatus.CONFIRMED,
            BookingStatus.CONFIRMED_WITHOUT_DEPOSIT,
        ):
            transition(booking, BookingStatus.PENDING_REVIEW)
            changed_fields.append("status")

    if notes != booking.notes:
        booking.notes = notes
        changed_fields.append("notes")

    if changed_fields:
        booking.save(update_fields=[*changed_fields, "updated_at"])
    return booking


def _enforce_cancellation_cutoff(
    booking: Booking,
    settings: RestaurantSettings,
) -> None:
    if booking.starts_at - timezone.now() < timedelta(
        hours=settings.cancellation_cutoff_hours
    ):
        raise DomainError(ErrorCode.CUTOFF_PASSED)
