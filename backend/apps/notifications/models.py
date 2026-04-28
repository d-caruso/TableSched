"""Tenant-schema notification audit models."""

from django.db import models

from apps.common.models import TimeStampedModel


class NotificationLog(TimeStampedModel):
    """Audit trail entry for a notification send attempt."""

    CHANNEL_SMS = "sms"
    CHANNEL_EMAIL = "email"
    CHANNEL_CHOICES = (
        (CHANNEL_SMS, CHANNEL_SMS),
        (CHANNEL_EMAIL, CHANNEL_EMAIL),
    )

    booking: models.ForeignKey = models.ForeignKey(
        "bookings.Booking",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    template_code: models.CharField = models.CharField(max_length=64)
    locale: models.CharField = models.CharField(max_length=8)
    channel: models.CharField = models.CharField(max_length=16, choices=CHANNEL_CHOICES)
    recipient: models.CharField = models.CharField(max_length=128)
    status: models.CharField = models.CharField(max_length=16)
    provider_message_id: models.CharField = models.CharField(max_length=128, blank=True)
    error_code: models.CharField = models.CharField(max_length=64, blank=True)
