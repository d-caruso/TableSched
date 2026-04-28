"""URL routing tests."""

import pytest


@pytest.mark.django_db
def test_healthz_on_public_schema(client):
    response = client.get("/healthz/", HTTP_HOST="localhost")
    assert response.status_code == 200


@pytest.mark.django_db
def test_tenant_api_requires_tenant_host(client):
    response = client.get("/api/v1/bookings/", HTTP_HOST="localhost")
    assert response.status_code in (404, 400, 403)
