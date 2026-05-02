"""Development settings."""

import environ
import pathlib
environ.Env.read_env(pathlib.Path(__file__).resolve().parents[2] / ".env")

from . import base as base_settings

for setting_name in dir(base_settings):
    if setting_name.isupper():
        globals()[setting_name] = getattr(base_settings, setting_name)

DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8081",
    "http://127.0.0.1:8081",
]
