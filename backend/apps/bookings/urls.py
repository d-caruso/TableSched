"""Bookings URL patterns."""

from django.urls import path
from django.urls.resolvers import URLPattern, URLResolver

from apps.bookings.views_customer import CustomerBookingView

app_name = "bookings"
urlpatterns: list[URLPattern | URLResolver] = [
    path(
        "public/bookings/<str:raw_token>/",
        CustomerBookingView.as_view(),
        name="customer-booking",
    ),
]
