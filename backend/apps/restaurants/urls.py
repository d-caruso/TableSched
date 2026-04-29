"""Restaurants URL patterns."""

from django.urls import path
from django.urls.resolvers import URLPattern, URLResolver

from apps.restaurants.views import PublicRestaurantView, RestaurantSettingsView

app_name = "restaurants"
urlpatterns: list[URLPattern | URLResolver] = [
    path("public/restaurant/", PublicRestaurantView.as_view(), name="public-restaurant"),
    path("restaurant/settings/", RestaurantSettingsView.as_view(), name="restaurant-settings"),
]
