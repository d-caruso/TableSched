"""Opening-hours helpers."""

from datetime import datetime

from apps.restaurants.models import ClosedDay, OpeningHours


def is_open(dt: datetime) -> bool:
    """Return True when restaurant is open at the given datetime."""

    if ClosedDay.objects.filter(date=dt.date()).exists():
        return False
    return OpeningHours.objects.filter(
        weekday=dt.weekday(),
        opens_at__lte=dt.time(),
        closes_at__gt=dt.time(),
    ).exists()
