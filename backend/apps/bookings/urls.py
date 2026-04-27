"""Bookings URL patterns."""

from django.urls.resolvers import URLPattern, URLResolver

app_name = "bookings"
urlpatterns: list[URLPattern | URLResolver] = []
