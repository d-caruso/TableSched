"""Admin registrations for memberships models."""

from django.contrib import admin

from apps.memberships.models import StaffMembership


@admin.register(StaffMembership)
class StaffMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "is_active", "created_at", "updated_at")
    list_filter = ("role", "is_active")
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user",)
