"""Serializers for restaurant public endpoints."""

from rest_framework import serializers  # type: ignore[import-untyped]

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
