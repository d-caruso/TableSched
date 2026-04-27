"""Payments URL patterns."""

from django.urls.resolvers import URLPattern, URLResolver

app_name = "payments"
urlpatterns: list[URLPattern | URLResolver] = []
