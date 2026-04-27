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
    path("auth/", include("allauth.urls")),
    path("stripe/webhook/", stripe_webhook, name="stripe-webhook"),
    path("healthz/", healthz, name="healthz"),
]
