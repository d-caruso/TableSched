"""Available booking slot generation."""

from datetime import date, datetime, timedelta

from django.utils import timezone

from apps.restaurants.models import ClosedDay, OpeningHours, RestaurantSettings

SLOT_INTERVAL_MINUTES = 15


def available_slots(requested_date: date, settings: RestaurantSettings) -> list[datetime]:
    """Return available booking start times for the given date.

    Filters out:
    - Slots on closed days
    - Slots outside opening hours
    - Slots within booking cutoff (too soon)
    - Slots beyond advance booking limit (too far)
    """
    if ClosedDay.objects.filter(date=requested_date).exists():
        return []

    windows = OpeningHours.objects.filter(weekday=requested_date.weekday()).order_by("opens_at")
    if not windows.exists():
        return []

    now = timezone.now()
    cutoff_boundary = now + timedelta(minutes=settings.booking_cutoff_minutes)
    advance_boundary = now + timedelta(days=settings.advance_booking_days)

    slots = []
    for window in windows:
        current = datetime.combine(requested_date, window.opens_at, tzinfo=timezone.utc)
        closes = datetime.combine(requested_date, window.closes_at, tzinfo=timezone.utc)
        while current < closes:
            if cutoff_boundary <= current <= advance_boundary:
                slots.append(current)
            current += timedelta(minutes=SLOT_INTERVAL_MINUTES)

    return slots
