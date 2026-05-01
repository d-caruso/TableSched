"""Walk-in serializers."""

from rest_framework import serializers  # type: ignore[import-untyped]

from apps.bookings.models import Walkin


class WalkinSerializer(serializers.ModelSerializer):
    """Serialize walk-in records."""

    tables = serializers.SerializerMethodField()

    def get_tables(self, obj: Walkin):
        assignments = getattr(obj, "table_assignments")
        return [assignment.table_id for assignment in assignments.all()]

    class Meta:
        model = Walkin
        fields = ("id", "starts_at", "party_size", "tables", "notes")
