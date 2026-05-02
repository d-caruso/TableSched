"""Credential hardening regressions."""

from __future__ import annotations

import logging

import pytest
from django.conf import settings
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.bookings.views import AdminDashboardView
from apps.memberships.models import StaffMembership
from apps.common.log_filters import SensitiveDataFilter
from tests.tenant_helpers import tenant_schema


def _manager(username: str) -> StaffMembership:
    user = User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="testpass123",
    )
    return StaffMembership.objects.create(
        user=user,
        role=StaffMembership.ROLE_MANAGER,
        is_active=True,
    )


@pytest.mark.django_db(transaction=True)
def test_twilio_credentials_not_in_api_response(monkeypatch):
    monkeypatch.setattr(settings, "TWILIO_ACCOUNT_SID", "AC1234567890")
    monkeypatch.setattr(settings, "TWILIO_AUTH_TOKEN", "auth-token-secret")
    monkeypatch.setattr(settings, "TWILIO_FROM", "+15550000000")

    with tenant_schema("credentials"):
        membership = _manager("credential_manager")
        request = APIRequestFactory().get("/api/v1/admin/dashboard/")
        request.user = membership.user

        response = AdminDashboardView.as_view()(request)

    assert response.status_code == 200
    body = str(response.data)
    assert "AC1234567890" not in body
    assert "auth-token-secret" not in body
    assert "+15550000000" not in body


@pytest.mark.django_db
def test_log_filter_redacts_sensitive_keys(monkeypatch):
    monkeypatch.setattr(settings, "TWILIO_AUTH_TOKEN", "super-secret-token")
    monkeypatch.setattr(settings, "EMAIL_HOST_PASSWORD", "smtp-secret")

    record = logging.LogRecord(
        "test",
        logging.INFO,
        "",
        0,
        "auth_token=abc123 password=smtp-secret token=super-secret-token",
        (),
        None,
    )

    SensitiveDataFilter().filter(record)

    assert "abc123" not in record.getMessage()
    assert "smtp-secret" not in record.getMessage()
    assert "super-secret-token" not in record.getMessage()
    assert "[REDACTED]" in record.getMessage()
