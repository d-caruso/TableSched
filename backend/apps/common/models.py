"""Shared abstract model mixins."""

import uuid
from datetime import datetime

from django.db import models


class TimeStampedModel(models.Model):
    id: models.UUIDField[uuid.UUID, uuid.UUID] = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    created_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(
        auto_now_add=True
    )
    updated_at: models.DateTimeField[datetime, datetime] = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
