"""Booking creation workflow and validation rules."""

from datetime import timedelta
from typing import Any

from django.utils import timezone

from apps.bookings.models import Booking
from apps.common.codes import ErrorCode
from apps.common.errors import DomainError
from apps.customers.models import BookingAccessToken, Customer
from apps.restaurants.models import RestaurantSettings
from apps.restaurants.services.opening_hours import is_open


def create_booking_request(
    *,
    settings: RestaurantSettings,
    customer: Customer,
    starts_at,
    party_size: int,
    notes: str,
) -> tuple[Booking, Any | None]:
    """Create booking request and optional near-term pre-authorization intent."""

    _validate_slot_alignment(starts_at)
    _validate_advance_limit(starts_at, settings)
    _validate_cutoff(starts_at, settings)
    _validate_opening_hours(starts_at)
    _validate_party_size(party_size)

    booking = Booking.objects.create(
        customer=customer,
        starts_at=starts_at,
        party_size=party_size,
        notes=notes,
    )

    payment_intent = None
    if _deposit_required(settings, party_size) and _is_near_term(starts_at, settings):
        from apps.payments import services as payments

        payment_intent = payments.create_preauth(booking=booking, settings=settings)

    _token, raw = BookingAccessToken.issue(booking)
    from apps.notifications import services as notifications

    _safe_notify(notifications.notify_customer, booking, "booking_request_received", raw_token=raw)
    _safe_notify(notifications.notify_staff, booking, "new_booking_request")

    return booking, payment_intent


def _safe_notify(fn, *args, **kwargs) -> None:
    try:
        fn(*args, **kwargs)
    except Exception:
        return


def _deposit_required(settings: RestaurantSettings, party_size: int) -> bool:
    if settings.deposit_policy == RestaurantSettings.DEPOSIT_ALWAYS:
        return True
    if settings.deposit_policy == RestaurantSettings.DEPOSIT_NEVER:
        return False
    threshold = settings.deposit_party_threshold
    return threshold is not None and party_size >= threshold


def _is_near_term(starts_at, settings: RestaurantSettings) -> bool:
    limit = timezone.now() + timedelta(hours=settings.near_term_threshold_hours)
    return starts_at <= limit


def _validate_slot_alignment(starts_at) -> None:
    if starts_at.minute % 15 != 0:
        raise DomainError(ErrorCode.BOOKING_SLOT_MISALIGNED)


def _validate_advance_limit(starts_at, settings: RestaurantSettings) -> None:
    max_start = timezone.now() + timedelta(days=settings.advance_booking_days)
    if starts_at > max_start:
        raise DomainError(ErrorCode.BOOKING_BEYOND_ADVANCE_LIMIT)


def _validate_cutoff(starts_at, settings: RestaurantSettings) -> None:
    minimum_start = timezone.now() + timedelta(minutes=settings.booking_cutoff_minutes)
    if starts_at < minimum_start:
        raise DomainError(ErrorCode.BOOKING_CUTOFF_PASSED)


def _validate_opening_hours(starts_at) -> None:
    if not is_open(starts_at):
        raise DomainError(ErrorCode.BOOKING_OUTSIDE_OPENING_HOURS)


def _validate_party_size(party_size: int) -> None:
    if party_size < 1:
        raise DomainError(ErrorCode.VALIDATION_FAILED, {"field": "party_size"})
