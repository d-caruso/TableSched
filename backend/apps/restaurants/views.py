"""Views for restaurant APIs."""

from rest_framework.request import Request  # type: ignore[import-untyped]
from rest_framework.response import Response  # type: ignore[import-untyped]
from rest_framework.views import APIView  # type: ignore[import-untyped]
from rest_framework import generics  # type: ignore[import-untyped]

from apps.common.permissions import IsManager, IsTenantMember
from apps.restaurants.models import ClosedDay, OpeningHours, RestaurantSettings, Room, Table
from apps.restaurants.serializers import (
    ClosedDaySerializer,
    OpeningWindowSerializer,
    PublicRestaurantSerializer,
    RestaurantSettingsSerializer,
    RoomSerializer,
    TableSerializer,
)


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


class RestaurantSettingsView(APIView):
    """Tenant-member endpoint for singleton restaurant settings."""

    def get_permissions(self):
        if self.request.method == "PATCH":
            return [IsManager()]
        return [IsTenantMember()]

    def get(self, request: Request) -> Response:
        settings_obj = self._settings()
        return Response(RestaurantSettingsSerializer(settings_obj).data)

    def patch(self, request: Request) -> Response:
        settings_obj = self._settings()
        serializer = RestaurantSettingsSerializer(settings_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def _settings(self) -> RestaurantSettings:
        settings_obj, _created = RestaurantSettings.objects.get_or_create()
        return settings_obj


class OpeningWindowListCreateView(generics.ListCreateAPIView):
    """Tenant opening-window collection endpoint."""

    serializer_class = OpeningWindowSerializer

    def get_queryset(self):
        return OpeningHours.objects.order_by("weekday", "opens_at")

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsManager()]
        return [IsTenantMember()]


class OpeningWindowDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Tenant opening-window detail endpoint."""

    serializer_class = OpeningWindowSerializer
    lookup_url_kwarg = "pk"
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return OpeningHours.objects.order_by("weekday", "opens_at")

    def get_permissions(self):
        if self.request.method in {"PATCH", "DELETE"}:
            return [IsManager()]
        return [IsTenantMember()]


class ClosedDayListCreateView(generics.ListCreateAPIView):
    """Tenant closed-day collection endpoint."""

    serializer_class = ClosedDaySerializer

    def get_queryset(self):
        return ClosedDay.objects.order_by("date")

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsManager()]
        return [IsTenantMember()]


class ClosedDayDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Tenant closed-day detail endpoint."""

    serializer_class = ClosedDaySerializer
    lookup_url_kwarg = "pk"
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return ClosedDay.objects.order_by("date")

    def get_permissions(self):
        if self.request.method in {"PATCH", "DELETE"}:
            return [IsManager()]
        return [IsTenantMember()]


class RoomListCreateView(generics.ListCreateAPIView):
    """Tenant room collection endpoint."""

    serializer_class = RoomSerializer

    def get_queryset(self):
        return Room.objects.order_by("name")

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsManager()]
        return [IsTenantMember()]


class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Tenant room detail endpoint."""

    serializer_class = RoomSerializer
    lookup_url_kwarg = "pk"
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return Room.objects.order_by("name")

    def get_permissions(self):
        if self.request.method in {"PATCH", "DELETE"}:
            return [IsManager()]
        return [IsTenantMember()]


class TableListCreateView(generics.ListCreateAPIView):
    """Tenant table collection endpoint."""

    serializer_class = TableSerializer

    def get_queryset(self):
        return Table.objects.select_related("room").order_by("room__name", "label")

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsManager()]
        return [IsTenantMember()]


class TableDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Tenant table detail endpoint."""

    serializer_class = TableSerializer
    lookup_url_kwarg = "pk"
    http_method_names = ["get", "patch", "delete", "head", "options"]

    def get_queryset(self):
        return Table.objects.select_related("room").order_by("room__name", "label")

    def get_permissions(self):
        if self.request.method in {"PATCH", "DELETE"}:
            return [IsManager()]
        return [IsTenantMember()]
