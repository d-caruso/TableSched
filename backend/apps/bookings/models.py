"""Tenant-schema booking models."""

from django.db import models

from apps.common.models import TimeStampedModel


class Booking(TimeStampedModel):
    """Booking record used by staff and customer token flows."""

    customer: models.ForeignKey = models.ForeignKey("customers.Customer", on_delete=models.PROTECT)
    starts_at: models.DateTimeField = models.DateTimeField()
    party_size: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField()
    status: models.CharField = models.CharField(max_length=32, default="pending_review")
    notes: models.TextField = models.TextField(blank=True)
    staff_message: models.TextField = models.TextField(blank=True)
    payment_due_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    decided_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    decided_by: models.ForeignKey = models.ForeignKey(
        "memberships.StaffMembership",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        indexes = [models.Index(fields=["status", "starts_at"])]
