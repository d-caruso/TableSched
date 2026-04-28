"""Payment service stubs for booking workflows."""

from apps.payments.models import Payment


def create_preauth(*, booking, settings):
    """Create a near-term authorization intent placeholder."""
    from apps.payments.gateways.stripe import create_preauth as stripe_create_preauth

    return stripe_create_preauth(booking=booking, settings=settings)


def get_authorized_payment(*, booking):
    """Return authorized payment placeholder for booking, if any."""

    _ = booking
    return None


def capture(payment) -> Payment:
    """Capture an already authorized payment placeholder."""

    from apps.payments.gateways.stripe import capture as stripe_capture

    return stripe_capture(payment)


def cancel_authorization(payment) -> Payment:
    """Cancel an existing authorization placeholder."""

    from apps.payments.gateways.stripe import cancel_authorization as stripe_cancel_authorization

    return stripe_cancel_authorization(payment)


def create_payment_link(*, booking, settings):
    """Create payment link placeholder for long-term payment flow."""

    from apps.payments.gateways.stripe import create_payment_link as stripe_create_payment_link

    return stripe_create_payment_link(booking=booking, settings=settings)


def refund(payment) -> Payment:
    """Refund a captured payment placeholder."""

    from apps.payments.gateways.stripe import refund as stripe_refund

    return stripe_refund(payment)
