"""Tests for memberships models."""

import uuid

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db import transaction

from apps.memberships.models import StaffMembership
from tests.tenant_helpers import tenant_schema


@pytest.mark.django_db
def test_staff_membership_unique_per_tenant():
    with tenant_schema("membership_models"):
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
