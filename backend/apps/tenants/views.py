"""Tenant public views."""

from django.http import HttpRequest, JsonResponse

from apps.tenants.models import Restaurant


def tenant_directory(request: HttpRequest) -> JsonResponse:
    tenants = (
        Restaurant.objects.filter(is_active=True)
        .exclude(schema_name="public")
        .values("name", "schema_name")
        .order_by("name")
    )
    data = [
        {
            "name": t["name"],
            "schema": t["schema_name"],
            "api_prefix": f"/restaurants/{t['schema_name']}/",
        }
        for t in tenants
    ]
    return JsonResponse(data, safe=False)
