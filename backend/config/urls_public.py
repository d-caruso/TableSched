"""Public schema URL configuration."""

from django.http import HttpRequest, HttpResponse
from django.urls import path
from django.urls.resolvers import URLPattern, URLResolver

from apps.payments.views import stripe_webhook
from django.contrib import admin


def healthz(_: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")


urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    path("stripe/webhook/", stripe_webhook, name="stripe-webhook"),
    path("healthz/", healthz, name="healthz"),
]
