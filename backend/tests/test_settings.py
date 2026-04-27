"""Settings tests."""

from django.core.management import call_command


def test_django_check_passes():
    """Django system check must pass with no errors."""
    call_command("check")
