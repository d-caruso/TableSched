"""Tests for accounts models."""

from django.contrib.auth import get_user_model


def test_user_model_is_custom(db):
    user_model = get_user_model()
    assert user_model.__name__ == "User"
    assert user_model._meta.app_label == "accounts"


def test_create_user(db):
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username="staff1",
        email="staff1@example.com",
        password="pass",
    )
    assert user.pk is not None
