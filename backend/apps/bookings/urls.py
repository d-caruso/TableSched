"""Bookings URL patterns."""

from django.urls import include, path
from django.urls.resolvers import URLPattern, URLResolver
from rest_framework.routers import DefaultRouter  # type: ignore[import-untyped]

from apps.bookings.views import BookingViewSet
from apps.bookings.views import AdminDashboardView
from apps.bookings.views_customer import CustomerBookingView, PublicBookingCreateView, PublicSlotsView
from apps.bookings.views_walkins import WalkinViewSet

app_name = "bookings"
router = DefaultRouter()
router.register("bookings", BookingViewSet, basename="bookings")
router.register("walkins", WalkinViewSet, basename="walkins")

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include(router.urls)),
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("public/slots/", PublicSlotsView.as_view(), name="public-slots"),
    path("public/bookings/", PublicBookingCreateView.as_view(), name="public-booking-create"),
    path(
        "public/bookings/<str:raw_token>/",
        CustomerBookingView.as_view(),
        name="customer-booking",
    ),
]
