"""Restaurants URL patterns."""

from django.urls.resolvers import URLPattern, URLResolver

app_name = "restaurants"
urlpatterns: list[URLPattern | URLResolver] = []
