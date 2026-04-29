"""Customer token-authenticated booking endpoints."""

import logging
from collections.abc import Mapping
from typing import Any, cast

from django.utils import timezone
from rest_framework.request import Request  # type: ignore[import-untyped]
from rest_framework.response import Response  # type: ignore[import-untyped]
from rest_framework.views import APIView  # type: ignore[import-untyped]

from apps.bookings.serializers import BookingPublicSerializer, CustomerBookingPatchSerializer
from apps.bookings.services import cancel_by_customer, modify_by_customer
from apps.common.codes import ErrorCode
from apps.common.errors import DomainError
from apps.customers.models import BookingAccessToken, hash_token, verify_token
from apps.customers.throttles import BookingTokenThrottle
from apps.restaurants.models import RestaurantSettings

logger = logging.getLogger("bookings")


class CustomerBookingView(APIView):
    """Public endpoint secured by booking access token."""

    authentication_classes: list = []
    permission_classes: list = []
    throttle_classes = [BookingTokenThrottle]
    patch_fields = frozenset({"starts_at", "party_size", "notes"})

    def _resolve(self, raw_token: str):
        hashed = hash_token(raw_token)
        try:
            token = BookingAccessToken.objects.select_related("booking").get(token_hash=hashed)
        except BookingAccessToken.DoesNotExist as exc:
            logger.warning("customer_booking_token_invalid")
            raise DomainError(ErrorCode.TOKEN_INVALID, status=404) from exc

        if not verify_token(raw_token, token.token_hash):
            logger.warning("customer_booking_token_invalid")
            raise DomainError(ErrorCode.TOKEN_INVALID, status=404)

        if token.revoked_at or token.expires_at < timezone.now():
            logger.warning("customer_booking_token_expired")
            raise DomainError(ErrorCode.TOKEN_EXPIRED, status=410)
        return token.booking

    def get(self, request: Request, raw_token: str) -> Response:
        booking = self._resolve(raw_token)
        return Response(BookingPublicSerializer(booking).data)

    def patch(self, request: Request, raw_token: str) -> Response:
        booking = self._resolve(raw_token)
        settings = RestaurantSettings.objects.get()
        payload = cast(Mapping[str, Any], request.data)
        self._validate_patch_fields(payload)
        serializer = CustomerBookingPatchSerializer(data=payload, partial=True)
        serializer.is_valid(raise_exception=True)
        booking = modify_by_customer(booking, serializer.validated_data, settings=settings)
        return Response(BookingPublicSerializer(booking).data)

    def delete(self, request: Request, raw_token: str) -> Response:
        booking = self._resolve(raw_token)
        settings = RestaurantSettings.objects.get()
        booking = cancel_by_customer(booking, settings=settings)
        return Response(BookingPublicSerializer(booking).data)

    def post(self, request: Request, raw_token: str) -> Response:
        booking = self._resolve(raw_token)
        settings = RestaurantSettings.objects.get()
        action = request.data.get("action")
        if action == "cancel":
            booking = cancel_by_customer(booking, settings=settings)
        elif action == "modify":
            booking = modify_by_customer(booking, request.data, settings=settings)
        else:
            raise DomainError(ErrorCode.VALIDATION_FAILED)
        return Response(BookingPublicSerializer(booking).data)

    def _validate_patch_fields(self, payload: Mapping[str, Any]) -> None:
        unsupported = set(payload) - self.patch_fields
        if unsupported:
            raise DomainError(
                ErrorCode.VALIDATION_FAILED,
                {"field": sorted(unsupported)[0]},
            )
