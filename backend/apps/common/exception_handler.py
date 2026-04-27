"""DRF exception handling for code-only API responses."""

from typing import Any

from rest_framework.views import exception_handler as drf_handler  # type: ignore[import-untyped]

from apps.common.codes import ErrorCode


def custom_exception_handler(exc: Exception, context: dict[str, Any]):
    response = drf_handler(exc, context)
    if response is None:
        return None

    data = response.data
    if isinstance(data, dict) and "error_code" in data and "params" in data:
        return response

    params = data if isinstance(data, dict) else {"detail": data}
    response.data = {"error_code": ErrorCode.VALIDATION_FAILED, "params": params}
    return response
