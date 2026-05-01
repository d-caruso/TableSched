"""Shared tenant helpers for payment tests."""

from collections.abc import Iterator
from contextlib import contextmanager
from uuid import uuid4

from django_tenants.utils import schema_context  # type: ignore[import-untyped]

from apps.tenants.models import Domain, Restaurant


@contextmanager
def payment_tenant() -> Iterator[tuple[Restaurant, str, str]]:
    """Create an isolated tenant schema and matching test domain."""

    schema_name = f"pay_{uuid4().hex[:8]}"
    restaurant = Restaurant.objects.create(schema_name=schema_name, name="Payment Test")

    with schema_context("public"):
        Domain.objects.create(domain=schema_name, tenant=restaurant, is_primary=True)

    with schema_context(schema_name):
        yield restaurant, schema_name, schema_name
