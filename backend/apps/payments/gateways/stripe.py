"""Stripe payment gateway skeleton."""

from __future__ import annotations

from typing import Any

import stripe
from django.db import connection

from apps.payments.models import Payment
from apps.payments.models import PaymentStatus


def create_preauth(*, booking: Any, settings) -> stripe.PaymentIntent:
    """Create a manual-capture PaymentIntent and persist a payment record."""

    tenant_schema = getattr(connection, "schema_name", "public")
    intent = stripe.PaymentIntent.create(
        amount=settings.deposit_amount_cents,
        currency="eur",
        capture_method="manual",
        automatic_payment_methods={"enabled": True},
        metadata={
            "tenant_schema": tenant_schema,
            "booking_id": str(booking.id),
        },
    )
    Payment.objects.create(
        booking=booking,
        kind=Payment.KIND_PREAUTH,
        stripe_payment_intent_id=intent.id,
        amount_cents=settings.deposit_amount_cents,
        status=PaymentStatus.PENDING,
    )
    return intent


class StripeGateway:
    """Stripe gateway implementation placeholder for the MVP."""

    def create_preauth(self, *, booking: Any, amount_cents: int) -> Any:
        _ = amount_cents
        from apps.restaurants.models import RestaurantSettings

        settings = RestaurantSettings.objects.get()
        return create_preauth(booking=booking, settings=settings)

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
