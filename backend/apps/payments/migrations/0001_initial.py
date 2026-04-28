"""Initial payment schema."""

import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("bookings", "0002_booking_status_set_and_table_fk"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("kind", models.CharField(choices=[("preauth", "preauth"), ("link", "link")], max_length=16)),
                ("stripe_payment_intent_id", models.CharField(blank=True, db_index=True, max_length=128)),
                ("stripe_checkout_session_id", models.CharField(blank=True, db_index=True, max_length=128)),
                ("amount_cents", models.PositiveIntegerField()),
                ("currency", models.CharField(default="eur", max_length=8)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "pending"),
                            ("authorized", "authorized"),
                            ("captured", "captured"),
                            ("failed", "failed"),
                            ("refund_pending", "refund_pending"),
                            ("refunded", "refunded"),
                            ("refund_failed", "refund_failed"),
                        ],
                        default="pending",
                        max_length=32,
                    ),
                ),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                (
                    "booking",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="bookings.booking",
                    ),
                ),
            ],
        ),
    ]
