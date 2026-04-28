import django.db.models.deletion
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bookings", "0002_booking_status_set_and_table_fk"),
        ("restaurants", "0003_room_table"),
    ]

    operations = [
        migrations.CreateModel(
            name="Walkin",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("starts_at", models.DateTimeField()),
                ("party_size", models.PositiveSmallIntegerField()),
                ("notes", models.TextField(blank=True)),
                (
                    "table",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="restaurants.table",
                    ),
                ),
            ],
        ),
    ]
