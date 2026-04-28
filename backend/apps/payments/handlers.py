"""Stripe webhook event handlers."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from django.utils import timezone

from apps.bookings.models import BookingStatus
from apps.bookings.services.state_machine import transition
from apps.notifications import services as notifications
from apps.payments.models import Payment, PaymentStatus, StripeEvent


def dispatch(event: dict[str, Any]) -> None:
    """Dispatch a Stripe event once."""

    event_id = event["id"]
    event_type = event["type"]

    stripe_event, created = StripeEvent.objects.get_or_create(
        event_id=event_id,
        defaults={"event_type": event_type},
    )
    if not created and stripe_event.processed_at is not None:
        return

    handler = _HANDLERS.get(event_type)
    if handler is None:
        stripe_event.processed_at = timezone.now()
        stripe_event.save(update_fields=["processed_at", "updated_at"])
        return

    handler(event)
    stripe_event.event_type = event_type
    stripe_event.processed_at = timezone.now()
    stripe_event.save(update_fields=["event_type", "processed_at", "updated_at"])


def _payment_from_intent(event: dict[str, Any]) -> Payment | None:
    intent = event["data"]["object"]
    intent_id = intent.get("id")
    if not intent_id:
        return None
    return Payment.objects.filter(stripe_payment_intent_id=intent_id).select_related("booking").first()


def _payment_from_session(event: dict[str, Any]) -> Payment | None:
    session = event["data"]["object"]
    session_id = session.get("id")
    if not session_id:
        return None
    return Payment.objects.filter(stripe_checkout_session_id=session_id).select_related("booking").first()


def _payment_from_charge(event: dict[str, Any]) -> Payment | None:
    charge = event["data"]["object"]
    payment_intent_id = charge.get("payment_intent") or charge.get("id")
    if not payment_intent_id:
        return None
    return Payment.objects.filter(stripe_payment_intent_id=payment_intent_id).select_related("booking").first()


def _handle_payment_intent_amount_capturable_updated(event: dict[str, Any]) -> None:
    payment = _payment_from_intent(event)
    if payment is None:
        return
    payment.status = PaymentStatus.AUTHORIZED
    payment.save(update_fields=["status", "updated_at"])


def _handle_payment_intent_succeeded(event: dict[str, Any]) -> None:
    payment = _payment_from_intent(event)
    if payment is None:
        return
    payment.status = PaymentStatus.CAPTURED
    payment.save(update_fields=["status", "updated_at"])


def _handle_payment_intent_failed(event: dict[str, Any]) -> None:
    payment = _payment_from_intent(event)
    if payment is None:
        return
    payment.status = PaymentStatus.FAILED
    payment.save(update_fields=["status", "updated_at"])


def _handle_payment_intent_canceled(event: dict[str, Any]) -> None:
    _handle_payment_intent_failed(event)


def _handle_checkout_session_completed(event: dict[str, Any]) -> None:
    payment = _payment_from_session(event)
    if payment is None:
        return
    payment.status = PaymentStatus.CAPTURED
    payment.save(update_fields=["status", "updated_at"])
    booking = payment.booking
    transition(booking, BookingStatus.CONFIRMED)
    booking.decided_at = timezone.now()
    booking.save(update_fields=["status", "decided_at", "updated_at"])
    notifications.notify_customer(booking, "booking_approved")


def _handle_checkout_session_expired(event: dict[str, Any]) -> None:
    payment = _payment_from_session(event)
    if payment is None:
        return
    payment.status = PaymentStatus.FAILED
    payment.save(update_fields=["status", "updated_at"])


def _handle_charge_refunded(event: dict[str, Any]) -> None:
    payment = _payment_from_charge(event)
    if payment is None:
        return
    payment.status = PaymentStatus.REFUNDED
    payment.save(update_fields=["status", "updated_at"])


def _handle_charge_refund_failed(event: dict[str, Any]) -> None:
    payment = _payment_from_charge(event)
    if payment is None:
        return
    payment.status = PaymentStatus.REFUND_FAILED
    payment.save(update_fields=["status", "updated_at"])


_HANDLERS: dict[str, Callable[[dict[str, Any]], None]] = {
    "payment_intent.amount_capturable_updated": _handle_payment_intent_amount_capturable_updated,
    "payment_intent.succeeded": _handle_payment_intent_succeeded,
    "payment_intent.payment_failed": _handle_payment_intent_failed,
    "payment_intent.canceled": _handle_payment_intent_canceled,
    "checkout.session.completed": _handle_checkout_session_completed,
    "checkout.session.expired": _handle_checkout_session_expired,
    "charge.refunded": _handle_charge_refunded,
    "charge.refund.failed": _handle_charge_refund_failed,
}
