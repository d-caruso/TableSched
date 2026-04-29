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
    path("restaurant/closed-days/", ClosedDayListCreateView.as_view(), name="closed-days"),
    path(
        "restaurant/closed-days/<uuid:pk>/",
        ClosedDayDetailView.as_view(),
        name="closed-day-detail",
    ),
    path("restaurant/rooms/", RoomListCreateView.as_view(), name="rooms"),
    path("restaurant/rooms/<uuid:pk>/", RoomDetailView.as_view(), name="room-detail"),
    path("restaurant/tables/", TableListCreateView.as_view(), name="tables"),
    path("restaurant/tables/<uuid:pk>/", TableDetailView.as_view(), name="table-detail"),
]
