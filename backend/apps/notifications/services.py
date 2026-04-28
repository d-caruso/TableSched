"""Notification routing and synchronous sending for booking workflows."""

from __future__ import annotations

import logging
from typing import cast

from django.conf import settings
from django.core.mail import send_mail
from twilio.base.exceptions import TwilioRestException  # type: ignore[import-untyped]

from apps.notifications.i18n import render
from apps.notifications.models import NotificationLog

logger = logging.getLogger("notifications")

def notify_customer(booking, code: str, *, raw_token: str | None = None) -> None:
    """Route a customer notification to the appropriate channels."""

    customer = booking.customer
    ctx = _build_ctx(booking, raw_token)
    _send_sms(booking, code, customer.locale, customer.phone, ctx)

    if customer.email:
        _send_email(booking, code, customer.locale, customer.email, ctx)


def notify_staff(booking, code: str, **kwargs) -> None:
    """Best-effort staff notification placeholder."""

    _ = (booking, code, kwargs)


def _build_ctx(booking, raw_token: str | None) -> dict[str, object]:
    """Build the shared template context."""

    return {
        "restaurant": getattr(settings, "PUBLIC_BOOKING_RESTAURANT_NAME", ""),
        "when": booking.starts_at.strftime("%a %d %b %H:%M"),
        "party": booking.party_size,
        "url": f"{settings.PUBLIC_BOOKING_BASE_URL}/{raw_token}" if raw_token else "",
        "booking_id": str(booking.id),
    }


def _send_sms(booking, code: str, locale: str, phone: str, ctx: dict[str, object]) -> None:
    """Send an SMS and record the attempt."""

    effective_ctx = _build_ctx(booking, None)
    effective_ctx.update(ctx)
    text = render(code, locale, "sms", effective_ctx)
    log = NotificationLog.objects.create(
        booking=booking,
        template_code=code,
        locale=locale,
        channel=NotificationLog.CHANNEL_SMS,
        recipient=phone,
        status="queued",
    )

    try:
        from apps.notifications.twilio_client import client as twilio_client

        message = twilio_client.messages.create(
            to=phone,
            from_=getattr(settings, "TWILIO_FROM", ""),
            body=text,
        )
        log.status = "sent"
        log.provider_message_id = getattr(message, "sid", "")
    except TwilioRestException as exc:
        log.status = "failed"
        log.error_code = str(exc.code) if exc.code is not None else exc.__class__.__name__
        logger.exception("sms_failed", extra={"booking_id": str(booking.id)})
    except Exception as exc:  # pragma: no cover - defensive boundary.
        log.status = "failed"
        log.error_code = exc.__class__.__name__
        logger.exception("sms_failed", extra={"booking_id": str(booking.id)})

    log.save(update_fields=["status", "provider_message_id", "error_code", "updated_at"])


def _send_email(
    booking,
    code: str,
    locale: str,
    email: str,
    ctx: dict[str, object],
) -> None:
    """Send an email and record the attempt."""

    effective_ctx = _build_ctx(booking, None)
    effective_ctx.update(ctx)
    subject, body = cast(
        tuple[str, str],
        render(code, locale, "email", effective_ctx),
    )
    log = NotificationLog.objects.create(
        booking=booking,
        template_code=code,
        locale=locale,
        channel=NotificationLog.CHANNEL_EMAIL,
        recipient=email,
        status="queued",
    )

    try:
        send_mail(
            subject,
            body,
            getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"),
            [email],
            fail_silently=False,
        )
        log.status = "sent"
    except Exception as exc:  # pragma: no cover - defensive boundary.
        log.status = "failed"
        log.error_code = exc.__class__.__name__
        logger.exception("email_failed", extra={"booking_id": str(booking.id)})

    log.save(update_fields=["status", "provider_message_id", "error_code", "updated_at"])
