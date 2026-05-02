"""Tests for allauth headless JWT login."""

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_login_returns_jwt_tokens(client, public_tenant):
    user = User.objects.create_user(username="a@b.com", email="a@b.com", password="pass1234")
    EmailAddress.objects.create(user=user, email="a@b.com", verified=True, primary=True)

    response = client.post(
        "/_allauth/app/v1/auth/login",
        {"login": "a@b.com", "password": "pass1234"},
        content_type="application/json",
    )

    assert response.status_code == 200
    data = response.json()
    assert "access" in data.get("meta", {})


@pytest.mark.django_db(transaction=True)
def test_login_unverified_email_returns_403(client, public_tenant):
    User.objects.create_user(username="b@b.com", email="b@b.com", password="pass1234")

    response = client.post(
        "/_allauth/app/v1/auth/login",
        {"login": "b@b.com", "password": "pass1234"},
        content_type="application/json",
    )

    assert response.status_code == 403
