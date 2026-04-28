"""Payment gateway protocol definitions."""

from typing import Any, Protocol

from apps.payments.models import Payment


class PaymentGateway(Protocol):
    """Gateway contract for payment providers."""

    def create_preauth(self, *, booking: Any, amount_cents: int) -> Payment: ...

    def capture(self, payment: Payment) -> Payment: ...

    def cancel_authorization(self, payment: Payment) -> Payment: ...

    def create_payment_link(
        self,
        *,
        booking: Any,
        amount_cents: int,
        expires_at: Any,
    ) -> Payment: ...

    def refund(self, payment: Payment) -> Payment: ...

