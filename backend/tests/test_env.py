"""Environment variable contract tests."""

from __future__ import annotations

from pathlib import Path


def test_required_env_vars_listed_in_env_example():
    env_example = Path(__file__).resolve().parents[1] / ".env.example"
    contents = env_example.read_text().splitlines()

    required = [
        "DJANGO_SECRET_KEY",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
        "STRIPE_API_KEY",
        "STRIPE_WEBHOOK_SECRET",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_FROM",
        "EMAIL_HOST",
        "EMAIL_HOST_USER",
        "EMAIL_HOST_PASSWORD",
        "DEFAULT_FROM_EMAIL",
        "ALLOWED_HOSTS",
        "PUBLIC_DOMAIN",
        "PUBLIC_BOOKING_RETURN_URL",
        "PUBLIC_BOOKING_CANCEL_URL",
        "PUBLIC_BOOKING_BASE_URL",
    ]

    for name in required:
        assert any(line.startswith(f"{name}=") for line in contents), name
