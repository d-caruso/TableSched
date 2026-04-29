"""Tenant-schema booking models."""

from django.db import models

from apps.common.models import TimeStampedModel


class BookingStatus(models.TextChoices):
    PENDING_REVIEW = "pending_review"
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    CONFIRMED_WITHOUT_DEPOSIT = "confirmed_without_deposit"
    DECLINED = "declined"
    CANCELLED_BY_CUSTOMER = "cancelled_by_customer"
    CANCELLED_BY_STAFF = "cancelled_by_staff"
    NO_SHOW = "no_show"
    EXPIRED = "expired"
    AUTHORIZATION_EXPIRED = "authorization_expired"


class Booking(TimeStampedModel):
    """Booking record used by staff and customer token flows."""

    customer: models.ForeignKey = models.ForeignKey("customers.Customer", on_delete=models.PROTECT)
    starts_at: models.DateTimeField = models.DateTimeField()
    party_size: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField()
    status: models.CharField = models.CharField(
        max_length=32,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING_REVIEW,
    )
    notes: models.TextField = models.TextField(blank=True)
    staff_message: models.TextField = models.TextField(blank=True)
    payment_due_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    decided_at: models.DateTimeField = models.DateTimeField(null=True, blank=True)
    decided_by: models.ForeignKey = models.ForeignKey(
        "memberships.StaffMembership",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        indexes = [models.Index(fields=["status", "starts_at"])]


class BookingTableAssignment(TimeStampedModel):
    """Manual table assignment for a booking."""

    booking: models.ForeignKey = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="table_assignments",
    )
    table: models.ForeignKey = models.ForeignKey(
        "restaurants.Table",
        on_delete=models.CASCADE,
        related_name="booking_assignments",
    )
    assigned_by: models.ForeignKey = models.ForeignKey(
        "memberships.StaffMembership",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["booking", "table"],
                name="uniq_booking_table_assignment",
            )
        ]


class Walkin(TimeStampedModel):
    """Staff-only in-person reservation record."""

    starts_at: models.DateTimeField = models.DateTimeField()
    party_size: models.PositiveSmallIntegerField = models.PositiveSmallIntegerField()
    table: models.ForeignKey = models.ForeignKey(
        "restaurants.Table",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    notes: models.TextField = models.TextField(blank=True)
