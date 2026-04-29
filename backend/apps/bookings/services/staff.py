"""Staff-initiated booking actions."""

from datetime import timedelta

from django.utils import timezone

from apps.bookings.models import Booking, BookingStatus, BookingTableAssignment
from apps.bookings.services.state_machine import transition
from apps.common.codes import ErrorCode
from apps.common.errors import DomainError
from apps.memberships.models import StaffMembership
from apps.restaurants.models import RestaurantSettings, Table


def approve(
    booking: Booking,
    *,
    by_membership: StaffMembership,
    settings: RestaurantSettings,
) -> Booking:
    """Approve a pending booking according to deposit/payment state."""

    if booking.status != BookingStatus.PENDING_REVIEW:
        raise DomainError(ErrorCode.BOOKING_TRANSITION_INVALID)

    from apps.payments import services as payments

    payment = payments.get_authorized_payment(booking=booking)
    payment_due_at = None
    if payment is not None:
        payments.capture(payment)
        transition(booking, BookingStatus.CONFIRMED)
    elif _deposit_required(settings, booking.party_size):
        payments.create_payment_link(booking=booking, settings=settings)
        payment_due_at = timezone.now() + timedelta(
            hours=settings.long_term_payment_window_hours
        )
        transition(booking, BookingStatus.PENDING_PAYMENT)
    else:
        transition(booking, BookingStatus.CONFIRMED_WITHOUT_DEPOSIT)

    booking.payment_due_at = payment_due_at
    booking.decided_by = by_membership
    booking.decided_at = timezone.now()
    booking.save(update_fields=["status", "payment_due_at", "decided_by", "decided_at", "updated_at"])

    _notify_customer_for_status(booking)
    _record_audit(
        actor=by_membership,
        action="booking.approve",
        booking=booking,
        payload={"to_status": booking.status},
    )
    return booking


def decline(
    booking: Booking,
    *,
    by_membership: StaffMembership,
    reason_code: str,
    staff_message: str = "",
) -> Booking:
    """Decline a booking and cancel authorized payment if present."""

    transition(booking, BookingStatus.DECLINED)
    booking.staff_message = staff_message
    booking.decided_by = by_membership
    booking.decided_at = timezone.now()
    booking.save(update_fields=["status", "staff_message", "decided_by", "decided_at", "updated_at"])

    from apps.payments import services as payments

    payment = payments.get_authorized_payment(booking=booking)
    if payment is not None:
        payments.cancel_authorization(payment)

    from apps.notifications import services as notifications

    notifications.notify_customer(booking, "booking_declined")
    _record_audit(
        actor=by_membership,
        action="booking.decline",
        booking=booking,
        payload={"reason_code": reason_code},
    )
    return booking


def request_payment_again(
    booking: Booking,
    *,
    by_membership: StaffMembership,
    settings: RestaurantSettings,
) -> Booking:
    """Request a new payment attempt for an existing booking."""

    from apps.payments import services as payments

    payments.create_payment_link(booking=booking, settings=settings)
    booking.payment_due_at = timezone.now() + timedelta(
        hours=settings.long_term_payment_window_hours
    )
    transition(booking, BookingStatus.PENDING_PAYMENT)
    booking.save(update_fields=["status", "payment_due_at", "updated_at"])

    from apps.notifications import services as notifications

    notifications.notify_customer(booking, "payment_required")
    _record_audit(
        actor=by_membership,
        action="booking.request_payment_again",
        booking=booking,
        payload={},
    )
    return booking


def confirm_without_deposit(
    booking: Booking,
    *,
    by_membership: StaffMembership,
) -> Booking:
    """Confirm a booking without deposit capture."""

    transition(booking, BookingStatus.CONFIRMED_WITHOUT_DEPOSIT)
    booking.decided_by = by_membership
    booking.decided_at = timezone.now()
    booking.save(update_fields=["status", "decided_by", "decided_at", "updated_at"])

    from apps.notifications import services as notifications

    notifications.notify_customer(booking, "booking_approved")
    _record_audit(
        actor=by_membership,
        action="booking.confirm_without_deposit",
        booking=booking,
        payload={},
    )
    return booking


def assign_table(
    booking: Booking,
    *,
    by_membership: StaffMembership,
    table: Table,
) -> Booking:
    """Assign or reassign the booking table."""

    BookingTableAssignment.objects.update_or_create(
        booking=booking,
        table=table,
        defaults={"assigned_by": by_membership},
    )
    _record_audit(
        actor=by_membership,
        action="booking.assign_table",
        booking=booking,
        payload={"table_id": str(table.id)},
    )
    return booking


def mark_no_show(booking: Booking, *, by_membership: StaffMembership) -> Booking:
    """Mark a confirmed booking as no-show."""

    transition(booking, BookingStatus.NO_SHOW)
    booking.save(update_fields=["status", "updated_at"])
    _record_audit(
        actor=by_membership,
        action="booking.mark_no_show",
        booking=booking,
        payload={},
    )
    return booking


def modify_by_staff(
    booking: Booking,
    *,
    by_membership: StaffMembership,
    starts_at=None,
    party_size: int | None = None,
    notes: str | None = None,
    table: Table | None = None,
) -> Booking:
    """Apply direct staff edits to booking fields."""

    update_fields: list[str] = []
    if starts_at is not None:
        booking.starts_at = starts_at
        update_fields.append("starts_at")
    if party_size is not None:
        booking.party_size = party_size
        update_fields.append("party_size")
    if notes is not None:
        booking.notes = notes
        update_fields.append("notes")
    if table is not None:
        BookingTableAssignment.objects.update_or_create(
            booking=booking,
            table=table,
            defaults={"assigned_by": by_membership},
        )

    if update_fields:
        booking.save(update_fields=[*update_fields, "updated_at"])
    if update_fields or table is not None:
        payload_fields = [*update_fields]
        if table is not None:
            payload_fields.append("table")
        _record_audit(
            actor=by_membership,
            action="booking.modify_by_staff",
            booking=booking,
            payload={"fields": payload_fields},
        )
    return booking


def _deposit_required(settings: RestaurantSettings, party_size: int) -> bool:
    if settings.deposit_policy == RestaurantSettings.DEPOSIT_ALWAYS:
        return True
    if settings.deposit_policy == RestaurantSettings.DEPOSIT_NEVER:
        return False
    threshold = settings.deposit_party_threshold
    return threshold is not None and party_size >= threshold


def _notify_customer_for_status(booking: Booking) -> None:
    from apps.notifications import services as notifications

    notifications.notify_customer(booking, _customer_code_for(booking.status))


def _customer_code_for(status: str) -> str:
    if status == BookingStatus.PENDING_PAYMENT:
        return "payment_required"
    return "booking_approved"


def _record_audit(*, actor: StaffMembership, action: str, booking: Booking, payload: dict) -> None:
    from apps.audit import services as audit

    audit.record(actor=actor, action=action, target=booking, payload=payload)
