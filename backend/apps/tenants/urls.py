"""Tenant URL configuration."""

from django.urls import path

from apps.tenants.views import tenant_directory

urlpatterns = [
    path("api/tenants/", tenant_directory, name="tenant-directory"),
]
