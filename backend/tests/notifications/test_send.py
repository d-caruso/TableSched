from datetime import timedelta
from types import SimpleNamespace

import pytest
from django.utils import timezone
from twilio.base.exceptions import TwilioRestException  # type: ignore[import-untyped]

from apps.bookings.models import Booking
from apps.customers.models import Customer
from apps.notifications.models import NotificationLog
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
def test_sms_failure_does_not_raise(monkeypatch):
    with tenant_schema("notifications_send"):
        from apps.notifications import services
        from apps.notifications import twilio_client

        monkeypatch.setattr(
            twilio_client.client.messages,
            "create",
            lambda **kwargs: (_ for _ in ()).throw(
                TwilioRestException(500, "", "boom", code=123)
            ),
        )

        services._send_sms(_booking(), "booking_approved", "en", "+39123", {})


@pytest.mark.django_db
def test_sms_failure_logs_failed_status(monkeypatch):
    with tenant_schema("notifications_send"):
        from apps.notifications import services
        from apps.notifications import twilio_client

        monkeypatch.setattr(
            twilio_client.client.messages,
            "create",
            lambda **kwargs: (_ for _ in ()).throw(
                TwilioRestException(500, "", "boom", code=123)
            ),
        )

        booking = _booking()
        services._send_sms(booking, "booking_approved", "en", "+39123", {})

        log = NotificationLog.objects.get(booking=booking, channel="sms")
        assert log.status == "failed"


@pytest.mark.django_db
def test_email_failure_does_not_raise(monkeypatch):
    with tenant_schema("notifications_send"):
        from apps.notifications import services

        monkeypatch.setattr(
            services,
            "send_mail",
            lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")),
        )

        services._send_email(_booking(email="a@b.com"), "booking_approved", "en", "a@b.com", {})


@pytest.mark.django_db
def test_sms_success_logs_sent_status(monkeypatch):
    with tenant_schema("notifications_send"):
        from apps.notifications import services
        from apps.notifications import twilio_client

        monkeypatch.setattr(
            twilio_client.client.messages,
            "create",
            lambda **kwargs: SimpleNamespace(sid="SM123"),
        )

        booking = _booking()
        services._send_sms(booking, "booking_approved", "en", "+39123", {})

        log = NotificationLog.objects.get(booking=booking, channel="sms")
        assert log.status == "sent"
