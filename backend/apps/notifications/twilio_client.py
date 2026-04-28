"""Twilio client singleton used by notification senders."""

from django.conf import settings
from twilio.rest import Client  # type: ignore[import-untyped]


client = Client(
    getattr(settings, "TWILIO_ACCOUNT_SID", ""),
    getattr(settings, "TWILIO_AUTH_TOKEN", ""),
)
