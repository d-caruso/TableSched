"""Base Django settings."""

from pathlib import Path

import environ  # type: ignore[import-untyped]  # django-environ ships without type hints.

BASE_DIR = Path(__file__).resolve().parents[2]

env = environ.Env(DEBUG=(bool, False))

SECRET_KEY = env("SECRET_KEY", default="dev-secret-key")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": env("DB_NAME", default="tablesched"),
        "USER": env("DB_USER", default="postgres"),
        "PASSWORD": env("DB_PASSWORD", default="postgres"),
        "HOST": env("DB_HOST", default="127.0.0.1"),
        "PORT": env("DB_PORT", default="5432"),
    }
}
DATABASE_ROUTERS = ("django_tenants.routers.TenantSyncRouter",)

SHARED_APPS = (
    "apps.tenants",
    "django_tenants",
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.accounts",
    "allauth",
    "allauth.account",
    "allauth.headless",
)
TENANT_APPS = (
    "apps.memberships",
    "apps.customers",
    "apps.restaurants",
    "apps.bookings",
    "apps.payments",
    "apps.notifications",
    "apps.audit",
)
INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

TENANT_MODEL = "tenants.Restaurant"
TENANT_DOMAIN_MODEL = "tenants.Domain"
TENANT_SUBFOLDER_PREFIX = "restaurants"

MIDDLEWARE = [
    "django_tenants.middleware.TenantSubfolderMiddleware",
    "apps.common.middleware.CsrfExemptAllauthAppMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "apps.memberships.middleware.MembershipMiddleware",
]

ROOT_URLCONF = "config.urls"
PUBLIC_SCHEMA_URLCONF = "config.urls_public"
SHOW_PUBLIC_IF_NO_TENANT_FOUND = env.bool("SHOW_PUBLIC_IF_NO_TENANT_FOUND", default=True)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)
SITE_ID = 1
AUTH_USER_MODEL = "accounts.User"
HEADLESS_ONLY = True
HEADLESS_TOKEN_STRATEGY = "allauth.headless.tokens.strategies.jwt.JWTTokenStrategy"
HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": "/auth/verify-email/{key}",
    "account_reset_password": "/auth/reset-password",
    "account_reset_password_from_key": "/auth/reset-password/{key}",
    "account_signup": "/auth/signup",
}
HEADLESS_JWT_SECRET_KEY = env("SECRET_KEY", default="dev-secret-key")
HEADLESS_JWT_ALGORITHM = "HS256"
HEADLESS_JWT_ACCESS_TOKEN_EXPIRATION = 60 * 15  # 15 minutes
HEADLESS_JWT_REFRESH_TOKEN_EXPIRATION = 60 * 60 * 24 * 7  # 7 days
HEADLESS_JWT_ROTATE_REFRESH_TOKEN = True
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_ADAPTER = "apps.accounts.adapters.AccountAdapter"
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "30/min"},
    "EXCEPTION_HANDLER": "apps.common.exception_handler.custom_exception_handler",
}
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")
TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN", default="")
TWILIO_FROM = env("TWILIO_FROM", default="")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "sensitive_data": {
            "()": "apps.common.log_filters.SensitiveDataFilter",
        }
    },
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.json.JsonFormatter",
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "filters": ["sensitive_data"],
            "formatter": "json",
        }
    },
    "loggers": {
        "bookings": {
            "handlers": ["stdout"],
            "level": "INFO",
            "propagate": False,
        },
        "payments.webhook": {
            "handlers": ["stdout"],
            "level": "INFO",
            "propagate": False,
        },
        "notifications": {
            "handlers": ["stdout"],
            "level": "INFO",
            "propagate": False,
        },
        "audit": {
            "handlers": ["stdout"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
