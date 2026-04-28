"""Production settings."""

from . import base as base_settings

for setting_name in dir(base_settings):
    if setting_name.isupper():
        globals()[setting_name] = getattr(base_settings, setting_name)

DEBUG = False
ALLOWED_HOSTS = base_settings.env.list("ALLOWED_HOSTS")
PUBLIC_DOMAIN = base_settings.env("PUBLIC_DOMAIN", default="")
