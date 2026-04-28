"""Tenant-schema audit log models."""

from django.db import models

from apps.common.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    """Explicit audit trail entry for booking and payment actions."""

    actor: models.ForeignKey = models.ForeignKey(
        "memberships.StaffMembership",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    action: models.CharField = models.CharField(max_length=64)
    target_type: models.CharField = models.CharField(max_length=64)
    target_id: models.UUIDField = models.UUIDField()
    payload: models.JSONField = models.JSONField(default=dict)
