"""Shared helpers for tenant-scoped tests."""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import uuid4

from django.core.management import call_command
from django_tenants.utils import schema_context  # type: ignore[import-untyped]

from apps.tenants.models import Domain, Restaurant


@contextmanager
def tenant_schema(prefix: str) -> Iterator[tuple[Restaurant, str, str]]:
    """Create a tenant with a primary domain and switch into its schema."""

    schema_name = f"{prefix}_{uuid4().hex[:8]}"
    domain_name = f"{schema_name}.localhost"
    tenant = Restaurant.objects.create(schema_name=schema_name, name=prefix)

    with schema_context("public"):
        Domain.objects.create(domain=domain_name, tenant=tenant, is_primary=True)

    call_command("migrate_schemas", schema_name=schema_name, interactive=False, verbosity=0)

    with schema_context(schema_name):
        yield tenant, schema_name, domain_name
