import django.db.models.deletion
import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("memberships", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AuditLog",
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
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="memberships.staffmembership",
                    ),
                ),
                ("action", models.CharField(max_length=64)),
                ("target_type", models.CharField(max_length=64)),
                ("target_id", models.UUIDField()),
                ("payload", models.JSONField(default=dict)),
            ],
        ),
    ]
