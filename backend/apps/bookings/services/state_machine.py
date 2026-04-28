"""Booking status transition rules."""

from apps.bookings.models import Booking, BookingStatus as S
from apps.common.codes import ErrorCode
from apps.common.errors import DomainError

ALLOWED = {
    S.PENDING_REVIEW: {
        S.CONFIRMED,
        S.CONFIRMED_WITHOUT_DEPOSIT,
        S.PENDING_PAYMENT,
        S.DECLINED,
        S.CANCELLED_BY_CUSTOMER,
        S.EXPIRED,
        S.AUTHORIZATION_EXPIRED,
    },
    S.PENDING_PAYMENT: {
        S.CONFIRMED,
        S.CONFIRMED_WITHOUT_DEPOSIT,
        S.EXPIRED,
        S.CANCELLED_BY_CUSTOMER,
        S.CANCELLED_BY_STAFF,
        S.DECLINED,
    },
    S.AUTHORIZATION_EXPIRED: {
        S.PENDING_PAYMENT,
        S.CONFIRMED_WITHOUT_DEPOSIT,
        S.DECLINED,
        S.CANCELLED_BY_STAFF,
        S.CANCELLED_BY_CUSTOMER,
    },
    S.CONFIRMED: {S.CANCELLED_BY_CUSTOMER, S.CANCELLED_BY_STAFF, S.NO_SHOW},
    S.CONFIRMED_WITHOUT_DEPOSIT: {S.CANCELLED_BY_CUSTOMER, S.CANCELLED_BY_STAFF, S.NO_SHOW},
}


def transition(booking: Booking, target: str) -> Booking:
    """Apply a valid state transition or raise a domain error."""

    if target not in ALLOWED.get(booking.status, set()):
        raise DomainError(
            ErrorCode.BOOKING_TRANSITION_INVALID,
            {"from": booking.status, "to": target},
        )

    booking.status = target
    return booking
