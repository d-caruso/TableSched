"""Localized notification template rendering."""

from importlib import import_module

SUPPORTED_LOCALES = {"en", "it", "de"}
DEFAULT_LOCALE = "en"


def render(code: str, locale: str, channel: str, ctx: dict) -> str | tuple[str, str]:
    """Render a localized notification template."""

    selected_locale = locale if locale in SUPPORTED_LOCALES else DEFAULT_LOCALE
    templates = import_module(f"apps.notifications.templates.{selected_locale}").TEMPLATES
    template = templates[code]

    if channel == "sms":
        return template["sms"].format(**ctx)

    return template["email_subject"].format(**ctx), template["email_body"].format(**ctx)
