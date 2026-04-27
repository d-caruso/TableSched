"""Payment views."""

from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@csrf_exempt
@require_POST
def stripe_webhook(_: HttpRequest) -> HttpResponse:
    return HttpResponse(status=200)
