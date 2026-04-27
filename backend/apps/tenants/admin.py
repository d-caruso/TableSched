"""Admin registrations for tenant public-schema models."""

from django.contrib import admin

from apps.tenants.models import Domain, Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("schema_name", "name", "is_active", "created_on")
    search_fields = ("schema_name", "name")
    list_filter = ("is_active",)


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "tenant", "is_primary")
    search_fields = ("domain", "tenant__schema_name", "tenant__name")
    list_filter = ("is_primary",)
