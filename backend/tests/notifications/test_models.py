import pytest

from tests.tenant_helpers import tenant_schema


@pytest.mark.django_db
def test_notification_log_channels():
    with tenant_schema("notifications") as _:
        from apps.notifications.models import NotificationLog

        valid = {choice[0] for choice in NotificationLog.CHANNEL_CHOICES}

        assert valid == {"sms", "email"}
