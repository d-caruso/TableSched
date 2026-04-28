"""Tenant-schema payment models."""

from django.db import models

from apps.common.models import TimeStampedModel


class PaymentStatus(models.TextChoices):
    PENDING = "pending"
    AUTHORIZED = "authorized"
    CAPTURED = "captured"
    FAILED = "failed"
    REFUND_PENDING = "refund_pending"
    REFUNDED = "refunded"
    REFUND_FAILED = "refund_failed"


class Payment(TimeStampedModel):
    """Canonical payment record for Stripe-backed booking deposits."""

    KIND_PREAUTH = "preauth"
    KIND_LINK = "link"
    KIND_CHOICES = (
        (KIND_PREAUTH, KIND_PREAUTH),
        (KIND_LINK, KIND_LINK),
    )

    booking: models.OneToOneField = models.OneToOneField(
        "bookings.Booking",
        on_delete=models.PROTECT,
    )
    kind: models.CharField = models.CharField(max_length=16, choices=KIND_CHOICES)
    stripe_payment_intent_id: models.CharField = models.CharField(
        max_length=128,
        blank=True,
        db_index=True,
    )
    stripe_checkout_session_id: models.CharField = models.CharField(
        max_length=128,
        blank=True,
        db_index=True,
    )
    amount_cents: models.PositiveIntegerField = models.PositiveIntegerField()
    currency: models.CharField = models.CharField(max_length=8, default="eur")
    status: models.CharField = models.CharField(
        max_length=32,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    expires_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)


class StripeEvent(TimeStampedModel):
    """Idempotency record for processed Stripe webhook events."""

    event_id: models.CharField = models.CharField(max_length=128, unique=True)
    event_type: models.CharField = models.CharField(max_length=128)
    processed_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
