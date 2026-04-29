"""Serializers for restaurant endpoints."""

from rest_framework import serializers  # type: ignore[import-untyped]

from apps.restaurants.models import ClosedDay
from apps.restaurants.models import OpeningHours as OpeningWindow
from apps.restaurants.models import RestaurantSettings


class OpeningHoursPublicSerializer(serializers.Serializer):
    """Code-only opening-hours representation."""

    weekday = serializers.IntegerField()
    opens_at = serializers.TimeField(format="%H:%M:%S")
    closes_at = serializers.TimeField(format="%H:%M:%S")


class PublicRestaurantSerializer(serializers.Serializer):
    """Public response payload for restaurant info endpoint."""

    name = serializers.CharField(allow_blank=True)
    deposit_policy = serializers.ChoiceField(choices=RestaurantSettings.DEPOSIT_POLICY)
    deposit_party_threshold = serializers.IntegerField(allow_null=True)
    deposit_amount_cents = serializers.IntegerField()
    near_term_threshold_hours = serializers.IntegerField()
    long_term_payment_window_hours = serializers.IntegerField()
    cancellation_cutoff_hours = serializers.IntegerField()
    booking_cutoff_minutes = serializers.IntegerField()
    advance_booking_days = serializers.IntegerField()
    opening_hours = OpeningHoursPublicSerializer(many=True)


class RestaurantSettingsSerializer(serializers.ModelSerializer[RestaurantSettings]):
    """Tenant restaurant booking and deposit settings."""

    class Meta:
        model = RestaurantSettings
        fields = (
            "deposit_policy",
            "deposit_party_threshold",
            "deposit_amount_cents",
            "near_term_threshold_hours",
            "long_term_payment_window_hours",
            "cancellation_cutoff_hours",
            "booking_cutoff_minutes",
            "advance_booking_days",
        )


class OpeningWindowSerializer(serializers.ModelSerializer[OpeningWindow]):
    """Tenant restaurant weekly opening window."""

    class Meta:
        model = OpeningWindow
        fields = ("id", "weekday", "opens_at", "closes_at")

    def validate_weekday(self, value: int) -> int:
        if value < 0 or value > 6:
            raise serializers.ValidationError("invalid")
        return value

    def validate(self, attrs):
        opens_at = attrs.get("opens_at", getattr(self.instance, "opens_at", None))
        closes_at = attrs.get("closes_at", getattr(self.instance, "closes_at", None))
        if opens_at is not None and closes_at is not None and opens_at >= closes_at:
            raise serializers.ValidationError({"closes_at": "invalid"})
        return attrs


class ClosedDaySerializer(serializers.ModelSerializer[ClosedDay]):
    """Tenant one-off closed day."""

    class Meta:
        model = ClosedDay
        fields = ("id", "date", "reason_code")
