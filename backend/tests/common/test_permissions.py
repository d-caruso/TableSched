"""Tests for shared permission classes."""

from types import SimpleNamespace

from apps.common.permissions import IsManager, IsTenantMember


def test_is_tenant_member_allows_with_membership(rf):
    request = rf.get("/")
    setattr(request, "membership", object())
    assert IsTenantMember().has_permission(request, None) is True


def test_is_tenant_member_denies_without_membership(rf):
    request = rf.get("/")
    setattr(request, "membership", None)
    assert IsTenantMember().has_permission(request, None) is False


def test_is_manager_denies_staff_role(rf):
    request = rf.get("/")
    setattr(request, "membership", SimpleNamespace(role="staff"))
    assert IsManager().has_permission(request, None) is False


def test_is_manager_allows_manager_role(rf):
    request = rf.get("/")
    setattr(request, "membership", SimpleNamespace(role="manager"))
    assert IsManager().has_permission(request, None) is True
