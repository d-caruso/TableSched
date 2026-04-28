from datetime import timedelta

import pytest
from django.utils import timezone

from apps.bookings.models import Booking
from apps.customers.models import Customer
from tests.tenant_helpers import tenant_schema


def _booking(*, email: str = "") -> Booking:
    customer = Customer.objects.create(
        phone="+39123456789",
        email=email,
        name="Notification Customer",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=1),
        party_size=2,
    )


@pytest.mark.django_db
def test_sms_always_sent(monkeypatch):
    with tenant_schema("notifications_routing"):
        from apps.notifications import services

        calls: list[tuple] = []

        def fake_send_sms(*args):
            calls.append(args)

        def fake_send_email(*args):
            raise AssertionError("email should not be sent")

        monkeypatch.setattr(services, "_send_sms", fake_send_sms)
        monkeypatch.setattr(services, "_send_email", fake_send_email)

        services.notify_customer(_booking(), "booking_approved")

        assert len(calls) == 1


@pytest.mark.django_db
def test_email_sent_when_email_present(monkeypatch):
    with tenant_schema("notifications_routing"):
        from apps.notifications import services

        email_calls: list[tuple] = []

        monkeypatch.setattr(services, "_send_sms", lambda *args: None)
        monkeypatch.setattr(services, "_send_email", lambda *args: email_calls.append(args))

        services.notify_customer(_booking(email="guest@example.com"), "booking_approved")

        assert len(email_calls) == 1


@pytest.mark.django_db
def test_email_not_sent_when_no_email(monkeypatch):
    with tenant_schema("notifications_routing"):
        from apps.notifications import services

        email_calls: list[tuple] = []

        monkeypatch.setattr(services, "_send_sms", lambda *args: None)
        monkeypatch.setattr(services, "_send_email", lambda *args: email_calls.append(args))

        services.notify_customer(_booking(), "booking_approved")

        assert email_calls == []
