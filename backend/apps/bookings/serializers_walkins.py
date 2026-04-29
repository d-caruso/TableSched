"""Walk-in serializers."""

from rest_framework import serializers  # type: ignore[import-untyped]

from apps.bookings.models import Walkin


class WalkinSerializer(serializers.ModelSerializer):
    """Serialize walk-in records."""

    table = serializers.SerializerMethodField()

    def get_table(self, obj: Walkin):
        assignments = getattr(obj, "table_assignments")
        assignment = next(iter(assignments.all()), None)
        if assignment is None:
            return None
        return assignment.table_id

    class Meta:
        model = Walkin
        fields = ("id", "starts_at", "party_size", "table", "notes")
