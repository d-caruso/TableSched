"""URL routing tests."""

import pytest


@pytest.mark.django_db(transaction=True)
def test_healthz_on_public_schema(client, public_tenant):
    response = client.get("/healthz/")
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_unknown_tenant_slug_returns_404(client, public_tenant):
    response = client.get("/restaurants/does-not-exist/api/v1/bookings/")
    assert response.status_code == 404
