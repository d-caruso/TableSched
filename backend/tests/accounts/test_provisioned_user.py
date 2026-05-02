"""Tests for create_provisioned_user utility."""

import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model

from apps.accounts.utils import create_provisioned_user

User = get_user_model()


@pytest.mark.django_db
def test_creates_user_with_verified_email(public_tenant):
    user = create_provisioned_user("staff@example.com", "pass1234")

    assert User.objects.filter(email="staff@example.com").exists()
    email_addr = EmailAddress.objects.get(user=user)
    assert email_addr.verified is True
    assert email_addr.primary is True


@pytest.mark.django_db
def test_user_can_login_without_verification(client, public_tenant):
    create_provisioned_user("staff2@example.com", "pass1234")

    response = client.post(
        "/_allauth/app/v1/auth/login",
        {"login": "staff2@example.com", "password": "pass1234"},
        content_type="application/json",
    )

    assert response.status_code == 200
