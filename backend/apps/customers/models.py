"""Tenant-schema customer models."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Protocol

from django.db import models

from apps.common.models import TimeStampedModel

LOCALE_EN = "en"
LOCALE_IT = "it"
LOCALE_DE = "de"
LOCALE_CHOICES = (
    (LOCALE_EN, LOCALE_EN),
    (LOCALE_IT, LOCALE_IT),
    (LOCALE_DE, LOCALE_DE),
)


class Customer(TimeStampedModel):
    """Guest customer record deduplicated by phone number."""

    phone: models.CharField = models.CharField(max_length=32, unique=True)
    email: models.EmailField = models.EmailField(blank=True)
    name: models.CharField = models.CharField(max_length=200)
    locale: models.CharField = models.CharField(
        max_length=8,
        choices=LOCALE_CHOICES,
        default=LOCALE_EN,
    )


class BookingAccessToken(TimeStampedModel):
    """One-time issued customer access token for a booking."""

    booking: models.OneToOneField = models.OneToOneField(
        "bookings.Booking",
        on_delete=models.CASCADE,
    )
    token_hash: models.CharField = models.CharField(max_length=128, unique=True, db_index=True)
    expires_at: models.DateTimeField = models.DateTimeField()
    revoked_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)

    @classmethod
    def issue(cls, booking: "BookingWithStart") -> tuple["BookingAccessToken", str]:
        raw = secrets.token_urlsafe(48)
        hashed = hash_token(raw)
        expires = booking.starts_at + timedelta(days=7)
        token = cls.objects.create(booking=booking, token_hash=hashed, expires_at=expires)
        return token, raw


def hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


def verify_token(raw: str, stored_hash: str) -> bool:
    """Verify a booking token without leaking timing differences."""

    return hmac.compare_digest(hash_token(raw), stored_hash)


class BookingWithStart(Protocol):
    starts_at: datetime
