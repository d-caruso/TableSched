"""Notification routing for booking workflows."""


def notify_customer(booking, code: str, *, raw_token: str | None = None) -> None:
    """Route a customer notification to the appropriate channels."""

    customer = booking.customer
    ctx = _build_ctx(booking, raw_token)
    _send_sms(booking, code, customer.locale, customer.phone, ctx)

    if customer.email:
        _send_email(booking, code, customer.locale, customer.email, ctx)


def notify_staff(booking, code: str, **kwargs) -> None:
    """Best-effort staff notification placeholder."""

    _ = (booking, code, kwargs)


def _build_ctx(booking, raw_token: str | None) -> dict[str, object]:
    """Build the shared template context."""

    from django.conf import settings

    return {
        "restaurant": getattr(settings, "PUBLIC_BOOKING_RESTAURANT_NAME", ""),
        "when": booking.starts_at.strftime("%a %d %b %H:%M"),
        "party": booking.party_size,
        "url": f"{settings.PUBLIC_BOOKING_BASE_URL}/{raw_token}" if raw_token else "",
        "booking_id": str(booking.id),
    }


def _send_sms(booking, code: str, locale: str, phone: str, ctx: dict[str, object]) -> None:
    """Placeholder SMS sender for the routing task."""

    _ = (booking, code, locale, phone, ctx)


def _send_email(
    booking,
    code: str,
    locale: str,
    email: str,
    ctx: dict[str, object],
) -> None:
    """Placeholder email sender for the routing task."""

    _ = (booking, code, locale, email, ctx)
