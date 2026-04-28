"""Italian notification templates."""

TEMPLATES = {
    "booking_request_received": {
        "sms": "La tua prenotazione da {restaurant} per {when} e {party} persone è stata ricevuta. Gestiscila: {url}",
        "email_subject": "Richiesta di prenotazione ricevuta",
        "email_body": "La tua prenotazione da {restaurant} per {when} e {party} persone è stata ricevuta. Gestiscila: {url}",
    },
    "booking_approved": {
        "sms": "La tua prenotazione da {restaurant} per {when} è confermata.",
        "email_subject": "Prenotazione confermata",
        "email_body": "La tua prenotazione da {restaurant} per {when} e {party} persone è confermata.",
    },
    "booking_declined": {
        "sms": "La tua prenotazione da {restaurant} per {when} è stata rifiutata.",
        "email_subject": "Prenotazione rifiutata",
        "email_body": "La tua prenotazione da {restaurant} per {when} è stata rifiutata.",
    },
    "payment_required": {
        "sms": "Completa il pagamento della tua prenotazione: {url}",
        "email_subject": "Pagamento richiesto",
        "email_body": "Completa il pagamento della tua prenotazione da {restaurant}: {url}",
    },
    "authorization_expired_staff": {
        "sms": "La pre-autorizzazione per la prenotazione {booking_id} è scaduta. Azione richiesta.",
        "email_subject": "Pre-autorizzazione scaduta",
        "email_body": "La pre-autorizzazione per la prenotazione {booking_id} è scaduta. Controlla.",
    },
}

