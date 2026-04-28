"""Twilio client singleton used by notification senders."""

from django.conf import settings
from twilio.rest import Client  # type: ignore[import-untyped]


client = Client(
    settings.TWILIO_ACCOUNT_SID,
    settings.TWILIO_AUTH_TOKEN,
)
