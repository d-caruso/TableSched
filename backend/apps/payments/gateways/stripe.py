"""Stripe payment gateway skeleton."""

from typing import Any

from apps.payments.models import Payment


class StripeGateway:
    """Stripe gateway implementation placeholder for the MVP."""

    def create_preauth(self, *, booking: Any, amount_cents: int) -> Payment:
        _ = (booking, amount_cents)
        raise NotImplementedError

    def capture(self, payment: Payment) -> Payment:
        _ = payment
        raise NotImplementedError

    def cancel_authorization(self, payment: Payment) -> Payment:
        _ = payment
        raise NotImplementedError

    def create_payment_link(
        self,
        *,
        booking: Any,
        amount_cents: int,
        expires_at: Any,
    ) -> Payment:
        _ = (booking, amount_cents, expires_at)
        raise NotImplementedError

    def refund(self, payment: Payment) -> Payment:
        _ = payment
        raise NotImplementedError

