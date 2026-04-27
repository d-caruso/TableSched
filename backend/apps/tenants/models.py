"""Public-schema tenant models."""

from datetime import date

from django.db import models
from django_tenants.models import DomainMixin, TenantMixin  # type: ignore[import-untyped]


class Restaurant(TenantMixin):
    """Tenant model for each restaurant."""

    name: models.CharField[str, str] = models.CharField(max_length=200)
    is_active: models.BooleanField[bool, bool] = models.BooleanField(default=True)
    created_on: models.DateField[date, date] = models.DateField(auto_now_add=True)
    auto_create_schema = True


class Domain(DomainMixin):
    """Tenant domain model."""
