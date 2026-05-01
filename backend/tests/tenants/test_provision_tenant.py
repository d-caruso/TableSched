"""Tests for the provision_tenant management command."""

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django_tenants.utils import schema_context

from apps.memberships.models import StaffMembership
from apps.tenants.models import Domain, Restaurant

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_provision_tenant_creates_all_objects():
    call_command(
        "provision_tenant",
        name="Rome Restaurant",
        schema="rome_test",
        admin_email="owner@rome.com",
        admin_password="testpass123",
    )

    assert Restaurant.objects.filter(schema_name="rome_test").exists()
    assert Domain.objects.filter(domain="rome_test").exists()
    user = User.objects.get(email="owner@rome.com")
    with schema_context("rome_test"):
        assert StaffMembership.objects.filter(
            user=user, role=StaffMembership.ROLE_MANAGER, is_active=True
        ).exists()


@pytest.mark.django_db(transaction=True)
def test_provision_tenant_prints_prefix_and_login(capsys):
    call_command(
        "provision_tenant",
        name="Rome Restaurant",
        schema="rome_print",
        admin_email="print@rome.com",
        admin_password="testpass123",
    )

    out = capsys.readouterr().out
    assert "/restaurants/rome_print/" in out
    assert "print@rome.com" in out


@pytest.mark.django_db(transaction=True)
def test_provision_tenant_fails_if_schema_exists():
    call_command(
        "provision_tenant",
        name="Rome Restaurant",
        schema="rome_dup",
        admin_email="a@rome.com",
        admin_password="testpass123",
    )
    with pytest.raises(Exception):
        call_command(
            "provision_tenant",
            name="Rome 2",
            schema="rome_dup",
            admin_email="b@rome.com",
            admin_password="testpass123",
        )
