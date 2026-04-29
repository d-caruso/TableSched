"""Tests for the manual payment refund endpoint."""

from datetime import timedelta
from unittest.mock import Mock, patch
from uuid import uuid4

from django.utils import timezone
import stripe as stripe_sdk
from django_tenants.test.cases import FastTenantTestCase  # type: ignore[import-untyped]
from django_tenants.test.client import TenantClient  # type: ignore[import-untyped]

from apps.accounts.models import User
from apps.bookings.models import Booking
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.payments.models import Payment, PaymentStatus


class RefundEndpointTestCase(FastTenantTestCase):
    @classmethod
    def get_test_schema_name(cls) -> str:
        return "refund_test"

    @classmethod
    def get_test_tenant_domain(cls) -> str:
        return "refund.test.com"

    def _booking(self) -> Booking:
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

    def _payment(self, *, booking: Booking) -> Payment:
        return Payment.objects.create(
            booking=booking,
            kind=Payment.KIND_PREAUTH,
            stripe_payment_intent_id="pi_refund",
            amount_cents=2500,
            currency="eur",
            status=PaymentStatus.CAPTURED,
        )

    def _manager_membership(self) -> StaffMembership:
        suffix = uuid4().hex[:8]
        user = User.objects.create_user(
            username=f"manager_8_6_{suffix}",
            email=f"manager86-{suffix}@example.com",
            password="testpass123",
        )
        return StaffMembership.objects.create(
            user=user,
            role=StaffMembership.ROLE_MANAGER,
            is_active=True,
        )

    def _staff_membership(self) -> StaffMembership:
        suffix = uuid4().hex[:8]
        user = User.objects.create_user(
            username=f"staff_8_6_{suffix}",
            email=f"staff86-{suffix}@example.com",
            password="testpass123",
        )
        return StaffMembership.objects.create(
            user=user,
            role=StaffMembership.ROLE_STAFF,
            is_active=True,
        )

    def test_refund_requires_manager_role(self):
        booking = self._booking()
        payment = self._payment(booking=booking)
        membership = self._staff_membership()
        tenant_client = TenantClient(self.tenant)
        tenant_client.force_login(membership.user)

        response = tenant_client.post(f"/api/v1/payments/{payment.id}/refunds/")

        assert response.status_code == 403
        payment.refresh_from_db()
        assert payment.status == PaymentStatus.CAPTURED

    def test_refund_succeeds_for_manager(self):
        booking = self._booking()
        payment = self._payment(booking=booking)
        membership = self._manager_membership()
        tenant_client = TenantClient(self.tenant)
        tenant_client.force_login(membership.user)

        refund_mock = Mock(return_value=Mock())
        with patch.object(stripe_sdk.Refund, "create", refund_mock):
            response = tenant_client.post(f"/api/v1/payments/{payment.id}/refunds/")
        payment.refresh_from_db()

        assert response.status_code == 200
        assert response.json()["id"] == str(payment.id)
        assert response.json()["status"] == PaymentStatus.REFUNDED
        assert payment.status == PaymentStatus.REFUNDED
        assert refund_mock.called
