"""Serializers for booking API surfaces."""

from rest_framework import serializers  # type: ignore[import-untyped]

from apps.bookings.models import Booking


class BookingPublicSerializer(serializers.ModelSerializer[Booking]):
    """Customer-facing booking shape for token-authenticated endpoints."""

    class Meta:
        model = Booking
        fields = ("id", "starts_at", "party_size", "status", "notes")
