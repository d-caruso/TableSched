"""Payment views."""

from django.conf import settings as django_settings
from django.http import HttpRequest, HttpResponse
from django_tenants.utils import schema_context  # type: ignore[import-untyped]
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from apps.payments import handlers


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
