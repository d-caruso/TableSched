"""Tenant-schema restaurant configuration models."""

from django.db import models

from apps.common.models import TimeStampedModel


class RestaurantSettings(TimeStampedModel):
    """Per-tenant settings for booking and deposit policies."""

    DEPOSIT_NEVER = "never"
    DEPOSIT_ALWAYS = "always"
    DEPOSIT_PARTY_THRESHOLD = "party_threshold"
    DEPOSIT_POLICY = (
        (DEPOSIT_NEVER, DEPOSIT_NEVER),
        (DEPOSIT_ALWAYS, DEPOSIT_ALWAYS),
        (DEPOSIT_PARTY_THRESHOLD, DEPOSIT_PARTY_THRESHOLD),
    )

    deposit_policy: models.CharField = models.CharField(
        max_length=32,
        choices=DEPOSIT_POLICY,
        default=DEPOSIT_NEVER,
    )
    deposit_party_threshold: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )
    deposit_amount_cents: models.PositiveIntegerField = models.PositiveIntegerField(default=0)
    near_term_threshold_hours: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        default=48
    )
    long_term_payment_window_hours: models.PositiveSmallIntegerField = (
        models.PositiveSmallIntegerField(default=24)
    )
    cancellation_cutoff_hours: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        default=24
    )
    booking_cutoff_minutes: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        default=5
    )
    advance_booking_days: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField(
        default=90
    )
