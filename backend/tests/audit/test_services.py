"""Tests for audit service helpers."""

import pytest

from apps.accounts.models import User
from apps.audit.models import AuditLog
from apps.audit.services import record
from apps.bookings.models import Booking
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from tests.tenant_helpers import tenant_schema


def _membership() -> StaffMembership:
    user = User.objects.create_user(
        username="audit_service_manager",
        email="audit-service@example.com",
        password="testpass123",
    )
    return StaffMembership.objects.create(
        user=user,
        role=StaffMembership.ROLE_MANAGER,
        is_active=True,
    )


def _booking() -> Booking:
    customer = Customer.objects.create(
        phone="+3900987654",
        email="audit-service-customer@example.com",
        name="Audit Service Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at="2025-01-01T12:00:00Z",
        party_size=2,
    )


@pytest.mark.django_db
def test_record_creates_audit_log():
    with tenant_schema("audit_service"):
        membership = _membership()
        booking = _booking()

        log = record(
            actor=membership,
            action="booking.decline",
            target=booking,
            payload={"reason_code": "staff_rejection_generic"},
        )

        stored = AuditLog.objects.get(action="booking.decline")
        assert stored.id == log.id
        assert stored.target_id == booking.id
        assert stored.payload["reason_code"] == "staff_rejection_generic"


@pytest.mark.django_db
def test_record_with_no_payload():
    with tenant_schema("audit_service"):
        membership = _membership()
        booking = _booking()

        log = record(actor=membership, action="booking.approve", target=booking)

        assert log.payload == {}
