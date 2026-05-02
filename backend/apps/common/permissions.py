"""Shared DRF permission classes."""

from rest_framework.permissions import BasePermission  # type: ignore[import-untyped]

from apps.memberships.models import StaffMembership


class IsTenantMember(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return StaffMembership.objects.filter(user=request.user, is_active=True).exists()


class IsManager(BasePermission):
    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        return StaffMembership.objects.filter(
            user=request.user, role=StaffMembership.ROLE_MANAGER, is_active=True
        ).exists()
