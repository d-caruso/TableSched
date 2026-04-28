"""Logging filters for sensitive data redaction."""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping
from typing import Any

from django.conf import settings

REDACTED = "[REDACTED]"
SENSITIVE_KEYS = ("password", "token", "secret", "auth", "sid", "key")
SENSITIVE_SETTINGS = (
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_FROM",
    "EMAIL_HOST_PASSWORD",
)
_SENSITIVE_ASSIGNMENT_RE = re.compile(
    r"(?i)([A-Za-z0-9_]*?(?:password|token|secret|auth|sid|key)[A-Za-z0-9_]*)"
    r"(\s*[:=]\s*)([^\s,;]+)"
)


def _configured_secret_values() -> list[str]:
    values: list[str] = []
    for name in SENSITIVE_SETTINGS:
        value = getattr(settings, name, "")
        if value:
            values.append(str(value))
    return values


def _is_sensitive_key(key: Any) -> bool:
    key_text = str(key).lower()
    return any(token in key_text for token in SENSITIVE_KEYS)


def _redact_text(value: str) -> str:
    redacted = value
    for secret_value in _configured_secret_values():
        redacted = redacted.replace(secret_value, REDACTED)
    return _SENSITIVE_ASSIGNMENT_RE.sub(r"\1\2[REDACTED]", redacted)


def _redact_value(value: Any) -> Any:
    if isinstance(value, str):
        return _redact_text(value)
    if isinstance(value, Mapping):
        return {
            key: REDACTED if _is_sensitive_key(key) else _redact_value(item)
            for key, item in value.items()
        }
    if isinstance(value, tuple):
        return tuple(_redact_value(item) for item in value)
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, set):
        return {_redact_value(item) for item in value}
    return value


class SensitiveDataFilter(logging.Filter):
    """Redact obvious credential values from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = _redact_value(record.msg)
        if record.args:
            record.args = _redact_value(record.args)
        return True
