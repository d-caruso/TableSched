"""Payment service stubs for booking workflows."""


def create_preauth(*, booking, settings):
    """Create a near-term authorization intent placeholder."""

    return {
        "provider": "stripe",
        "type": "preauth",
        "booking_id": str(booking.id),
        "amount_cents": settings.deposit_amount_cents,
    }
