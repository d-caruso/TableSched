"""Tests for the public tenant directory endpoint."""

import pytest

from apps.tenants.models import Restaurant


@pytest.mark.django_db(transaction=True)
def test_tenant_directory_lists_active_tenants(client, public_tenant):
    Restaurant.objects.create(schema_name="rome", name="Rome Restaurant", is_active=True)
    Restaurant.objects.create(schema_name="milan", name="Milan Restaurant", is_active=True)
    Restaurant.objects.create(schema_name="inactive", name="Inactive", is_active=False)

    response = client.get("/api/tenants/")

    assert response.status_code == 200
    data = response.json()
    schemas = [t["schema"] for t in data]
    assert "rome" in schemas
    assert "milan" in schemas
    assert "inactive" not in schemas
    assert "public" not in schemas
    assert all(t["api_prefix"] == f"/restaurants/{t['schema']}/" for t in data)


@pytest.mark.django_db(transaction=True)
def test_tenant_directory_requires_no_auth(client, public_tenant):
    response = client.get("/api/tenants/")
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_tenant_directory_returns_sorted_by_name(client, public_tenant):
    Restaurant.objects.create(schema_name="zzz", name="Zzz Restaurant", is_active=True)
    Restaurant.objects.create(schema_name="aaa", name="Aaa Restaurant", is_active=True)

    response = client.get("/api/tenants/")
    data = response.json()
    names = [t["name"] for t in data]
    assert names == sorted(names)
