import pytest

from apps.notifications.templates import de, en, it


def test_render_sms_english():
    from apps.notifications.i18n import render

    text = render(
        "booking_approved",
        "en",
        "sms",
        {"restaurant": "Ristorante X", "when": "Mon 20:00", "party": 2, "url": ""},
    )

    assert isinstance(text, str)
    assert "confirmed" in text


def test_render_falls_back_to_english_for_unknown_locale():
    from apps.notifications.i18n import render

    text = render(
        "booking_approved",
        "zh",
        "sms",
        {"restaurant": "R", "when": "Mon", "party": 1, "url": ""},
    )

    assert isinstance(text, str)


def test_render_email_returns_subject_and_body():
    from apps.notifications.i18n import render

    subject, body = render(
        "booking_approved",
        "it",
        "email",
        {"restaurant": "R", "when": "Mon", "party": 2, "url": ""},
    )

    assert isinstance(subject, str)
    assert isinstance(body, str)


@pytest.mark.parametrize(
    "locale, expected",
    [
        ("en", "received"),
        ("it", "ricevuta"),
        ("de", "empfangen"),
    ],
)
def test_render_booking_request_received_across_locales(locale, expected):
    from apps.notifications.i18n import render

    text = render(
        "booking_request_received",
        locale,
        "sms",
        {"restaurant": "Ristorante X", "when": "Mon 20:00", "party": 2, "url": "/token"},
    )

    assert isinstance(text, str)
    assert expected in text


def test_all_codes_present_in_all_locales():
    for code in en.TEMPLATES:
        assert code in it.TEMPLATES, f"Missing in it: {code}"
        assert code in de.TEMPLATES, f"Missing in de: {code}"
