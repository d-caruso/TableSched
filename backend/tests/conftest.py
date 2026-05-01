"""Shared pytest fixtures for backend tests."""

from __future__ import annotations

from uuid import uuid4
from typing import cast

import pytest
from django.core.management import call_command
from django_tenants.test.client import TenantClient  # type: ignore[import-untyped]
from django_tenants.utils import schema_context  # type: ignore[import-untyped]

from apps.bookings.models import Booking
from apps.bookings.models import Walkin
from apps.customers.models import BookingAccessToken, Customer
from apps.memberships.models import StaffMembership
from apps.payments.models import Payment
from apps.restaurants.models import RestaurantSettings, Room, Table
from apps.tenants.models import Restaurant
from tests.factories import (
    BookingFactory,
    BookingAccessTokenFactory,
    CustomerFactory,
    DomainFactory,
    PaymentFactory,
    RestaurantFactory,
    RestaurantSettingsFactory,
    RoomFactory,
    StaffMembershipFactory,
    TableFactory,
    UserFactory,
    WalkinFactory,
)


@pytest.fixture(autouse=True)
def public_tenant(transactional_db):
    """Ensure the public tenant row exists — required by TenantSubfolderMiddleware."""
    Restaurant.objects.get_or_create(schema_name="public", defaults={"name": "Public"})


@pytest.fixture
def tenant_db(transactional_db) -> tuple[Restaurant, str, str]:
    schema_name = f"test_{uuid4().hex[:8]}"
    domain_name = f"{schema_name}.localhost"
    tenant = cast(Restaurant, RestaurantFactory(schema_name=schema_name, name="Test Restaurant"))

    with schema_context("public"):
        DomainFactory(domain=domain_name, tenant=tenant, is_primary=True)

    call_command("migrate_schemas", schema_name=schema_name, interactive=False, verbosity=0)

    return tenant, schema_name, domain_name


@pytest.fixture
def tenant(tenant_db) -> Restaurant:
    tenant, _schema_name, domain_name = tenant_db
    setattr(tenant, "domain", domain_name)
    return tenant


@pytest.fixture
def staff_user(tenant_db):
    return UserFactory()


@pytest.fixture
def manager_user(tenant_db):
    return UserFactory()


@pytest.fixture
def staff_membership(tenant_db, staff_user) -> StaffMembership:
    _tenant, schema_name, _domain_name = tenant_db
    with schema_context(schema_name):
        return cast(StaffMembership, StaffMembershipFactory(user=staff_user, role=StaffMembership.ROLE_STAFF))


@pytest.fixture
def manager_membership(tenant_db, manager_user) -> StaffMembership:
    _tenant, schema_name, _domain_name = tenant_db
    with schema_context(schema_name):
        return cast(StaffMembership, StaffMembershipFactory(user=manager_user, manager=True))


@pytest.fixture
def staff_client(tenant, staff_membership):
    client = TenantClient(tenant)
    client.force_login(staff_membership.user)
    return client


@pytest.fixture
def manager_client(tenant, manager_membership):
    client = TenantClient(tenant)
    client.force_login(manager_membership.user)
    return client


@pytest.fixture
def customer(tenant_db) -> Customer:
    _tenant, schema_name, _domain_name = tenant_db
    with schema_context(schema_name):
        return cast(Customer, CustomerFactory())


@pytest.fixture
def restaurant_settings(tenant_db) -> RestaurantSettings:
    _tenant, schema_name, _domain_name = tenant_db
    with schema_context(schema_name):
        return cast(RestaurantSettings, RestaurantSettingsFactory())


@pytest.fixture
def room(tenant_db) -> Room:
    _tenant, schema_name, _domain_name = tenant_db
    with schema_context(schema_name):
        return cast(Room, RoomFactory())


@pytest.fixture
def table(tenant_db, room) -> Table:
    _tenant, schema_name, _domain_name = tenant_db
    with schema_context(schema_name):
        return cast(Table, TableFactory(room=room))


@pytest.fixture
def booking(tenant_db, customer) -> Booking:
    _tenant, schema_name, _domain_name = tenant_db
    with schema_context(schema_name):
        return cast(Booking, BookingFactory(customer=customer))


@pytest.fixture
def walkin(tenant_db, table) -> Walkin:
    _tenant, schema_name, _domain_name = tenant_db
    _ = table
    with schema_context(schema_name):
        return cast(Walkin, WalkinFactory())


@pytest.fixture
def payment(tenant_db, booking) -> Payment:
    _tenant, schema_name, _domain_name = tenant_db
    with schema_context(schema_name):
        return cast(Payment, PaymentFactory(booking=booking))


@pytest.fixture
def booking_access_token(tenant_db, booking) -> BookingAccessToken:
    _tenant, schema_name, _domain_name = tenant_db
    with schema_context(schema_name):
        return cast(BookingAccessToken, BookingAccessTokenFactory(booking=booking))
