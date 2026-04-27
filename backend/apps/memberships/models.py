"""Tenant-schema staff membership models."""

from django.db import models

from apps.common.models import TimeStampedModel


class StaffMembership(TimeStampedModel):
    """Staff membership for a user within a single tenant schema."""

    ROLE_MANAGER = "manager"
    ROLE_STAFF = "staff"
    ROLE_CHOICES = (
        (ROLE_MANAGER, ROLE_MANAGER),
        (ROLE_STAFF, ROLE_STAFF),
    )

    user: models.ForeignKey = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        db_constraint=False,
    )
    role: models.CharField = models.CharField(max_length=16, choices=ROLE_CHOICES)
    is_active: models.BooleanField = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user"], name="uniq_user_per_tenant"),
        ]
