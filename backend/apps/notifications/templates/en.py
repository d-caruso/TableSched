"""English notification templates."""

TEMPLATES = {
    "booking_request_received": {
        "sms": "Your booking at {restaurant} on {when} for {party} was received. Manage it: {url}",
        "email_subject": "Booking request received",
        "email_body": "Your booking at {restaurant} on {when} for {party} was received. Manage it: {url}",
    },
    "booking_approved": {
        "sms": "Your booking at {restaurant} on {when} is confirmed.",
        "email_subject": "Booking confirmed",
        "email_body": "Your booking at {restaurant} on {when} for {party} is confirmed.",
    },
    "booking_declined": {
        "sms": "Your booking at {restaurant} on {when} was declined.",
        "email_subject": "Booking declined",
        "email_body": "Your booking at {restaurant} on {when} was declined.",
    },
    "payment_required": {
        "sms": "Please complete payment for your booking: {url}",
        "email_subject": "Payment required",
        "email_body": "Please complete payment for your booking at {restaurant}: {url}",
    },
    "authorization_expired_staff": {
        "sms": "Pre-authorization expired for booking {booking_id}. Action required.",
        "email_subject": "Pre-authorization expired",
        "email_body": "Pre-authorization expired for booking {booking_id}. Please review.",
    },
}

