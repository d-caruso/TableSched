"""Tests for tenant public-schema models."""

import uuid

import pytest
from django.db import connection
from django_tenants.utils import schema_context  # type: ignore[import-untyped]

from apps.tenants.models import Domain, Restaurant


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@pytest.mark.django_db(transaction=True)
def test_restaurant_creates_schema():
    schema_name = _new_id("rest")
    domain_name = f"{schema_name}.localhost"

    restaurant = Restaurant.objects.create(schema_name=schema_name, name="Test Restaurant")
    Domain.objects.create(domain=domain_name, tenant=restaurant, is_primary=True)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s",
            [schema_name],
        )
        row = cursor.fetchone()

    assert row == (schema_name,)


@pytest.mark.django_db(transaction=True)
def test_tenant_schema_isolation():
    schema_a = _new_id("tenant_a")
    schema_b = _new_id("tenant_b")

    restaurant_a = Restaurant.objects.create(schema_name=schema_a, name="Tenant A")
    restaurant_b = Restaurant.objects.create(schema_name=schema_b, name="Tenant B")
    Domain.objects.create(domain=f"{schema_a}.localhost", tenant=restaurant_a, is_primary=True)
    Domain.objects.create(domain=f"{schema_b}.localhost", tenant=restaurant_b, is_primary=True)

    with schema_context(schema_a):
        with connection.cursor() as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS isolation_probe (value TEXT)")
            cursor.execute("TRUNCATE TABLE isolation_probe")
            cursor.execute("INSERT INTO isolation_probe (value) VALUES (%s)", ["tenant_a"])

    with schema_context(schema_b):
        with connection.cursor() as cursor:
            cursor.execute("CREATE TABLE IF NOT EXISTS isolation_probe (value TEXT)")
            cursor.execute("TRUNCATE TABLE isolation_probe")
            cursor.execute("INSERT INTO isolation_probe (value) VALUES (%s)", ["tenant_b"])

    with schema_context(schema_a):
        with connection.cursor() as cursor:
            cursor.execute("SELECT value FROM isolation_probe")
            values_a = [row[0] for row in cursor.fetchall()]

    with schema_context(schema_b):
        with connection.cursor() as cursor:
            cursor.execute("SELECT value FROM isolation_probe")
            values_b = [row[0] for row in cursor.fetchall()]

    assert values_a == ["tenant_a"]
    assert values_b == ["tenant_b"]
