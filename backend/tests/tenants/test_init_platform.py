"""Tests for the init_platform management command."""

import pytest
from django.core.management import call_command

from apps.tenants.models import Restaurant


@pytest.mark.django_db(transaction=True)
def test_init_platform_creates_public_tenant():
    Restaurant.objects.filter(schema_name="public").delete()
    call_command("init_platform")
    assert Restaurant.objects.filter(schema_name="public").exists()


@pytest.mark.django_db(transaction=True)
def test_init_platform_is_idempotent():
    call_command("init_platform")
    call_command("init_platform")
    assert Restaurant.objects.filter(schema_name="public").count() == 1


@pytest.mark.django_db(transaction=True)
def test_init_platform_prints_confirmation(capsys):
    Restaurant.objects.filter(schema_name="public").delete()
    call_command("init_platform")
    out = capsys.readouterr().out
    assert "Platform initialised." in out
