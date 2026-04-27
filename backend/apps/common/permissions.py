"""Shared DRF permission classes."""

from rest_framework.permissions import BasePermission  # type: ignore[import-untyped]


class IsTenantMember(BasePermission):
    def has_permission(self, request, view) -> bool:
        return getattr(request, "membership", None) is not None


class IsManager(BasePermission):
    def has_permission(self, request, view) -> bool:
        membership = getattr(request, "membership", None)
        return bool(membership and getattr(membership, "role", None) == "manager")
