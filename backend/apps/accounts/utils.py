"""Account creation utilities for operator-provisioned users."""

from django.contrib.auth import get_user_model

from allauth.account.models import EmailAddress

User = get_user_model()


def create_provisioned_user(email: str, password: str) -> "User":
    """Create a user with a pre-verified email address.

    Used for operator-provisioned accounts (tenant admins, manager-invited staff)
    that bypass the self-signup email verification flow.
    """
    user = User.objects.create_user(username=email, email=email, password=password)
    EmailAddress.objects.create(user=user, email=email, verified=True, primary=True)
    return user
