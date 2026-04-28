import django.db.models.deletion
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("bookings", "0002_booking_status_set_and_table_fk"),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationLog",
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
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True),
                ),
                (
                    "booking",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="bookings.booking",
                    ),
                ),
                ("template_code", models.CharField(max_length=64)),
                ("locale", models.CharField(max_length=8)),
                (
                    "channel",
                    models.CharField(
                        choices=[("sms", "sms"), ("email", "email")],
                        max_length=16,
                    ),
                ),
                ("recipient", models.CharField(max_length=128)),
                ("status", models.CharField(max_length=16)),
                ("provider_message_id", models.CharField(blank=True, max_length=128)),
                ("error_code", models.CharField(blank=True, max_length=64)),
            ],
            options={},
        ),
    ]
