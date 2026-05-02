"""Restaurants URL patterns."""

from django.urls import path
from django.urls.resolvers import URLPattern, URLResolver

from apps.restaurants.views import (
    ClosedDayDetailView,
    ClosedDayListCreateView,
    OpeningWindowDetailView,
    OpeningWindowListCreateView,
    PublicRestaurantView,
    RestaurantSettingsView,
    RoomDetailView,
    RoomListCreateView,
    TableDetailView,
    TableListCreateView,
)

app_name = "restaurants"
urlpatterns: list[URLPattern | URLResolver] = [
    path("public/", PublicRestaurantView.as_view(), name="public-restaurant"),
    path("settings/", RestaurantSettingsView.as_view(), name="restaurant-settings"),
    path("opening-windows/", OpeningWindowListCreateView.as_view(), name="opening-windows"),
    path(
        "opening-windows/<uuid:pk>/",
        OpeningWindowDetailView.as_view(),
        name="opening-window-detail",
    ),
    path("closed-days/", ClosedDayListCreateView.as_view(), name="closed-days"),
    path("closed-days/<uuid:pk>/", ClosedDayDetailView.as_view(), name="closed-day-detail"),
    path("rooms/", RoomListCreateView.as_view(), name="rooms"),
    path("rooms/<uuid:pk>/", RoomDetailView.as_view(), name="room-detail"),
    path("tables/", TableListCreateView.as_view(), name="tables"),
    path("tables/<uuid:pk>/", TableDetailView.as_view(), name="table-detail"),
]
