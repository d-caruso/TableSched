"""Audit service stubs for MVP domain flows."""


def record(*, actor, action: str, target, payload: dict) -> None:
    """Record an audit event placeholder."""

    _ = (actor, action, target, payload)
