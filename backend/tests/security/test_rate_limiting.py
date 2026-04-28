"""Rate limiting regressions for public endpoints."""

from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIRequestFactory  # type: ignore[import-untyped]

from apps.bookings.models import Booking
from apps.bookings.views_customer import CustomerBookingView
from apps.customers.models import BookingAccessToken, Customer
from tests.tenant_helpers import tenant_schema


def _booking() -> Booking:
    customer = Customer.objects.create(
        phone="+3900099999",
        email="ratelimit@example.com",
        name="Rate Limit",
        locale="en",
    )
    return Booking.objects.create(
        customer=customer,
        starts_at=timezone.now() + timedelta(days=2),
        party_size=2,
    )


@pytest.mark.django_db(transaction=True)
def test_public_booking_endpoint_throttled():
    with tenant_schema("rate_limiting"):
        booking = _booking()
        _, raw = BookingAccessToken.issue(booking)
        factory = APIRequestFactory()
        response = None

        for _ in range(31):
            request = factory.get(f"/api/v1/public/bookings/{raw}/")
            request.META["REMOTE_ADDR"] = "127.0.0.42"
            response = CustomerBookingView.as_view()(request, raw_token=raw)
            if response.status_code == 429:
                break

    assert response is not None
    assert response.status_code == 429
