"""Add Stripe webhook dedupe table."""

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="StripeEvent",
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
                ("event_id", models.CharField(max_length=128, unique=True)),
                ("event_type", models.CharField(max_length=128)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
