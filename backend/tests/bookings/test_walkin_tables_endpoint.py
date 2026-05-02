"""Tests for walk-in table assignment resource endpoint."""

import pytest
from django.urls import resolve
from django.utils import timezone
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.bookings.models import Walkin, WalkinTableAssignment
from apps.bookings.services.table_assignments import replace_walkin_tables
from apps.bookings.views_walkins import WalkinViewSet
from apps.memberships.models import StaffMembership
from apps.restaurants.models import Room, Table
from tests.tenant_helpers import tenant_schema


def _walkin() -> Walkin:
    return Walkin.objects.create(starts_at=timezone.now(), party_size=2)


def _membership() -> StaffMembership:
    user = User.objects.create_user(username="staff18_4", email="staff184@example.com")
    return StaffMembership.objects.create(user=user, role=StaffMembership.ROLE_MANAGER)


def _table(label: str) -> Table:
    room, _ = Room.objects.get_or_create(name="Main")
    return Table.objects.create(room=room, label=label, seats=2)


def _request(method: str, walkin: Walkin, membership: StaffMembership, data=None):
    factory = APIRequestFactory()
    request = getattr(factory, method)(
        f"/api/v1/walkins/{walkin.id}/tables/",
        data or {},
        format="json",
    )
    request.user = membership.user
    return request


@pytest.mark.django_db(transaction=True)
def test_get_walkin_tables_returns_assigned_table_ids():
    with tenant_schema("walkin_tables_endpoint"):
        walkin = _walkin()
        membership = _membership()
        table = _table("T1")
        replace_walkin_tables(walkin, tables=[table], by_membership=membership)
        request = _request("get", walkin, membership)

        response = WalkinViewSet.as_view({"get": "tables"})(request, pk=str(walkin.id))

        assert response.status_code == 200
        assert response.data == {"tables": [str(table.id)]}


@pytest.mark.django_db(transaction=True)
def test_put_walkin_tables_replaces_assignments_idempotently():
    with tenant_schema("walkin_tables_endpoint"):
        walkin = _walkin()
        membership = _membership()
        table_1 = _table("T1")
        table_2 = _table("T2")
        table_3 = _table("T3")
        replace_walkin_tables(walkin, tables=[table_1], by_membership=membership)
        request = _request(
            "put",
            walkin,
            membership,
            {"tables": [str(table_2.id), str(table_3.id)]},
        )
        repeat_request = _request(
            "put",
            walkin,
            membership,
            {"tables": [str(table_2.id), str(table_3.id)]},
        )

        response = WalkinViewSet.as_view({"put": "tables"})(request, pk=str(walkin.id))
        repeat_response = WalkinViewSet.as_view({"put": "tables"})(
            repeat_request,
            pk=str(walkin.id),
        )

        assert response.status_code == 200
        assert repeat_response.status_code == 200
        assert set(response.data["tables"]) == {str(table_2.id), str(table_3.id)}
        assert WalkinTableAssignment.objects.filter(walkin=walkin).count() == 2


@pytest.mark.django_db(transaction=True)
def test_delete_walkin_table_removes_only_selected_assignment():
    with tenant_schema("walkin_tables_endpoint"):
        walkin = _walkin()
        membership = _membership()
        table_1 = _table("T1")
        table_2 = _table("T2")
        replace_walkin_tables(walkin, tables=[table_1, table_2], by_membership=membership)
        request = _request("delete", walkin, membership)

        response = WalkinViewSet.as_view({"delete": "tables"})(
            request,
            pk=str(walkin.id),
            table_id=str(table_1.id),
        )

        assert response.status_code == 204
        assert list(
            WalkinTableAssignment.objects.filter(walkin=walkin).values_list(
                "table_id", flat=True
            )
        ) == [table_2.id]


@pytest.mark.django_db(transaction=True)
def test_put_walkin_tables_requires_tables_list():
    with tenant_schema("walkin_tables_endpoint"):
        walkin = _walkin()
        membership = _membership()
        request = _request("put", walkin, membership, {"tables": "not-a-list"})

        response = WalkinViewSet.as_view({"put": "tables"})(request, pk=str(walkin.id))

        assert response.status_code == 400
        assert response.data["error_code"] == "validation_failed"
        assert response.data["params"]["field"] == "tables"


def test_walkin_tables_route_resolves():
    match = resolve("/api/v1/walkins/00000000-0000-0000-0000-000000000000/tables/")
    delete_match = resolve(
        "/api/v1/walkins/00000000-0000-0000-0000-000000000000/tables/"
        "11111111-1111-1111-1111-111111111111/"
    )

    assert match.url_name == "walkins-tables"
    assert delete_match.url_name == "walkins-tables"
