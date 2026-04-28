"""Audit write helper for explicit service-layer events."""

from apps.audit.models import AuditLog


def record(*, actor, action: str, target, payload: dict | None = None) -> AuditLog:
    """Persist an explicit audit event."""

    return AuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=target.__class__.__name__,
        target_id=target.id,
        payload=payload or {},
    )
