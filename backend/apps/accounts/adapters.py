"""Allauth account adapter customizations."""

from allauth.account.adapter import DefaultAccountAdapter  # type: ignore[import-untyped]
from allauth.core.exceptions import ImmediateHttpResponse  # type: ignore[import-untyped]
from django.http import HttpResponseForbidden


class AccountAdapter(DefaultAccountAdapter):
    """Disallow public self-service signups; operator-only staff provisioning."""

    def is_open_for_signup(self, request):
        raise ImmediateHttpResponse(HttpResponseForbidden())
