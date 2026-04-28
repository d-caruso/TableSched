"""Views for restaurant public APIs."""

from rest_framework.request import Request  # type: ignore[import-untyped]
from rest_framework.response import Response  # type: ignore[import-untyped]
from rest_framework.views import APIView  # type: ignore[import-untyped]

from apps.restaurants.models import OpeningHours, RestaurantSettings
from apps.restaurants.serializers import PublicRestaurantSerializer


class PublicRestaurantView(APIView):
    """Unauthenticated endpoint with public restaurant configuration."""

    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request: Request) -> Response:
        settings_obj, _ = RestaurantSettings.objects.get_or_create()
        opening_hours = list(
            OpeningHours.objects.order_by("weekday", "opens_at").values(
                "weekday", "opens_at", "closes_at"
            )
        )
        payload = {
            "name": getattr(getattr(request, "tenant", None), "name", ""),
            "deposit_policy": settings_obj.deposit_policy,
            "deposit_party_threshold": settings_obj.deposit_party_threshold,
            "deposit_amount_cents": settings_obj.deposit_amount_cents,
            "near_term_threshold_hours": settings_obj.near_term_threshold_hours,
            "long_term_payment_window_hours": settings_obj.long_term_payment_window_hours,
            "cancellation_cutoff_hours": settings_obj.cancellation_cutoff_hours,
            "booking_cutoff_minutes": settings_obj.booking_cutoff_minutes,
            "advance_booking_days": settings_obj.advance_booking_days,
            "opening_hours": opening_hours,
        }
        serializer = PublicRestaurantSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)
