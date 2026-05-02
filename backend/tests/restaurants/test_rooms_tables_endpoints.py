"""Tests for tenant room and table endpoints."""

from uuid import uuid4

import pytest
from django.urls import resolve
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.memberships.models import StaffMembership
from apps.restaurants.models import Room, Table
from apps.restaurants.views import (
    RoomDetailView,
    RoomListCreateView,
    TableDetailView,
    TableListCreateView,
)
from tests.tenant_helpers import tenant_schema


def _membership(role: str) -> StaffMembership:
    suffix = uuid4().hex[:8]
    user = User.objects.create_user(
        username=f"{role}_layout_{suffix}",
        email=f"{role}-layout-{suffix}@example.com",
    )
    return StaffMembership.objects.create(user=user, role=role, is_active=True)


def _request(method: str, path: str, membership: StaffMembership, data=None):
    factory = APIRequestFactory()
    request = getattr(factory, method)(path, data or {}, format="json")
    request.user = membership.user
    return request


@pytest.mark.django_db(transaction=True)
def test_staff_can_list_rooms_and_tables():
    with tenant_schema("rooms_tables_endpoint"):
        room = Room.objects.create(name="Main")
        table = Table.objects.create(room=room, label="T1", seats=4)
        membership = _membership(StaffMembership.ROLE_STAFF)
        rooms_request = _request("get", "/api/v1/restaurant/rooms/", membership)
        tables_request = _request("get", "/api/v1/restaurant/tables/", membership)

        rooms_response = RoomListCreateView.as_view()(rooms_request)
        tables_response = TableListCreateView.as_view()(tables_request)

        assert rooms_response.status_code == 200
        assert rooms_response.data[0]["id"] == str(room.id)
        assert tables_response.status_code == 200
        assert tables_response.data[0]["id"] == str(table.id)


@pytest.mark.django_db(transaction=True)
def test_manager_can_create_update_and_delete_room():
    with tenant_schema("rooms_tables_endpoint"):
        membership = _membership(StaffMembership.ROLE_MANAGER)
        create_request = _request(
            "post",
            "/api/v1/restaurant/rooms/",
            membership,
            {"name": "Main"},
        )

        create_response = RoomListCreateView.as_view()(create_request)
        room = Room.objects.get(name="Main")
        patch_request = _request(
            "patch",
            f"/api/v1/restaurant/rooms/{room.id}/",
            membership,
            {"name": "Garden"},
        )
        delete_request = _request(
            "delete",
            f"/api/v1/restaurant/rooms/{room.id}/",
            membership,
        )

        patch_response = RoomDetailView.as_view()(patch_request, pk=str(room.id))
        room.refresh_from_db()
        delete_response = RoomDetailView.as_view()(delete_request, pk=str(room.id))

        assert create_response.status_code == 201
        assert patch_response.status_code == 200
        assert room.name == "Garden"
        assert delete_response.status_code == 204
        assert not Room.objects.filter(pk=room.pk).exists()


@pytest.mark.django_db(transaction=True)
def test_manager_can_create_update_and_delete_table():
    with tenant_schema("rooms_tables_endpoint"):
        room = Room.objects.create(name="Main")
        membership = _membership(StaffMembership.ROLE_MANAGER)
        create_request = _request(
            "post",
            "/api/v1/restaurant/tables/",
            membership,
            {"room": str(room.id), "label": "T1", "seats": 4, "pos_x": 10, "pos_y": 20},
        )

        create_response = TableListCreateView.as_view()(create_request)
        table = Table.objects.get(label="T1")
        patch_request = _request(
            "patch",
            f"/api/v1/restaurant/tables/{table.id}/",
            membership,
            {"seats": 6, "pos_x": 30},
        )
        delete_request = _request(
            "delete",
            f"/api/v1/restaurant/tables/{table.id}/",
            membership,
        )

        patch_response = TableDetailView.as_view()(patch_request, pk=str(table.id))
        table.refresh_from_db()
        delete_response = TableDetailView.as_view()(delete_request, pk=str(table.id))

        assert create_response.status_code == 201
        assert patch_response.status_code == 200
        assert table.seats == 6
        assert table.pos_x == 30
        assert delete_response.status_code == 204
        assert not Table.objects.filter(pk=table.pk).exists()


@pytest.mark.django_db(transaction=True)
def test_table_label_remains_unique_per_room():
    with tenant_schema("rooms_tables_endpoint"):
        room = Room.objects.create(name="Main")
        Table.objects.create(room=room, label="T1", seats=4)
        membership = _membership(StaffMembership.ROLE_MANAGER)
        request = _request(
            "post",
            "/api/v1/restaurant/tables/",
            membership,
            {"room": str(room.id), "label": "T1", "seats": 2},
        )

        response = TableListCreateView.as_view()(request)

        assert response.status_code == 400
        assert response.data["error_code"] == "validation_failed"


def test_room_and_table_routes_resolve():
    room_collection = resolve("/api/v1/restaurant/rooms/")
    room_detail = resolve("/api/v1/restaurant/rooms/00000000-0000-0000-0000-000000000000/")
    table_collection = resolve("/api/v1/restaurant/tables/")
    table_detail = resolve("/api/v1/restaurant/tables/00000000-0000-0000-0000-000000000000/")

    assert room_collection.url_name == "rooms"
    assert room_detail.url_name == "room-detail"
    assert table_collection.url_name == "tables"
    assert table_detail.url_name == "table-detail"
