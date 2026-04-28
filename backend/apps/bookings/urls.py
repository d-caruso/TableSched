"""Bookings URL patterns."""

from django.urls import include, path
from django.urls.resolvers import URLPattern, URLResolver
from rest_framework.routers import DefaultRouter  # type: ignore[import-untyped]

from apps.bookings.views import BookingViewSet
from apps.bookings.views_customer import CustomerBookingView

app_name = "bookings"
router = DefaultRouter()
router.register("bookings", BookingViewSet, basename="bookings")

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include(router.urls)),
    path(
        "public/bookings/<str:raw_token>/",
        CustomerBookingView.as_view(),
        name="customer-booking",
    ),
]
