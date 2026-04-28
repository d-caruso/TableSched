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


class OpeningHours(TimeStampedModel):
    """Weekly opening schedule for a tenant restaurant."""

    weekday: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField()
    opens_at: models.TimeField = models.TimeField()
    closes_at: models.TimeField = models.TimeField()

    class Meta:
        unique_together = [("weekday", "opens_at", "closes_at")]


class ClosedDay(TimeStampedModel):
    """One-off closed day override."""

    date: models.DateField = models.DateField(unique=True)
    reason_code: models.CharField = models.CharField(max_length=64, blank=True)


class Room(TimeStampedModel):
    """Dining room in the restaurant floor layout."""

    name: models.CharField = models.CharField(max_length=100)


class Table(TimeStampedModel):
    """Bookable table with basic capacity and position data."""

    room: models.ForeignKey = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="tables",
    )
    label: models.CharField = models.CharField(max_length=50)
    seats: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField()
    pos_x: models.IntegerField = models.IntegerField(default=0)
    pos_y: models.IntegerField = models.IntegerField(default=0)

    class Meta:
        unique_together = [("room", "label")]
