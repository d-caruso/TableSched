"""Domain error and reason codes."""


class ErrorCode:
    VALIDATION_FAILED = "validation_failed"
    BOOKING_OUTSIDE_OPENING_HOURS = "booking_outside_opening_hours"
    BOOKING_CUTOFF_PASSED = "booking_cutoff_passed"
    BOOKING_BEYOND_ADVANCE_LIMIT = "booking_beyond_advance_limit"
    BOOKING_SLOT_MISALIGNED = "booking_slot_misaligned"
    BOOKING_TRANSITION_INVALID = "booking_transition_invalid"
    PAYMENT_REQUIRED = "payment_required"
    PAYMENT_AUTHORIZATION_FAILED = "payment_authorization_failed"
    PAYMENT_AUTHORIZATION_EXPIRED = "payment_authorization_expired"
    PAYMENT_CAPTURE_FAILED = "payment_capture_failed"
    NOT_TENANT_MEMBER = "not_tenant_member"
    PERMISSION_DENIED = "permission_denied"
    TOKEN_INVALID = "token_invalid"
    TOKEN_EXPIRED = "token_expired"
    CUTOFF_PASSED = "cutoff_passed"


class ReasonCode:
    STAFF_REJECTION_GENERIC = "staff_rejection_generic"
    PAYMENT_NOT_RECEIVED = "payment_not_received"
    NO_SHOW = "no_show"
    AUTHORIZATION_EXPIRED = "authorization_expired"
