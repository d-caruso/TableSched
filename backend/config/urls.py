"""Tenant URL configuration."""

from django.urls import include, path
from django.urls.resolvers import URLPattern, URLResolver

urlpatterns: list[URLPattern | URLResolver] = [
    path("api/v1/", include("apps.bookings.urls")),
    path("api/v1/", include("apps.restaurants.urls")),
    path("api/v1/", include("apps.payments.urls")),
    path("api/v1/", include("apps.notifications.urls")),
]
