"""Tests for Stripe webhook handling."""

from collections.abc import Iterator
from contextlib import contextmanager
from datetime import timedelta

import pytest
from django.db import connection
from django.utils import timezone
import stripe as stripe_sdk

from apps.accounts.models import User
from apps.bookings.models import Booking, BookingStatus
from apps.customers.models import Customer
from apps.memberships.models import StaffMembership
from apps.payments.models import Payment, PaymentStatus, StripeEvent
from apps.restaurants.models import RestaurantSettings, Room, Table


@contextmanager
def webhook_tables() -> Iterator[None]:
    existing_tables = set(connection.introspection.table_names())
    models_in_order = (
        User,
        Customer,
        StaffMembership,
        Room,
        Table,
        RestaurantSettings,
        Booking,
        Payment,
        StripeEvent,
    )
    for model in models_in_order:
        if model._meta.db_table not in existing_tables:
            with connection.schema_editor() as editor:
                editor.create_model(model)
            existing_tables.add(model._meta.db_table)
    yield


def _booking() -> Booking:
    customer = Customer.objects.create(
        phone="+3900085000",
        email="webhook@example.com",
        name="Webhook Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
    )


def _payment(booking: Booking) -> Payment:
    return Payment.objects.create(
        booking=booking,
        kind=Payment.KIND_PREAUTH,
        stripe_payment_intent_id="pi_123",
        stripe_checkout_session_id="cs_123",
        amount_cents=2500,
        status=PaymentStatus.PENDING,
    )


def _event(*, event_id: str, event_type: str, object_data: dict) -> dict:
    return {
        "id": event_id,
        "type": event_type,
        "data": {"object": object_data},
    }


@pytest.mark.django_db
def test_unsigned_webhook_returns_400(client):
    with webhook_tables():
        response = client.post(
            "/stripe/webhook/",
            data=b"{}",
            content_type="application/json",
        )
    assert response.status_code == 400


@pytest.mark.django_db
def test_missing_tenant_schema_returns_400(client, monkeypatch):
    with webhook_tables():
        monkeypatch.setattr(
            stripe_sdk.Webhook,
            "construct_event",
            lambda payload, sig, secret: _event(
                event_id="evt_1",
                event_type="payment_intent.payment_failed",
                object_data={"id": "pi_1", "metadata": {}},
            ),
        )
        response = client.post(
            "/stripe/webhook/",
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
    assert response.status_code == 400


@pytest.mark.django_db
def test_payment_intent_capturable_sets_authorized(client, monkeypatch):
    with webhook_tables():
        booking = _booking()
        payment = _payment(booking)
        event = _event(
            event_id="evt_2",
            event_type="payment_intent.amount_capturable_updated",
            object_data={
                "id": payment.stripe_payment_intent_id,
                "metadata": {"tenant_schema": connection.schema_name},
            },
        )
        monkeypatch.setattr(stripe_sdk.Webhook, "construct_event", lambda payload, sig, secret: event)

        response = client.post(
            "/stripe/webhook/",
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        payment.refresh_from_db()

    assert response.status_code == 200
    assert payment.status == PaymentStatus.AUTHORIZED


@pytest.mark.django_db
def test_checkout_session_completed_confirms_booking(client, monkeypatch):
    with webhook_tables():
        booking = _booking()
        payment = _payment(booking)
        event = _event(
            event_id="evt_3",
            event_type="checkout.session.completed",
            object_data={
                "id": payment.stripe_checkout_session_id,
                "metadata": {"tenant_schema": connection.schema_name},
            },
        )
        monkeypatch.setattr(stripe_sdk.Webhook, "construct_event", lambda payload, sig, secret: event)

        response = client.post(
            "/stripe/webhook/",
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        payment.refresh_from_db()
        booking.refresh_from_db()

    assert response.status_code == 200
    assert payment.status == PaymentStatus.CAPTURED
    assert booking.status == BookingStatus.CONFIRMED


@pytest.mark.django_db
def test_webhook_is_idempotent(client, monkeypatch):
    with webhook_tables():
        booking = _booking()
        payment = _payment(booking)
        event = _event(
            event_id="evt_4",
            event_type="payment_intent.amount_capturable_updated",
            object_data={
                "id": payment.stripe_payment_intent_id,
                "metadata": {"tenant_schema": connection.schema_name},
            },
        )
        monkeypatch.setattr(stripe_sdk.Webhook, "construct_event", lambda payload, sig, secret: event)

        response_1 = client.post(
            "/stripe/webhook/",
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        response_2 = client.post(
            "/stripe/webhook/",
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        payment.refresh_from_db()

    assert response_1.status_code == 200
    assert response_2.status_code == 200
    assert payment.status == PaymentStatus.AUTHORIZED
    assert StripeEvent.objects.filter(event_id="evt_4").count() == 1
