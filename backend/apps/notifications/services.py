"""Notification service stubs for booking workflows."""


def notify_customer(booking, code: str, **kwargs) -> None:
    """Best-effort customer notification placeholder."""

    _ = (booking, code, kwargs)


def notify_staff(booking, code: str, **kwargs) -> None:
    """Best-effort staff notification placeholder."""

    _ = (booking, code, kwargs)
