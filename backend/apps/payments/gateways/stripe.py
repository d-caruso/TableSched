"""Stripe payment gateway skeleton."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import stripe
from django.db import connection
from django.conf import settings as django_settings
from django.utils import timezone

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


def capture(payment: Payment) -> Payment:
    """Capture a manual PaymentIntent and persist captured status."""

    stripe.PaymentIntent.capture(payment.stripe_payment_intent_id)
    payment.status = PaymentStatus.CAPTURED
    payment.save(update_fields=["status", "updated_at"])
    return payment


def cancel_authorization(payment: Payment) -> Payment:
    """Cancel a manual PaymentIntent authorization and persist failure."""

    stripe.PaymentIntent.cancel(payment.stripe_payment_intent_id)
    payment.status = PaymentStatus.FAILED
    payment.save(update_fields=["status", "updated_at"])
    return payment


def create_payment_link(*, booking: Any, settings) -> Payment:
    """Create a Stripe Checkout session and persist the payment link."""

    expires_at = timezone.now() + timedelta(hours=settings.long_term_payment_window_hours)
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "eur",
                    "unit_amount": settings.deposit_amount_cents,
                    "product_data": {"name": f"Deposit booking {booking.id}"},
                },
                "quantity": 1,
            }
        ],
        success_url=getattr(django_settings, "PUBLIC_BOOKING_RETURN_URL", ""),
        cancel_url=getattr(django_settings, "PUBLIC_BOOKING_CANCEL_URL", ""),
        expires_at=int(expires_at.timestamp()),
        metadata={
            "tenant_schema": getattr(connection, "schema_name", "public"),
            "booking_id": str(booking.id),
        },
    )
    payment, _ = Payment.objects.update_or_create(
        booking=booking,
        defaults={
            "kind": Payment.KIND_LINK,
            "stripe_checkout_session_id": session.id,
            "amount_cents": settings.deposit_amount_cents,
            "currency": "eur",
            "status": PaymentStatus.PENDING,
            "expires_at": expires_at,
        },
    )
    return payment


def refund(payment: Payment) -> Payment:
    """Refund a captured payment and persist the outcome."""

    payment.status = PaymentStatus.REFUND_PENDING
    payment.save(update_fields=["status", "updated_at"])
    try:
        stripe.Refund.create(payment_intent=payment.stripe_payment_intent_id)
        payment.status = PaymentStatus.REFUNDED
    except stripe.error.StripeError:
        payment.status = PaymentStatus.REFUND_FAILED
    payment.save(update_fields=["status", "updated_at"])
    return payment


class StripeGateway:
    """Stripe gateway implementation placeholder for the MVP."""

    def create_preauth(self, *, booking: Any, amount_cents: int) -> Any:
        _ = amount_cents
        from apps.restaurants.models import RestaurantSettings

        settings = RestaurantSettings.objects.get()
        return create_preauth(booking=booking, settings=settings)

    def capture(self, payment: Payment) -> Payment:
        return capture(payment)

    def cancel_authorization(self, payment: Payment) -> Payment:
        return cancel_authorization(payment)

    def create_payment_link(
        self,
        *,
        booking: Any,
        amount_cents: int,
        expires_at: Any,
    ) -> Payment:
        _ = amount_cents, expires_at
        from apps.restaurants.models import RestaurantSettings

        settings = RestaurantSettings.objects.get()
        return create_payment_link(booking=booking, settings=settings)

    def refund(self, payment: Payment) -> Payment:
        return refund(payment)
