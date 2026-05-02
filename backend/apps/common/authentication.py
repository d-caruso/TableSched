"""DRF authentication backend for allauth headless JWT tokens."""

import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class AllauthJWTAuthentication(BaseAuthentication):
    """Authenticate DRF requests using allauth headless JWT access tokens."""

    def authenticate(self, request):
        auth = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth.startswith("Bearer "):
            return None
        token = auth[7:]
        try:
            payload = jwt.decode(
                token,
                settings.HEADLESS_JWT_SECRET_KEY,
                algorithms=[settings.HEADLESS_JWT_ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Access token expired.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid access token.")

        if payload.get("token_use") != "access":
            raise AuthenticationFailed("Not an access token.")

        try:
            user = User.objects.get(pk=payload["sub"])
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found.")

        return (user, token)
