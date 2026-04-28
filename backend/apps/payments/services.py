"""Payment service stubs for booking workflows."""


def create_preauth(*, booking, settings):
    """Create a near-term authorization intent placeholder."""
    from apps.payments.gateways.stripe import create_preauth as stripe_create_preauth

    return stripe_create_preauth(booking=booking, settings=settings)


def get_authorized_payment(*, booking):
    """Return authorized payment placeholder for booking, if any."""

    _ = booking
    return None


def capture(payment) -> None:
    """Capture an already authorized payment placeholder."""

    _ = payment


def cancel_authorization(payment) -> None:
    """Cancel an existing authorization placeholder."""

    _ = payment


def create_payment_link(*, booking, settings):
    """Create payment link placeholder for long-term payment flow."""

    return {
        "provider": "stripe",
        "type": "payment_link",
        "booking_id": str(booking.id),
        "amount_cents": settings.deposit_amount_cents,
    }
