import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
django.setup()

from django.urls import get_resolver

def show(resolver, prefix=""):
    for pattern in resolver.url_patterns:
        if hasattr(pattern, "url_patterns"):
            show(pattern, prefix + str(pattern.pattern))
        else:
            print(prefix + str(pattern.pattern))

show(get_resolver())
