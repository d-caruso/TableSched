"""Payment views."""

from django.shortcuts import get_object_or_404
from django.conf import settings as django_settings
from django.http import HttpRequest, HttpResponse
from django_tenants.utils import schema_context  # type: ignore[import-untyped]
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework.request import Request  # type: ignore[import-untyped]
from rest_framework.response import Response  # type: ignore[import-untyped]
from rest_framework.views import APIView  # type: ignore[import-untyped]

from apps.payments import handlers
from apps.common.permissions import IsManager
from apps.payments.models import Payment
from apps.payments import services


@csrf_exempt
@require_POST
def stripe_webhook(request: HttpRequest) -> HttpResponse:
    payload = request.body
    signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            getattr(django_settings, "STRIPE_WEBHOOK_SECRET", ""),
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    obj = event["data"]["object"]
    tenant_schema = (obj.get("metadata") or {}).get("tenant_schema")
    if not tenant_schema:
        return HttpResponse(status=400)

    with schema_context(tenant_schema):
        handlers.dispatch(event)

    return HttpResponse(status=200)


class PaymentRefundView(APIView):
    """Manager-only manual refund endpoint."""

    permission_classes = [IsManager]

    def post(self, request: Request, pk: str) -> Response:
        payment = get_object_or_404(Payment, pk=pk)
        services.refund(payment)
        payment.refresh_from_db()
        return Response({"id": str(payment.id), "status": payment.status})
