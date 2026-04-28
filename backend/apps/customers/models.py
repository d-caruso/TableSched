"""Tenant-schema customer models."""

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
