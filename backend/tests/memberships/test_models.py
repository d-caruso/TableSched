"""Tests for memberships models."""

import uuid
from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.db import IntegrityError
from django.db import transaction

from apps.memberships.models import StaffMembership


@contextmanager
def staff_membership_table() -> Iterator[None]:
    table_name = StaffMembership._meta.db_table
    table_exists = table_name in connection.introspection.table_names()
    if not table_exists:
        with connection.schema_editor() as editor:
            editor.create_model(StaffMembership)
    yield


@pytest.mark.django_db
def test_staff_membership_unique_per_tenant():
    with staff_membership_table():
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username=f"user_{uuid.uuid4().hex[:8]}",
            email=f"user_{uuid.uuid4().hex[:8]}@example.com",
            password="testpass123",
        )
        StaffMembership.objects.create(user=user, role=StaffMembership.ROLE_STAFF)
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                StaffMembership.objects.create(
                    user=user,
                    role=StaffMembership.ROLE_MANAGER,
                )


def test_staff_membership_role_choices():
    valid_roles = {choice[0] for choice in StaffMembership.ROLE_CHOICES}
    assert StaffMembership.ROLE_MANAGER in valid_roles
    assert StaffMembership.ROLE_STAFF in valid_roles
