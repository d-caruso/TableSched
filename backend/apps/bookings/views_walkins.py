"""Staff walk-in API views."""

from django.shortcuts import get_object_or_404
from rest_framework import status as http_status  # type: ignore[import-untyped]
from rest_framework.decorators import action  # type: ignore[import-untyped]
from rest_framework import viewsets  # type: ignore[import-untyped]
from rest_framework.request import Request  # type: ignore[import-untyped]
from rest_framework.response import Response  # type: ignore[import-untyped]

from apps.bookings import services
from apps.bookings.models import Walkin, WalkinTableAssignment
from apps.bookings.serializers_walkins import WalkinSerializer
from apps.common.codes import ErrorCode
from apps.common.errors import DomainError
from apps.common.permissions import IsTenantMember
from apps.memberships.models import StaffMembership
from apps.restaurants.models import Table


class WalkinViewSet(viewsets.ModelViewSet):
    """Create-only walk-in endpoint for staff members."""

    permission_classes = [IsTenantMember]
    serializer_class = WalkinSerializer
    queryset = Walkin.objects.prefetch_related("table_assignments")

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        walkin = serializer.save()
        return Response(self.get_serializer(walkin).data, status=201)

    @action(
        detail=True,
        methods=["get", "put", "delete"],
        url_path=r"tables(?:/(?P<table_id>[^/.]+))?",
    )
    def tables(
        self,
        request: Request,
        pk: str | None = None,
        table_id: str | None = None,
    ) -> Response:
        walkin = self.get_object()
        if request.method == "GET":
            return Response({"tables": self._assigned_table_ids(walkin)})
        if request.method == "PUT":
            if table_id is not None:
                raise DomainError(ErrorCode.VALIDATION_FAILED, {"field": "table_id"})
            table_ids = request.data.get("tables")
            if not isinstance(table_ids, list):
                raise DomainError(ErrorCode.VALIDATION_FAILED, {"field": "tables"})
            tables = [get_object_or_404(Table, pk=value) for value in table_ids]
            services.replace_walkin_tables(
                walkin,
                tables=tables,
                by_membership=self._membership(request),
            )
            return Response({"tables": self._assigned_table_ids(walkin)})
        if table_id is None:
            raise DomainError(ErrorCode.VALIDATION_FAILED, {"field": "table_id"})
        table = get_object_or_404(Table, pk=table_id)
        services.remove_walkin_table(walkin, table=table)
        return Response(status=http_status.HTTP_204_NO_CONTENT)

    def _membership(self, request: Request) -> StaffMembership | None:
        membership = getattr(request, "membership", None)
        if isinstance(membership, StaffMembership):
            return membership
        return None

    def _assigned_table_ids(self, walkin: Walkin) -> list[str]:
        return [
            str(assignment.table.id)
            for assignment in WalkinTableAssignment.objects.filter(walkin=walkin).order_by(
                "created_at"
            ).select_related("table")
        ]
