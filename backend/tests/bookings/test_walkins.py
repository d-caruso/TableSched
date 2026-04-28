import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.bookings.models import Walkin
from apps.bookings.views_walkins import WalkinViewSet
from apps.memberships.models import StaffMembership
from tests.tenant_helpers import tenant_schema


def _seed_staff():
    user = User.objects.create_user(
        username="staff_walkin",
        email="staff-walkin@example.com",
        password="testpass123",
    )
    return StaffMembership.objects.create(
        user=user,
        role=StaffMembership.ROLE_MANAGER,
        is_active=True,
    )


@pytest.mark.django_db(transaction=True)
def test_create_walkin_staff_only():
    with tenant_schema("walkins"):
        request = APIRequestFactory().post(
            "/api/v1/walkins/",
            {"starts_at": timezone.now().isoformat(), "party_size": 3},
            format="json",
        )
        response = WalkinViewSet.as_view({"post": "create"})(request)

        assert response.status_code == 403


@pytest.mark.django_db(transaction=True)
def test_create_walkin_succeeds_for_staff():
    with tenant_schema("walkins"):
        membership = _seed_staff()
        request = APIRequestFactory().post(
            "/api/v1/walkins/",
            {"starts_at": timezone.now().isoformat(), "party_size": 3},
            format="json",
        )
        request.membership = membership
        request.user = membership.user
        response = WalkinViewSet.as_view({"post": "create"})(request)

        assert response.status_code == 201


def test_walkin_has_no_customer_field():
    assert not hasattr(Walkin, "customer")
