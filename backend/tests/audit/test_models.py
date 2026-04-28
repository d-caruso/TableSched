"""Tests for audit log model."""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.audit.models import AuditLog
from apps.bookings.models import Booking
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from tests.tenant_helpers import tenant_schema


def _membership() -> StaffMembership:
    user = User.objects.create_user(
        username="audit_manager",
        email="audit@example.com",
        password="testpass123",
    )
    return StaffMembership.objects.create(
        user=user,
        role=StaffMembership.ROLE_MANAGER,
        is_active=True,
    )


def _booking() -> Booking:
    customer = Customer.objects.create(
        phone="+3900123456",
        email="audit-customer@example.com",
        name="Audit Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=1),
        party_size=2,
    )


@pytest.mark.django_db
def test_audit_log_fields():
    with tenant_schema("audit"):
        membership = _membership()
        booking = _booking()

        log = AuditLog.objects.create(
            actor=membership,
            action="booking.approve",
            target_type="Booking",
            target_id=booking.id,
            payload={"to_status": "confirmed"},
        )

        assert log.action == "booking.approve"
        assert log.payload["to_status"] == "confirmed"
