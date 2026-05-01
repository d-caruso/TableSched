"""Tests for the manual payment refund endpoint."""

from datetime import timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
from django.utils import timezone
from django_tenants.utils import schema_context  # type: ignore[import-untyped]
import stripe as stripe_sdk

from apps.accounts.models import User
from apps.bookings.models import Booking
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.payments.models import Payment, PaymentStatus


def _booking(schema_name: str) -> Booking:
    with schema_context(schema_name):
        suffix = uuid4().hex[:8]
        customer = Customer.objects.create(
            phone=f"+3900086{suffix}",
            email=f"refund-{suffix}@example.com",
            name="Refund Customer",
            locale="en",
        )
        return Booking.objects.create(
            customer=customer,
            starts_at=timezone.now() + timedelta(days=2),
            party_size=2,
        )


def _payment(booking: Booking, schema_name: str) -> Payment:
    with schema_context(schema_name):
        return Payment.objects.create(
            booking=booking,
            kind=Payment.KIND_PREAUTH,
            stripe_payment_intent_id="pi_refund",
            amount_cents=2500,
            currency="eur",
            status=PaymentStatus.CAPTURED,
        )


def _membership(schema_name: str, *, manager: bool) -> StaffMembership:
    with schema_context(schema_name):
        suffix = uuid4().hex[:8]
        role = "manager" if manager else "staff"
        user = User.objects.create_user(
            username=f"{role}_{suffix}",
            email=f"{role}-{suffix}@example.com",
            password="testpass123",
        )
        return StaffMembership.objects.create(
            user=user,
            role=StaffMembership.ROLE_MANAGER if manager else StaffMembership.ROLE_STAFF,
            is_active=True,
        )


@pytest.mark.django_db(transaction=True)
def test_refund_requires_manager_role(client, tenant_db):
    _tenant, schema_name, _domain = tenant_db
    prefix = f"/restaurants/{schema_name}"
    booking = _booking(schema_name)
    payment = _payment(booking, schema_name)
    membership = _membership(schema_name, manager=False)

    client.force_login(membership.user)
    response = client.post(f"{prefix}/api/v1/payments/{payment.id}/refunds/")

    assert response.status_code == 403
    with schema_context(schema_name):
        payment.refresh_from_db()
        assert payment.status == PaymentStatus.CAPTURED


@pytest.mark.django_db(transaction=True)
def test_refund_succeeds_for_manager(client, tenant_db):
    _tenant, schema_name, _domain = tenant_db
    prefix = f"/restaurants/{schema_name}"
    booking = _booking(schema_name)
    payment = _payment(booking, schema_name)
    membership = _membership(schema_name, manager=True)

    client.force_login(membership.user)
    refund_mock = Mock(return_value=Mock())
    with patch.object(stripe_sdk.Refund, "create", refund_mock):
        response = client.post(f"{prefix}/api/v1/payments/{payment.id}/refunds/")

    with schema_context(schema_name):
        payment.refresh_from_db()

    assert response.status_code == 200
    assert response.json()["id"] == str(payment.id)
    assert response.json()["status"] == PaymentStatus.REFUNDED
    assert payment.status == PaymentStatus.REFUNDED
    assert refund_mock.called
