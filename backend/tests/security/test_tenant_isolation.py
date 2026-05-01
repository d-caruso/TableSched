"""Tenant isolation security regressions."""

from datetime import timedelta

import pytest
from django.utils import timezone
from django_tenants.utils import schema_context  # type: ignore[import-untyped]
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]
import stripe as stripe_sdk

from apps.accounts.models import User
from apps.bookings.models import Booking, BookingStatus
from apps.customers.models import BookingAccessToken, Customer
from apps.memberships.models import StaffMembership
from apps.payments.models import Payment, PaymentStatus
from apps.payments.views import stripe_webhook
from tests.tenant_helpers import tenant_schema


def _customer(phone_suffix: str) -> Customer:
    return Customer.objects.create(
        phone=f"+3900200{phone_suffix}",
        email=f"security-{phone_suffix}@example.com",
        name=f"Security {phone_suffix}",
        locale="en",
    )


def _booking(phone_suffix: str, *, status: str = BookingStatus.PENDING_REVIEW) -> Booking:
    return Booking.objects.create(
        customer=_customer(phone_suffix),
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
        status=status,
    )


def _membership(username: str) -> StaffMembership:
    user = User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="testpass123",
    )
    return StaffMembership.objects.create(
        user=user,
        role=StaffMembership.ROLE_MANAGER,
        is_active=True,
    )


def _payment(booking: Booking, *, intent_id: str, session_id: str) -> Payment:
    return Payment.objects.create(
        booking=booking,
        kind=Payment.KIND_PREAUTH,
        stripe_payment_intent_id=intent_id,
        stripe_checkout_session_id=session_id,
        amount_cents=2500,
        currency="eur",
        status=PaymentStatus.PENDING,
    )


@pytest.mark.django_db(transaction=True)
def test_staff_cannot_read_other_tenant_bookings(client):
    with tenant_schema("security_a") as (tenant_a, _schema_a, _domain_a):
        membership_a = _membership("security_a_staff")
        booking_a = _booking("a")
        client.force_login(membership_a.user)

    with tenant_schema("security_b") as (tenant_b, _schema_b, _domain_b):
        _booking("b")
        response = client.get(f"/restaurants/{_schema_b}/api/v1/bookings/")

    assert response.status_code in (403, 404)
    with schema_context(tenant_a.schema_name):
        assert Booking.objects.filter(pk=booking_a.pk).exists()


@pytest.mark.django_db(transaction=True)
def test_webhook_cannot_affect_wrong_tenant(monkeypatch):
    with tenant_schema("security_webhook_a") as (tenant_a, schema_a, _domain_a):
        booking_a = _booking("wa")
        payment_a = _payment(booking_a, intent_id="pi_a", session_id="cs_a")

    with tenant_schema("security_webhook_b") as (_tenant_b, schema_b, _domain_b):
        booking_b = _booking("wb")
        payment_b = _payment(booking_b, intent_id="pi_b", session_id="cs_b")
        event = {
            "id": "evt_security_b",
            "type": "payment_intent.amount_capturable_updated",
            "data": {
                "object": {
                    "id": payment_b.stripe_payment_intent_id,
                    "metadata": {"tenant_schema": schema_b},
                }
            },
        }
        monkeypatch.setattr(stripe_sdk.Webhook, "construct_event", lambda payload, sig, secret: event)

    request = APIRequestFactory().post(
        "/stripe/webhook/",
        data=b"{}",
        content_type="application/json",
        HTTP_STRIPE_SIGNATURE="sig",
    )
    response = stripe_webhook(request)

    assert response.status_code == 200
    with schema_context(schema_a):
        payment_a.refresh_from_db()
        booking_a.refresh_from_db()
        assert payment_a.status == PaymentStatus.PENDING
        assert booking_a.status == BookingStatus.PENDING_REVIEW


@pytest.mark.django_db(transaction=True)
def test_token_from_tenant_a_invalid_on_tenant_b(client):
    with tenant_schema("security_token_a") as (tenant_a, schema_a, domain_a):
        booking_a = _booking("ta")
        _, raw_token_a = BookingAccessToken.issue(booking_a)

    with tenant_schema("security_token_b") as (tenant_b, schema_b, domain_b):
        _booking("tb")
        response = client.get(f"/restaurants/{schema_b}/api/v1/public/bookings/{raw_token_a}/")

    assert response.status_code in (404, 410)
    with schema_context(schema_a):
        assert BookingAccessToken.objects.filter(booking=booking_a).exists()
