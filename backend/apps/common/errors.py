"""Shared domain exceptions."""

from collections.abc import Mapping
from typing import Any

from rest_framework.exceptions import APIException  # type: ignore[import-untyped]


class DomainError(APIException):
    status_code = 400

    def __init__(
        self,
        code: str,
        params: Mapping[str, Any] | None = None,
        status: int = 400,
    ):
        self.status_code = status
        super().__init__({"error_code": code, "params": dict(params or {})})
