"""Membership middleware."""

from collections.abc import Callable

from django.apps import apps
from django.http import HttpRequest, HttpResponse


class MembershipMiddleware:
    """Resolve staff membership once per request."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        setattr(request, "membership", None)
        user = getattr(request, "user", None)
        if not getattr(user, "is_authenticated", False):
            return self.get_response(request)

        try:
            staff_membership_model = apps.get_model("memberships", "StaffMembership")
        except LookupError:
            return self.get_response(request)

        membership = staff_membership_model.objects.filter(user=user, is_active=True).first()
        setattr(request, "membership", membership)
        return self.get_response(request)
