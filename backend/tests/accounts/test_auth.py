"""Tests for django-allauth authentication configuration."""

from django.contrib.auth import get_user_model


def test_login_with_email(client, db):
    user_model = get_user_model()
    user_model.objects.create_user(
        username="staff1",
        email="staff@example.com",
        password="testpass123",
    )

    response = client.post(
        "/auth/login/",
        {"login": "staff@example.com", "password": "testpass123"},
        HTTP_HOST="localhost",
    )

    assert response.status_code in (200, 302)


def test_signup_is_disabled(client, db):
    response = client.post(
        "/auth/signup/",
        {"email": "new@example.com", "password1": "testpass123", "password2": "testpass123"},
        HTTP_HOST="localhost",
    )

    assert response.status_code == 403
