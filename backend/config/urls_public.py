"""Public schema URL configuration."""

from django.http import HttpRequest, HttpResponse
from django.urls import include, path
from django.urls.resolvers import URLPattern, URLResolver

from django.contrib import admin
from apps.payments.views import stripe_webhook


def healthz(_: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")


urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path("_allauth/", include("allauth.headless.urls")),
    path("api/v1/", include("apps.bookings.urls")),
    path("api/v1/", include("apps.restaurants.urls")),
    path("stripe/webhook/", stripe_webhook, name="stripe-webhook"),
    path("healthz/", healthz, name="healthz"),
    path("", include("apps.tenants.urls")),
]
