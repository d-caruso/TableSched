"""Restaurants URL patterns."""

from django.urls import path
from django.urls.resolvers import URLPattern, URLResolver

from apps.restaurants.views import (
    OpeningWindowDetailView,
    OpeningWindowListCreateView,
    PublicRestaurantView,
    RestaurantSettingsView,
)

app_name = "restaurants"
urlpatterns: list[URLPattern | URLResolver] = [
    path("public/restaurant/", PublicRestaurantView.as_view(), name="public-restaurant"),
    path("restaurant/settings/", RestaurantSettingsView.as_view(), name="restaurant-settings"),
    path(
        "restaurant/opening-windows/",
        OpeningWindowListCreateView.as_view(),
        name="opening-windows",
    ),
    path(
        "restaurant/opening-windows/<uuid:pk>/",
        OpeningWindowDetailView.as_view(),
        name="opening-window-detail",
    ),
]
