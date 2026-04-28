"""German notification templates."""

TEMPLATES = {
    "booking_request_received": {
        "sms": "Ihre Buchung bei {restaurant} am {when} für {party} Personen wurde empfangen. Verwalten: {url}",
        "email_subject": "Buchungsanfrage erhalten",
        "email_body": "Ihre Buchung bei {restaurant} am {when} für {party} Personen wurde empfangen. Verwalten: {url}",
    },
    "booking_approved": {
        "sms": "Ihre Buchung bei {restaurant} am {when} ist bestätigt.",
        "email_subject": "Buchung bestätigt",
        "email_body": "Ihre Buchung bei {restaurant} am {when} für {party} Personen ist bestätigt.",
    },
    "booking_declined": {
        "sms": "Ihre Buchung bei {restaurant} am {when} wurde abgelehnt.",
        "email_subject": "Buchung abgelehnt",
        "email_body": "Ihre Buchung bei {restaurant} am {when} wurde abgelehnt.",
    },
    "payment_required": {
        "sms": "Bitte schließen Sie die Zahlung für Ihre Buchung ab: {url}",
        "email_subject": "Zahlung erforderlich",
        "email_body": "Bitte schließen Sie die Zahlung für Ihre Buchung bei {restaurant} ab: {url}",
    },
    "authorization_expired_staff": {
        "sms": "Vorautorisierung für Buchung {booking_id} abgelaufen. Aktion erforderlich.",
        "email_subject": "Vorautorisierung abgelaufen",
        "email_body": "Vorautorisierung für Buchung {booking_id} abgelaufen. Bitte prüfen.",
    },
}

