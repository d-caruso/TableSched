"""Opportunistic maintenance for dashboard-triggered cleanup."""

from datetime import timedelta

from django.utils.timezone import now

from apps.bookings.models import Booking, BookingStatus
from apps.bookings.services.state_machine import transition
from apps.notifications import services as notifications
from apps.payments.models import Payment, PaymentStatus


def run_opportunistic_maintenance() -> None:
    """Run all bounded maintenance passes."""

    _expire_pending_payments()
    _expire_authorized_deposits()
    _reconcile_payments()


def _expire_pending_payments() -> None:
    """Expire overdue pending-payment bookings."""

    bookings = Booking.objects.filter(
        status=BookingStatus.PENDING_PAYMENT,
        payment_due_at__lt=now(),
    )[:200]
    for booking in bookings:
        transition(booking, BookingStatus.EXPIRED)
        booking.save(update_fields=["status", "updated_at"])
        notifications.notify_customer(booking, "booking_expired")


def _expire_authorized_deposits() -> None:
    """Mark stale authorizations as expired for staff review."""

    payments = (
        Payment.objects.filter(
            status=PaymentStatus.AUTHORIZED,
            booking__status=BookingStatus.PENDING_REVIEW,
            created_at__lt=now() - timedelta(days=6),
        )
        .select_related("booking")
        [:200]
    )
    for payment in payments:
        payment.status = PaymentStatus.FAILED
        payment.save(update_fields=["status", "updated_at"])
        booking = payment.booking
        transition(booking, BookingStatus.AUTHORIZATION_EXPIRED)
        booking.save(update_fields=["status", "updated_at"])
        notifications.notify_staff(booking, "authorization_expired_staff")


def _reconcile_payments() -> None:
    """Placeholder for best-effort payment reconciliation."""

    return None
