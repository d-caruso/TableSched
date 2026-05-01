"""Tests for tenant management commands."""

import uuid
from io import StringIO

import pytest
from django.core.management import call_command

from apps.tenants.models import Domain, Restaurant


@pytest.mark.django_db(transaction=True)
def test_create_tenant_without_domain():
    suffix = uuid.uuid4().hex[:8]
    schema_name = f"rest_{suffix}"
    out = StringIO()

    call_command("create_tenant", name="Ristorante X", schema=schema_name, stdout=out)

    assert Restaurant.objects.filter(schema_name=schema_name, name="Ristorante X").exists()
    assert not Domain.objects.filter(tenant__schema_name=schema_name).exists()
    assert f"/restaurants/{schema_name}/" in out.getvalue()


@pytest.mark.django_db(transaction=True)
def test_create_tenant_with_domain():
    suffix = uuid.uuid4().hex[:8]
    schema_name = f"rest_{suffix}"
    domain_name = f"rest-{suffix}.localhost"

    call_command("create_tenant", name="Ristorante X", schema=schema_name, domain=domain_name)

    assert Restaurant.objects.filter(schema_name=schema_name, name="Ristorante X").exists()
    assert Domain.objects.filter(domain=domain_name).exists()
