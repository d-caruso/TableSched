"""Tests for membership middleware."""

from types import SimpleNamespace

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse

from apps.memberships import middleware as memberships_middleware
from apps.memberships.middleware import MembershipMiddleware


class FakeQuerySet:
    def __init__(self, membership):
        self._membership = membership

    def first(self):
        return self._membership


class FakeManager:
    def __init__(self, membership):
        self.membership = membership
        self.last_filter = None

    def filter(self, **kwargs):
        self.last_filter = kwargs
        return FakeQuerySet(self.membership)


def test_middleware_sets_membership_for_authenticated_staff(rf, django_user_model, monkeypatch):
    user = django_user_model.objects.create_user(username="manager_user")
    membership = object()
    manager = FakeManager(membership)
    fake_model = SimpleNamespace(objects=manager)

    monkeypatch.setattr(
        memberships_middleware.apps,
        "get_model",
        lambda *args, **kwargs: fake_model,
    )

    middleware = MembershipMiddleware(lambda request: HttpResponse(status=204))
    request = rf.get("/")
    request.user = user

    response = middleware(request)

    assert response.status_code == 204
    assert getattr(request, "membership") is membership
    assert manager.last_filter == {"user": user, "is_active": True}


def test_middleware_sets_none_for_anonymous(rf, monkeypatch):
    monkeypatch.setattr(
        memberships_middleware.apps,
        "get_model",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("not expected")),
    )

    middleware = MembershipMiddleware(lambda request: HttpResponse(status=204))
    request = rf.get("/")
    request.user = AnonymousUser()

    response = middleware(request)

    assert response.status_code == 204
    assert getattr(request, "membership") is None


def test_middleware_sets_none_when_membership_model_missing(rf, django_user_model, monkeypatch):
    user = django_user_model.objects.create_user(username="staff_user")

    def _raise_lookup_error(*args, **kwargs):
        raise LookupError

    monkeypatch.setattr(memberships_middleware.apps, "get_model", _raise_lookup_error)

    middleware = MembershipMiddleware(lambda request: HttpResponse(status=204))
    request = rf.get("/")
    request.user = user

    response = middleware(request)

    assert response.status_code == 204
    assert getattr(request, "membership") is None
