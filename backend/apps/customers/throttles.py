"""Throttles for customer-facing token endpoints."""

from __future__ import annotations

from rest_framework.throttling import SimpleRateThrottle  # type: ignore[import-untyped]


class BookingTokenThrottle(SimpleRateThrottle):
    """Limit public booking token probes per client IP."""

    scope = "booking_token"
    rate = "30/min"

    def get_cache_key(self, request, view):  # noqa: D401, ANN001
        ident = self.get_ident(request)
        schema = getattr(getattr(request, "tenant", None), "schema_name", "public")
        return self.cache_format % {
            "scope": self.scope,
            "ident": f"{schema}:{ident}",
        }
