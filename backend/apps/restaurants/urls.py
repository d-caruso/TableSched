"""Restaurants URL patterns."""

from django.urls import path
from django.urls.resolvers import URLPattern, URLResolver

from apps.restaurants.views import PublicRestaurantView

app_name = "restaurants"
urlpatterns: list[URLPattern | URLResolver] = [
    path("public/restaurant/", PublicRestaurantView.as_view(), name="public-restaurant"),
]
