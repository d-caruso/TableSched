"""Observability regressions."""

import pytest


@pytest.mark.django_db(transaction=True)
def test_healthz_returns_200_and_ok_body(client, public_tenant):
    response = client.get("/healthz/")
    assert response.status_code == 200
    assert response.content == b"ok"
