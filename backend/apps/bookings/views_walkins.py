"""Staff walk-in API views."""

from rest_framework import viewsets  # type: ignore[import-untyped]
from rest_framework.request import Request  # type: ignore[import-untyped]
from rest_framework.response import Response  # type: ignore[import-untyped]

from apps.bookings.models import Walkin
from apps.bookings.serializers_walkins import WalkinSerializer
from apps.common.permissions import IsTenantMember


class WalkinViewSet(viewsets.ModelViewSet):
    """Create-only walk-in endpoint for staff members."""

    permission_classes = [IsTenantMember]
    serializer_class = WalkinSerializer
    queryset = Walkin.objects.all()

    def create(self, request: Request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        walkin = serializer.save()
        return Response(self.get_serializer(walkin).data, status=201)
