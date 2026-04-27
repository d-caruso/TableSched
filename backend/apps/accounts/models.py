"""Accounts models."""

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom staff user model for operator-managed accounts."""

