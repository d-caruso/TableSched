"""Staff booking API views."""

from typing import cast

from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework import viewsets  # type: ignore[import-untyped]
from rest_framework.decorators import action  # type: ignore[import-untyped]
from rest_framework.views import APIView  # type: ignore[import-untyped]
from rest_framework.request import Request  # type: ignore[import-untyped]
from rest_framework.response import Response  # type: ignore[import-untyped]

from apps.bookings import services
from apps.bookings.models import Booking
from apps.bookings.serializers import BookingSerializer
from apps.bookings.services import opportunistic_maintenance
from apps.common.codes import ErrorCode
from apps.common.errors import DomainError
from apps.common.permissions import IsTenantMember
from apps.memberships.models import StaffMembership
from apps.restaurants.models import RestaurantSettings, Table


class BookingViewSet(viewsets.ModelViewSet):
    """Thin staff endpoints delegating domain logic to services."""

    permission_classes = [IsTenantMember]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.select_related("customer").prefetch_related("table_assignments")

    @action(detail=True, methods=["post"], url_path="approve")
    def approve(self, request: Request, pk: str | None = None) -> Response:
        booking = self.get_object()
        services.approve(
            booking,
            by_membership=self._membership(request),
            settings=RestaurantSettings.objects.get(),
        )
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=["post"], url_path="decline")
    def decline(self, request: Request, pk: str | None = None) -> Response:
        booking = self.get_object()
        services.decline(
            booking,
            by_membership=self._membership(request),
            reason_code=request.data.get("reason_code", ""),
            staff_message=request.data.get("staff_message", ""),
        )
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=["post"], url_path="modify")
    def modify(self, request: Request, pk: str | None = None) -> Response:
        booking = self.get_object()
        table = None
        table_id = request.data.get("table")
        if table_id:
            table = get_object_or_404(Table, pk=table_id)

        services.modify_by_staff(
            booking,
            by_membership=self._membership(request),
            starts_at=request.data.get("starts_at"),
            party_size=request.data.get("party_size"),
            notes=request.data.get("notes"),
            table=table,
        )
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=["post"], url_path="assign-table")
    def assign_table(self, request: Request, pk: str | None = None) -> Response:
        booking = self.get_object()
        table_id = request.data.get("table")
        if not table_id:
            raise DomainError(ErrorCode.VALIDATION_FAILED, {"field": "table"})
        table = get_object_or_404(Table, pk=table_id)
        services.assign_table(booking, by_membership=self._membership(request), table=table)
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=["post"], url_path="mark-no-show")
    def mark_no_show(self, request: Request, pk: str | None = None) -> Response:
        booking = self.get_object()
        services.mark_no_show(booking, by_membership=self._membership(request))
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=["post"], url_path="confirm-without-deposit")
    def confirm_without_deposit(self, request: Request, pk: str | None = None) -> Response:
        booking = self.get_object()
        services.confirm_without_deposit(booking, by_membership=self._membership(request))
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=["post"], url_path="request-payment")
    def request_payment(self, request: Request, pk: str | None = None) -> Response:
        booking = self.get_object()
        services.request_payment_again(
            booking,
            by_membership=self._membership(request),
            settings=RestaurantSettings.objects.get(),
        )
        return Response(self.get_serializer(booking).data)

    def _membership(self, request: Request) -> StaffMembership:
        return cast(StaffMembership, getattr(request, "membership", None))


class AdminDashboardView(APIView):
    """Tenant dashboard endpoint that runs opportunistic maintenance."""

    permission_classes = [IsTenantMember]

    def get(self, request: Request) -> Response:
        opportunistic_maintenance.run_opportunistic_maintenance()
        return Response(
            {
                "counts_by_status": _counts_by_status(),
                "recent": list(
                    Booking.objects.order_by("-created_at")[:50].values(
                        "id",
                        "status",
                        "starts_at",
                        "party_size",
                    )
                ),
            }
        )


def _counts_by_status() -> dict[str, int]:
    return {
        row["status"]: row["count"]
        for row in Booking.objects.values("status").annotate(count=Count("id"))
    }
