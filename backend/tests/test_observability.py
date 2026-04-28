"""Observability regressions."""

import pytest


@pytest.mark.django_db
def test_healthz_returns_200_and_ok_body(client):
    response = client.get("/healthz/", HTTP_HOST="localhost")
    assert response.status_code == 200
    assert response.content == b"ok"
