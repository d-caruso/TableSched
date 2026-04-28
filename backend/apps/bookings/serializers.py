"""Serializers for booking API surfaces."""

from rest_framework import serializers  # type: ignore[import-untyped]

from apps.bookings.models import Booking


class BookingSerializer(serializers.ModelSerializer[Booking]):
    """Staff-facing serializer for booking CRUD and action responses."""

    class Meta:
        model = Booking
        fields = (
            "id",
            "customer",
            "starts_at",
            "party_size",
            "status",
            "table",
            "notes",
            "staff_message",
            "payment_due_at",
            "decided_at",
            "decided_by",
        )


class BookingPublicSerializer(serializers.ModelSerializer[Booking]):
    """Customer-facing booking shape for token-authenticated endpoints."""

    class Meta:
        model = Booking
        fields = ("id", "starts_at", "party_size", "status", "notes")
