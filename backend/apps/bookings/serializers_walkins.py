"""Walk-in serializers."""

from rest_framework import serializers  # type: ignore[import-untyped]

from apps.bookings.models import Walkin
from apps.restaurants.models import Table


class WalkinSerializer(serializers.ModelSerializer):
    """Serialize walk-in records."""

    table = serializers.PrimaryKeyRelatedField(
        queryset=Table.objects.all(),
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Walkin
        fields = ("id", "starts_at", "party_size", "table", "notes")
