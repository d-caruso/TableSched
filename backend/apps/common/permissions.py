"""Shared DRF permission classes."""

from rest_framework.permissions import BasePermission  # type: ignore[import-untyped]


def _resolve_membership(request):
    """Return membership for the authenticated user, caching on the request.

    MembershipMiddleware sets request.membership for session-authenticated requests.
    For JWT-authenticated requests DRF authenticates after middleware runs, so the
    middleware sees AnonymousUser. This function handles both cases.
    """
    membership = getattr(request, "membership", None)
    if membership is not None:
        return membership
    user = getattr(request, "user", None)
    if not getattr(user, "is_authenticated", False):
        return None
    from apps.memberships.models import StaffMembership
    membership = StaffMembership.objects.filter(user=user, is_active=True).first()
    request.membership = membership
    return membership


class IsTenantMember(BasePermission):
    def has_permission(self, request, view) -> bool:
        return _resolve_membership(request) is not None


class IsManager(BasePermission):
    def has_permission(self, request, view) -> bool:
        membership = _resolve_membership(request)
        return bool(membership and getattr(membership, "role", None) == "manager")
