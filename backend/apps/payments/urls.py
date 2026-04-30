"""Payments URL patterns."""

from django.urls import path
from django.urls.resolvers import URLPattern, URLResolver

from apps.payments.views import PaymentRefundView

app_name = "payments"
urlpatterns: list[URLPattern | URLResolver] = [
    path("payments/<uuid:pk>/refunds/", PaymentRefundView.as_view(), name="payment-refunds"),
]
